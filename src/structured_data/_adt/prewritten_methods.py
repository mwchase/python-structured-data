"""Methods to be added to ADT classes."""

import typing
import weakref

from .._unpack import unpack
from .constructor import ADT_BASES


def sum_base(obj: typing.Any) -> typing.Optional[type]:
    """Return the immediate base class of the type of a ``Sum`` instance."""
    return ADT_BASES.get(obj.__class__)


SUBCLASS_ORDER: typing.MutableMapping[
    type, typing.Tuple[type, ...]
] = weakref.WeakKeyDictionary()


class CommonPrewrittenMethods(tuple):
    """Methods to slot into various modified classes."""

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__qualname__, ", ".join(repr(item) for item in unpack(self))
        )

    def __eq__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) == unpack(typing.cast(tuple, other))
        return False

    def __ne__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) != unpack(typing.cast(tuple, other))
        return True

    def __hash__(self) -> int:
        return hash(unpack(self))


class PrewrittenProductMethods(CommonPrewrittenMethods):
    """Methods for subclasses of ``structured_data.adt.Product``."""

    def __lt__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) < unpack(other)
        raise TypeError

    def __le__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) <= unpack(other)
        raise TypeError

    def __gt__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) > unpack(other)
        raise TypeError

    def __ge__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) >= unpack(other)
        raise TypeError


class PrewrittenSumMethods(CommonPrewrittenMethods):
    """Methods for subclasses of ``structured_data.adt.Sum``."""

    def __init_subclass__(cls, **kwargs: typing.Any) -> None:
        raise TypeError(f"Cannot further subclass the class {cls.__name__}")

    def __lt__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) < unpack(other)
        self_base = sum_base(self)
        if sum_base(other) is self_base and self_base is not None:
            order = SUBCLASS_ORDER[self_base]
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index < other_index
        raise TypeError

    def __le__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) <= unpack(other)
        self_base = sum_base(self)
        if sum_base(other) is self_base and self_base is not None:
            order = SUBCLASS_ORDER[self_base]
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index <= other_index
        raise TypeError

    def __gt__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) > unpack(other)
        self_base = sum_base(self)
        if sum_base(other) is self_base and self_base is not None:
            order = SUBCLASS_ORDER[self_base]
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index > other_index
        raise TypeError

    def __ge__(self, other: tuple) -> bool:
        if other.__class__ is self.__class__:
            return unpack(self) >= unpack(other)
        self_base = sum_base(self)
        if sum_base(other) is self_base and self_base is not None:
            order = SUBCLASS_ORDER[self_base]
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index >= other_index
        raise TypeError


__all__ = ["PrewrittenProductMethods", "PrewrittenSumMethods"]
