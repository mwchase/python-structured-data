import inspect
import typing

from .. import _cant_modify
from . import constructor
from . import ordering
from . import prewritten_methods
from . import product_type

_T = typing.TypeVar("_T")


def _conditional_call(call: bool, func: typing.Callable, *args: typing.Any) -> None:
    if call:
        func(*args)


def _set_new_functions(cls: type, *functions: typing.Callable) -> typing.Optional[str]:
    """Attempt to set the attributes corresponding to the functions on cls.

    If any attributes are already defined, fail *before* setting any, and
    return the already-defined name.
    """
    cant_set = product_type._cant_set_new_functions(cls, *functions)
    if cant_set:
        return cant_set
    for function in functions:
        setattr(cls, product_type._name(cls, function), function)
    return None


def _sum_new(_cls: typing.Type[_T], subclasses: typing.FrozenSet[type]) -> None:
    def base(cls: typing.Type[_T], args: tuple) -> _T:
        # By the way, this is for https://github.com/python/mypy/issues/7580
        # When that's fixed, this can be made a one-liner again.
        superclass = super(_cls, cls)
        return superclass.__new__(cls, args)  # type: ignore

    new = vars(_cls).get("__new__", staticmethod(base))

    def __new__(cls: typing.Type[_T], args: tuple) -> _T:
        if cls not in subclasses:
            raise TypeError
        return new.__get__(None, cls)(cls, args)

    _cls.__new__ = staticmethod(__new__)  # type: ignore


class Sum:
    """Base class of classes with disjoint constructors.

    Examines PEP 526 __annotations__ to determine subclasses.

    If repr is true, a __repr__() method is added to the class.
    If order is true, rich comparison dunder methods are added.

    The Sum class examines the class to find Ctor annotations.
    A Ctor annotation is the adt.Ctor class itself, or the result of indexing
    the class, either with a single type hint, or a tuple of type hints.
    All other annotations are ignored.

    The subclass is not subclassable, but has subclasses at each of the
    names that had Ctor annotations. Each subclass takes a fixed number of
    arguments, corresponding to the type hints given to its annotation, if any.
    """

    __slots__ = ()

    def __new__(cls, /, *args, **kwargs):  # noqa: E225
        if not issubclass(cls, constructor.ADTConstructor):
            raise TypeError
        return super(Sum, cls).__new__(cls, *args, **kwargs)

    # Both of these are for consistency with modules defined in the stdlib.
    # BOOM!
    def __init_subclass__(
        cls: type,
        *,
        repr: bool = True,  # pylint: disable=redefined-builtin
        eq: bool = True,  # pylint: disable=invalid-name
        order: bool = False,
        **kwargs: typing.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)  # type: ignore
        if issubclass(cls, constructor.ADTConstructor):
            return
        ordering._ordering_options_are_valid(eq=eq, order=order)

        prewritten_methods.SUBCLASS_ORDER[cls] = constructor.make_constructors(cls)

        source = prewritten_methods.PrewrittenSumMethods

        cls.__init_subclass__ = source.__init_subclass__  # type: ignore

        _sum_new(cls, frozenset(prewritten_methods.SUBCLASS_ORDER[cls]))

        _conditional_call(repr, _set_new_functions, cls, source.__repr__)

        equality_methods_were_set = eq and not _set_new_functions(
            cls, source.__eq__, source.__ne__
        )

        if equality_methods_were_set:
            cls.__hash__ = source.__hash__  # type: ignore

        ordering.raise_for_collision(
            (
                order
                and ordering._can_set_ordering(can_set=equality_methods_were_set)
                and _set_new_functions(
                    cls, source.__lt__, source.__le__, source.__gt__, source.__ge__
                )
            ),
            cls.__name__,
        )

    def __bool__(self) -> bool:
        return True

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if not inspect.isdatadescriptor(
            inspect.getattr_static(self, name, _cant_modify.MISSING)
        ):
            _cant_modify.cant_modify(self, name)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if not inspect.isdatadescriptor(
            inspect.getattr_static(self, name, _cant_modify.MISSING)
        ):
            _cant_modify.cant_modify(self, name)
        super().__delattr__(name)
