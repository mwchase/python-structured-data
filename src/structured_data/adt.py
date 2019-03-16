"""Class decorator for defining abstract data types."""

import sys
import typing

from ._adt_constructor import make_constructor
from ._ctor import Ctor
from ._ctor import get_args
from ._prewritten_methods import SUBCLASS_ORDER
from ._prewritten_methods import PrewrittenMethods

_T = typing.TypeVar("_T")
_K = typing.TypeVar("_K")
_V = typing.TypeVar("_V")


def _name(cls: typing.Type[_T], function) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


def _set_new_functions(cls: typing.Type[_T], *functions) -> typing.Optional[str]:
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


def _adt_super(_cls: typing.Type[_T]):
    def base(cls, args):
        return super(_cls, cls).__new__(cls, args)

    return base


def _make_nested_new(_cls: typing.Type[_T], subclasses, base__new__):
    def __new__(cls, args):
        if cls not in subclasses:
            raise TypeError
        return base__new__(cls, args)

    return staticmethod(__new__)


def _nillable_write(dct: typing.Dict[_K, _V], key: _K, value: typing.Optional[_V]):
    if value is None:
        dct.pop(key, typing.cast(_V, None))
    else:
        dct[key] = value


def _add_methods(cls: typing.Type[_T], do_set, *methods):
    methods_were_set = False
    if do_set:
        methods_were_set = not _set_new_functions(cls, *methods)
    return methods_were_set


def _set_hash(cls: typing.Type[_T], set_hash):
    if set_hash:
        cls.__hash__ = PrewrittenMethods.__hash__


def _add_order(cls: typing.Type[_T], set_order, equality_methods_were_set):
    if set_order:
        if not equality_methods_were_set:
            raise ValueError(
                "Can't add ordering methods if equality methods are provided."
            )
        collision = _set_new_functions(
            cls,
            PrewrittenMethods.__lt__,
            PrewrittenMethods.__le__,
            PrewrittenMethods.__gt__,
            PrewrittenMethods.__ge__,
        )
        if collision:
            raise TypeError(
                "Cannot overwrite attribute {collision} in class "
                "{name}. Consider using functools.total_ordering".format(
                    collision=collision, name=cls.__name__
                )
            )


def _custom_new(cls: typing.Type[_T], subclasses):
    basic_new = _make_nested_new(cls, subclasses, _adt_super(cls))
    if _set_new_functions(cls, basic_new):
        augmented_new = _make_nested_new(cls, subclasses, cls.__new__)
        cls.__new__ = augmented_new


def _args_from_annotations(cls: typing.Type[_T]):
    args: typing.Dict[str, typing.Tuple] = {}
    for superclass in reversed(cls.__mro__):
        for key, value in getattr(superclass, "__annotations__", {}).items():
            _nillable_write(
                args, key, get_args(value, vars(sys.modules[superclass.__module__]))
            )
    return args


def _process_class(_cls: typing.Type[_T], _repr, eq, order) -> typing.Type[_T]:
    if order and not eq:
        raise ValueError("eq must be true if order is true")

    subclass_order: typing.List[typing.Type[_T]] = []

    for name, args in _args_from_annotations(_cls).items():
        make_constructor(_cls, name, args, subclass_order)

    SUBCLASS_ORDER[_cls] = tuple(subclass_order)

    _cls.__init_subclass__ = PrewrittenMethods.__init_subclass__

    _custom_new(_cls, frozenset(subclass_order))

    _set_new_functions(
        _cls, PrewrittenMethods.__setattr__, PrewrittenMethods.__delattr__
    )
    _set_new_functions(_cls, PrewrittenMethods.__bool__)

    _add_methods(_cls, _repr, PrewrittenMethods.__repr__)

    equality_methods_were_set = _add_methods(
        _cls, eq, PrewrittenMethods.__eq__, PrewrittenMethods.__ne__
    )

    _set_hash(_cls, equality_methods_were_set)

    _add_order(_cls, order, equality_methods_were_set)

    return _cls


@typing.overload
def adt(_cls: typing.Type[_T]) -> typing.Type[_T]:
    """Return a decorated class."""


@typing.overload
def adt(*, repr: bool, eq: bool, order: bool) -> typing.Callable[[typing.Type[_T]], typing.Type[_T]]:
    """Return a class decorator."""


def adt(_cls=None, *, repr=True, eq=True, order=False):
    """Decorate a class to be an algebraic data type."""

    def wrap(cls: typing.Type[_T]) -> typing.Type[_T]:
        """Return the processed class."""
        return _process_class(cls, repr, eq, order)

    if _cls is None:
        return wrap

    return wrap(_cls)


__all__ = ["Ctor", "adt"]
