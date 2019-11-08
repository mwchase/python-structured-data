from __future__ import annotations

import typing

S = typing.TypeVar("S")
T = typing.TypeVar("T")


if typing.TYPE_CHECKING:  # pragma: nocover
    from ._match.patterns import basic_patterns

    class Literal(typing.Generic[T]):
        pass

    Structure = typing.Union[
        Literal[T], CompoundMatch[T], basic_patterns.Pattern[T]  # noqa
    ]


class CompoundMatch(typing.Generic[T]):
    """Abstract base class for advanced match classes."""

    __slots__ = ()

    @typing.overload
    def destructure(self, value: Literal[T]) -> typing.Iterable[Literal[typing.Any]]:
        """Literals can only destructure to Literals."""

    @typing.overload
    def destructure(self: S, value: S) -> typing.Iterable[Structure[typing.Any]]:
        """Instances can destructure to anything."""

    def destructure(
        self: S, value: typing.Union[S, Literal[T]]
    ) -> typing.Iterable[Structure[typing.Any]]:
        """Given a value, return a sequence of values extracted from the match.

        Usually has special-case behavior when ``value is self``, possibly as
        part of a broader conditional that happens to be true in that specific
        case as well.
        """
        raise NotImplementedError
