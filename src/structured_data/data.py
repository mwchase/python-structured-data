import typing

from . import adt

T = typing.TypeVar("T")
R = typing.TypeVar("R")
E = typing.TypeVar("E")


@adt.adt
class Maybe(typing.Generic[T]):
    """An ADT that wraps a value, or nothing."""

    Just: adt.Ctor[T]
    Nothing: adt.Ctor


@adt.adt
class Either(typing.Generic[E, R]):
    """An ADT that wraps one type, or the other."""

    Left: adt.Ctor[E]
    Right: adt.Ctor[R]
