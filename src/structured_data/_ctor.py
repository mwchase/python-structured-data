import ast
import weakref

import astor

_CTOR_CACHE = {}


ARGS = weakref.WeakKeyDictionary()


class Ctor:
    """Marker class for adt constructors.

    To use, index with a sequence of types, and annotate a variable in an
    adt-decorated class with it.
    """

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


def _interpret_args_from_non_string(constructor):
    try:
        return ARGS.get(constructor)
    except TypeError:
        return None


def _parse_constructor(constructor):
    try:
        return ast.parse(constructor, mode="eval")
    except Exception:
        raise ValueError("parsing annotation failed")


def _get_args_from_index(index):
    if isinstance(index, ast.Tuple):
        return tuple(astor.to_source(elt) for elt in index.elts)
    return (astor.to_source(index),)


def _checked_eval(source, global_ns):
    try:
        return eval(source, global_ns)
    except Exception:
        return None


NO_VALUE = object()


def _extract_tuple_ast(constructor, global_ns):
    ctor_ast = _parse_constructor(constructor)
    value = index = NO_VALUE
    if isinstance(ctor_ast.body, ast.Subscript) and isinstance(
        ctor_ast.body.slice, ast.Index
    ):
        index = ctor_ast.body.slice.value
        ctor_ast.body = ctor_ast.body.value
        value = _checked_eval(compile(ctor_ast, "<annotation>", "eval"), global_ns)
    if value is Ctor:
        return _get_args_from_index(index)
    if value is None:
        return None
    return _interpret_args_from_non_string(_checked_eval(constructor, global_ns))


def get_args(constructor, global_ns):
    if isinstance(constructor, str):
        try:
            return _extract_tuple_ast(constructor, global_ns)
        except ValueError:
            return None
    return _interpret_args_from_non_string(constructor)
