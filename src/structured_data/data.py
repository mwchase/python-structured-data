"""Example types showing simple usage of adt.Sum."""

import typing

import typing_extensions

from . import adt
from . import match

# Name type variables like type variables.
T = typing.TypeVar("T")  # pylint: disable=invalid-name
R = typing.TypeVar("R")  # pylint: disable=invalid-name
E = typing.TypeVar("E")  # pylint: disable=invalid-name

MaybeT = typing.TypeVar("MaybeT", bound="MaybeMixin")


def just(pat: match.Pattern) -> match.Placeholder:
    @match.Placeholder
    def placeholder(cls: typing.Type[MaybeT]) -> MaybeT:
        return cls.Just(pat)  # type: ignore

    return placeholder


@match.Placeholder
def nothing(cls: typing.Type[MaybeT]) -> MaybeT:
    return cls.Nothing()  # type: ignore


class MaybeMixin(adt.SumBase, typing.Generic[T]):
    """Mixin that defines Maybe semantics."""

    Just: adt.Ctor[T]  # type: ignore
    Nothing: adt.Ctor

    @match.function
    def __bool__(self) -> bool:
        """Implement coercion to bool."""

    # This works out to reimplementing the underlying behavior, but oh well.
    @match.function
    def __contains__(self, value: T) -> bool:
        """Implement checking for value."""

    @match.function
    def __iter__(self) -> typing.Iterator[T]:
        """Implement iteration."""

    @match.function
    def __reversed__(self) -> typing.Iterator[T]:
        """Implement reversed."""


@MaybeMixin.__reversed__.when(self=just(match.pat.value))
@MaybeMixin.__iter__.when(self=just(match.pat.value))
def __yield_value(value: T) -> typing.Iterator[T]:
    yield value


@MaybeMixin.__reversed__.when(self=nothing)
@MaybeMixin.__iter__.when(self=nothing)
def __yield_nothing() -> typing.Iterator:
    yield from ()

#     @match.function
#     def unwrap(self, msg: typing.Optional[str]) -> T:
#         """Unwrap with an optional message."""


# @MaybeMixin.unwrap.when(self=just(match.pat.value), msg=match.pat._)
# def __just(value: T) -> T:
#     return value


# @MaybeMixin.unwrap.when(self=nothing, msg=None)
# def __no_message() -> None:
#     raise RuntimeError()


# @MaybeMixin.unwrap.when(self=nothing, msg=match.pat.msg)
# def __message(msg: str) -> None:
#     raise RuntimeError(msg)


@MaybeMixin.__bool__.when(self=just(match.pat._))
def __bool_true() -> typing_extensions.Literal[True]:
    return True


@MaybeMixin.__contains__.when(self=just(match.pat.contents), value=match.pat.value)
def __contains_just(contents: T, value: object) -> bool:
    return contents == value


@MaybeMixin.__contains__.when(self=nothing, value=match.pat._)
@MaybeMixin.__bool__.when(self=nothing)
def __false() -> typing_extensions.Literal[False]:
    return False


class Maybe(MaybeMixin, adt.Sum):  # type: ignore
    """An ADT that wraps a value, or nothing."""


class EitherMixin(adt.SumBase, typing.Generic[E, R]):
    """Mixin that defines Either semantics."""

    Left: adt.Ctor[E]  # type: ignore
    Right: adt.Ctor[R]  # type: ignore


class Either(EitherMixin, adt.Sum):
    """An ADT that wraps one type, or the other."""
