"""Example types showing simple usage of adt.Sum."""

import typing

from . import adt

# Name type variables like type variables.
T = typing.TypeVar("T")  # pylint: disable=invalid-name
R = typing.TypeVar("R")  # pylint: disable=invalid-name
E = typing.TypeVar("E")  # pylint: disable=invalid-name


class Maybe(adt.Sum, typing.Generic[T]):
    """An ADT that wraps a value, or nothing."""

    Just: adt.Ctor[T]
    Nothing: adt.Ctor


class Either(adt.Sum, typing.Generic[E, R]):
    """An ADT that wraps one type, or the other."""

    Left: adt.Ctor[E]
    Right: adt.Ctor[R]
