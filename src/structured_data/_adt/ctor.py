"""Internal implementation of helper types for Sum annotations."""

from __future__ import annotations

import ast
import types
import typing
import weakref

import astor  # type: ignore

_CTOR_CACHE: typing.Dict[typing.Tuple, "Ctor"] = {}


AnyCtor = typing.Union["Ctor", typing.Type["Ctor"]]

ARGS: typing.MutableMapping[AnyCtor, typing.Tuple] = weakref.WeakKeyDictionary()


class Ctor:
    """Marker class for adt constructors.

    To use, index with a sequence of types, and annotate a variable in an
    adt-decorated class with it.
    """

    __slots__ = ("__weakref__",)

    def __new__(cls, args: typing.Tuple[typing.Any, ...]) -> Ctor:
        if args == ():
            raise ValueError
        self = object.__new__(cls)
        ARGS[self] = args
        return _CTOR_CACHE.setdefault(args, self)

    def __init_subclass__(cls, **kwargs: typing.Any) -> None:
        raise TypeError

    def __class_getitem__(cls, args: typing.Any) -> AnyCtor:
        if not isinstance(args, tuple):
            args = (args,)
        if not args:
            return cls
        # Yes it is.
        return cls(args)  # pylint: disable=not-callable


ARGS[Ctor] = ()


def _interpret_args_from_non_string(
    constructor: typing.Any,
) -> typing.Optional[typing.Tuple]:
    try:
        return ARGS.get(constructor)
    except TypeError:
        return None


def _interpret_classvar_from_non_string(annotation: typing.Any) -> bool:
    if annotation is typing.ClassVar:
        return True
    try:
        return annotation.__origin__ is typing.ClassVar
    except AttributeError:
        return False


def _parse_constructor(constructor: str) -> ast.Expression:
    try:
        return typing.cast(ast.Expression, ast.parse(constructor, mode="eval"))
    except Exception:
        raise ValueError("parsing annotation failed")


def _get_args_from_index(index: ast.AST) -> typing.Tuple:
    if isinstance(index, ast.Tuple):
        return tuple(astor.to_source(elt) for elt in index.elts)
    return (astor.to_source(index),)


def _checked_eval(
    source: typing.Union[str, types.CodeType], global_ns: typing.Dict[str, typing.Any]
) -> typing.Any:
    try:
        # Oh no, the user might end up executing arbitrary code that they wrote
        # in the first place.
        return eval(source, global_ns)  # pylint: disable=eval-used
    # If we hit this, anything could have gone wrong, but just assume it's not
    # anything we care about.
    except Exception:  # pylint: disable=broad-except
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


def _str_is_classvar(annotation: str, global_ns: typing.Dict[str, typing.Any]) -> bool:
    annotation_ast = _parse_constructor(annotation)
    value = NO_VALUE
    if isinstance(annotation_ast.body, ast.Subscript) and isinstance(
        annotation_ast.body.slice, ast.Index
    ):
        annotation_ast.body = annotation_ast.body.value
        value = _checked_eval(
            compile(annotation_ast, "<annotation>", "eval"), global_ns
        )
    if value is typing.ClassVar:
        return True
    if value is None:
        return False
    return _interpret_classvar_from_non_string(_checked_eval(annotation, global_ns))


def get_args(
    constructor: typing.Any, global_ns: typing.Dict[str, typing.Any]
) -> typing.Optional[typing.Tuple]:
    """Given annotation value and module namespace, return Ctor args, if any.

    The function first checks if the value is a string. If so, it tries to
    parse it.
    Otherwise, if the value is a Ctor instance, it extracts the annotation, and
    if not, it returns ``None``.
    """
    if isinstance(constructor, str):
        try:
            return _extract_tuple_ast(constructor, global_ns)
        except ValueError:
            return None
    return _interpret_args_from_non_string(constructor)


def annotation_is_classvar(
    annotation: typing.Any, global_ns: typing.Dict[str, typing.Any]
) -> bool:
    """Given annotation value and module namespace, return whether it's a ClassVar.

    The function first checks if the value is a string. If so, it tries to
    parse it.
    Otherwise, if the value is a ClassVar instance, it returns ``True``.
    If not, it returns ``False``.
    """
    if isinstance(annotation, str):
        try:
            return _str_is_classvar(annotation, global_ns)
        except ValueError:
            return False
    return _interpret_classvar_from_non_string(annotation)
