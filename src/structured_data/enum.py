"""Class decorator for defining abstract data types."""

import ast
import sys
import typing
import weakref

import astor

from ._enum_constructor import make_constructor
from ._prewritten_methods import SUBCLASS_ORDER
from ._prewritten_methods import PrewrittenMethods

_CTOR_CACHE = {}


ARGS = weakref.WeakKeyDictionary()


class Ctor:
    """Marker class for enum constructors.

    To use, index with a sequence of types, and annotate a variable in an
    enum-decorated class with it.
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
        return ast.parse(constructor, mode='eval')
    except Exception:
        raise ValueError('parsing annotation failed')


def _get_args_from_index(index):
    if isinstance(index, ast.Tuple):
        return tuple(astor.to_source(elt) for elt in index.elts)
    return (astor.to_source(index),)


def _checked_eval(source, global_ns):
    try:
        return eval(source, global_ns)
    except Exception:
        return None


def _extract_tuple_ast(constructor, global_ns):
    ctor_ast = _parse_constructor(constructor)
    if (
            isinstance(ctor_ast.body, ast.Subscript)
            and isinstance(ctor_ast.body.slice, ast.Index)):
        index = ctor_ast.body.slice.value
        ctor_ast.body = ctor_ast.body.value
        value = _checked_eval(compile(ctor_ast, '<annotation>', 'eval'), global_ns)
        if value is Ctor:
            return _get_args_from_index(index)
        if value is None:
            return None
    return _interpret_args_from_non_string(_checked_eval(constructor, global_ns))


def _args(constructor, global_ns):
    if isinstance(constructor, str):
        try:
            return _extract_tuple_ast(constructor, global_ns)
        except ValueError:
            return None
    return _interpret_args_from_non_string(constructor)


def _name(cls, function) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


def _set_new_functions(cls, *functions) -> typing.Optional[str]:
    """Attempt to set the attributes corresponding to the functions on cls.

    If any attributes are already defined, fail *before* setting any, and
    return the already-defined name.
    """
    for function in functions:
        if _name(cls, function) in cls.__dict__:
            return _name(cls, function)
    for function in functions:
        setattr(cls, _name(cls, function), function)
    return None


def _enum_super(_cls):
    def base(cls, args):
        return super(_cls, cls).__new__(cls, args)
    return base


def _make_nested_new(_cls, subclasses, base__new__):
    @staticmethod
    def __new__(cls, args):
        if cls not in subclasses:
            raise TypeError
        return base__new__(cls, args)
    return __new__


def _nillable_write(dct, key, value):
    if value is None:
        dct.pop(key, None)
    else:
        dct[key] = value


def _add_repr(cls, set_repr):
    if set_repr:
        _set_new_functions(cls, PrewrittenMethods.__repr__)


def _add_eq(cls, set_eq):
    equality_methods_were_set = False
    if set_eq:
        equality_methods_were_set = not _set_new_functions(
            cls, PrewrittenMethods.__eq__, PrewrittenMethods.__ne__)
    return equality_methods_were_set


def _set_hash(cls, set_hash):
    if set_hash:
        cls.__hash__ = PrewrittenMethods.__hash__


def _add_order(cls, set_order, equality_methods_were_set):
    if set_order:
        if not equality_methods_were_set:
            raise ValueError(
                "Can't add ordering methods if equality methods are provided.")
        collision = _set_new_functions(
            cls,
            PrewrittenMethods.__lt__,
            PrewrittenMethods.__le__,
            PrewrittenMethods.__gt__,
            PrewrittenMethods.__ge__
            )
        if collision:
            raise TypeError(
                'Cannot overwrite attribute {collision} in class '
                '{name}. Consider using functools.total_ordering'.format(
                    collision=collision, name=cls.__name__))


def _custom_new(cls, subclasses):
    basic_new = _make_nested_new(cls, subclasses, _enum_super(cls))
    if _set_new_functions(cls, basic_new):
        augmented_new = _make_nested_new(cls, subclasses, cls.__new__)
        cls.__new__ = augmented_new


def _process_class(_cls, _repr, eq, order):
    if order and not eq:
        raise ValueError('eq must be true if order is true')

    args = {}
    subclasses = set()
    subclass_order = []
    for cls in reversed(_cls.__mro__):
        for key, value in getattr(cls, '__annotations__', {}).items():
            _nillable_write(
                args, key, _args(value, vars(sys.modules[cls.__module__])))

    for name, args_ in args.items():
        make_constructor(_cls, name, args_, subclasses, subclass_order)

    SUBCLASS_ORDER[_cls] = tuple(subclass_order)

    _cls.__init_subclass__ = PrewrittenMethods.__init_subclass__

    _custom_new(_cls, subclasses)

    _set_new_functions(
        _cls, PrewrittenMethods.__setattr__, PrewrittenMethods.__delattr__)
    _set_new_functions(_cls, PrewrittenMethods.__bool__)

    _add_repr(_cls, _repr)

    equality_methods_were_set = _add_eq(_cls, eq)

    _set_hash(_cls, equality_methods_were_set)

    _add_order(_cls, order, equality_methods_were_set)

    return _cls


def enum(_cls=None, *, repr=True, eq=True, order=False):
    """Decorate a class to be an algebraic data type."""

    def wrap(cls):
        """Return the processed class."""
        return _process_class(cls, repr, eq, order)

    if _cls is None:
        return wrap

    return wrap(_cls)


__all__ = ['Ctor', 'enum']
