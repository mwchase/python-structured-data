import ast
import typing
import weakref

import astor  # type: ignore

_CTOR_CACHE: typing.Dict[typing.Tuple, "Ctor"] = {}


ARGS: typing.MutableMapping[
    typing.Union["Ctor", typing.Type["Ctor"]], typing.Tuple
] = weakref.WeakKeyDictionary()


class Ctor:
    """Marker class for adt constructors.

    To use, index with a sequence of types, and annotate a variable in an
    adt-decorated class with it.
    """

    __slots__ = ("__weakref__",)

    def __new__(cls, args):
        if args == ():
            return cls
        self = object.__new__(cls)
        ARGS[self] = args
        return _CTOR_CACHE.setdefault(args, self)

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def __class_getitem__(cls, args):
        if not isinstance(args, tuple):
            args = (args,)
        return cls(args)


ARGS[Ctor] = ()


def _interpret_args_from_non_string(
    constructor: typing.Any
) -> typing.Optional[typing.Tuple]:
    try:
        return ARGS.get(constructor)
    except TypeError:
        return None


def _parse_constructor(constructor: str) -> ast.Module:
    try:
        return ast.parse(constructor, mode="eval")
    except Exception:
        raise ValueError("parsing annotation failed")


def _get_args_from_index(index: ast.AST) -> typing.Tuple:
    if isinstance(index, ast.Tuple):
        return tuple(astor.to_source(elt) for elt in index.elts)
    return (astor.to_source(index),)


def _checked_eval(source, global_ns: typing.Dict[str, typing.Any]) -> typing.Any:
    try:
        return eval(source, global_ns)
    except Exception:
        return None


NO_VALUE = object()


def _extract_tuple_ast(
    constructor: str, global_ns: typing.Dict[str, typing.Any]
) -> typing.Optional[typing.Tuple]:
    ctor_ast = _parse_constructor(constructor)
    value = index = NO_VALUE
    if isinstance(ctor_ast.body, ast.Subscript) and isinstance(
        ctor_ast.body.slice, ast.Index
    ):
        index = ctor_ast.body.slice.value
        ctor_ast.body = ctor_ast.body.value
        value = _checked_eval(compile(ctor_ast, "<annotation>", "eval"), global_ns)
    if value is Ctor:
        # If value is Ctor, then value was set, which is only possible if the
        # previous block executed, which will set "index" to an AST.
        return _get_args_from_index(typing.cast(ast.AST, index))
    if value is None:
        return None
    return _interpret_args_from_non_string(_checked_eval(constructor, global_ns))


def get_args(
    constructor, global_ns: typing.Dict[str, typing.Any]
) -> typing.Optional[typing.Tuple]:
    if isinstance(constructor, str):
        try:
            return _extract_tuple_ast(constructor, global_ns)
        except ValueError:
            return None
    return _interpret_args_from_non_string(constructor)
