"""Example types showing simple usage of adt.Sum."""

import typing

from . import adt
from . import match

# Name type variables like type variables.
T = typing.TypeVar("T")  # pylint: disable=invalid-name
R = typing.TypeVar("R")  # pylint: disable=invalid-name
E = typing.TypeVar("E")  # pylint: disable=invalid-name


def just(pat: match.Pattern) -> match.Placeholder:
    @match.placeholder
    def placeholder(cls):
        return cls.Just(pat)
    return placeholder


@match.placeholder
def nothing(cls):
    return cls.Nothing()


class MaybeMixin(adt.SumBase, typing.Generic[T]):
    """Mixin that defines Maybe semantics."""

    Just: adt.Ctor[T]  # type: ignore
    Nothing: adt.Ctor

    @match.function
    def __bool__(self) -> bool:
        """Implement coercion to bool."""


@MaybeMixin.__bool__.when(self=just(match.pat._))
def __bool_true():
    return True


@MaybeMixin.__bool__.when(self=nothing)
def __bool_false():
    return False


class Maybe(MaybeMixin, adt.Sum):  # type: ignore
    """An ADT that wraps a value, or nothing."""


class EitherMixin(adt.SumBase, typing.Generic[E, R]):
    """Mixin that defines Either semantics."""

    Left: adt.Ctor[E]  # type: ignore
    Right: adt.Ctor[R]  # type: ignore


class Either(EitherMixin, adt.Sum):
    """An ADT that wraps one type, or the other."""
