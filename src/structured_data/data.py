"""Example types showing simple usage of adt.Sum."""

import typing

from . import adt

# Name type variables like type variables.
T = typing.TypeVar("T")  # pylint: disable=invalid-name
R = typing.TypeVar("R")  # pylint: disable=invalid-name
E = typing.TypeVar("E")  # pylint: disable=invalid-name


class MaybeMixin(adt.SumBase, typing.Generic[T]):

    Just: adt.Ctor[T]  # type: ignore
    Nothing: adt.Ctor


class Maybe(MaybeMixin, adt.Sum):
    """An ADT that wraps a value, or nothing."""


class EitherMixin(adt.SumBase, typing.Generic[E, R]):

    Left: adt.Ctor[E]  # type: ignore
    Right: adt.Ctor[R]  # type: ignore


class Either(EitherMixin, adt.Sum):
    """An ADT that wraps one type, or the other."""
