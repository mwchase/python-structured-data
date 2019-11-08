"""The simplest patterns."""

from __future__ import annotations

import keyword
import sys
import typing

from ... import _structure

T = typing.TypeVar("T")


class Pattern(tuple, typing.Generic[T]):
    """A matcher that binds a value to a name.

    A ``Pattern`` can be indexed with another matcher to produce an
    ``AsPattern``. When matched with a value, an ``AsPattern`` both binds the
    value to the name, and uses the matcher to match the value, thereby
    constraining it to have a particular shape, and possibly introducing
    further bindings.
    """

    __slots__ = ()

    def __new__(cls, name: str) -> Pattern:
        if name == "_":
            return DISCARD
        if not name.isidentifier():
            raise ValueError
        if keyword.iskeyword(name):
            raise ValueError
        return super().__new__(cls, (sys.intern(name),))

    @property
    def name(self) -> str:
        """Return the name of the matcher."""
        return tuple.__getitem__(self, 0)

    # I have no idea if this is behaving as I want it to.
    # TODO: Get ``# type: ignore`` away from core user-facing interfaces.
    def __getitem__(  # type: ignore
        self, other: _structure.Structure[T]
    ) -> typing.Union[Pattern[T], AsPattern[T]]:
        return AsPattern.bind(self, other)


DISCARD = typing.cast(Pattern, object())


class AsPattern(_structure.CompoundMatch[T], tuple):
    """A matcher that contains further bindings."""

    __slots__ = ()

    def __new__(
        cls, pattern: Pattern[T], structure: _structure.Structure[T]
    ) -> AsPattern[T]:
        return super().__new__(cls, (pattern, structure))

    @classmethod
    def bind(
        cls, pattern: Pattern[T], structure: _structure.Structure[T]
    ) -> typing.Union[Pattern[T], AsPattern[T]]:
        """Bind the given pattern and structure, if possible."""
        if structure is DISCARD:
            return pattern
        return cls(pattern, structure)

    @property
    def pattern(self) -> Pattern[T]:
        """Return the left-hand-side of the as-match."""
        return self[0]

    @property
    def structure(self) -> _structure.Structure[T]:
        """Return the right-hand-side of the as-match."""
        return self[1]

    @typing.overload
    def destructure(
        self, value: _structure.Literal[T]
    ) -> typing.Tuple[_structure.Literal[T], _structure.Literal[T]]:
        """Literals destructure to themselves."""

    @typing.overload
    def destructure(
        self, value: AsPattern[T]
    ) -> typing.Tuple[_structure.Structure[T], typing.Union[Pattern[T], AsPattern[T]]]:
        """AsPatterns destructure to component patterns."""

    def destructure(
        self, value: typing.Union[AsPattern[T], _structure.Literal[T]]
    ) -> typing.Tuple[_structure.Structure[T], _structure.Structure[T]]:
        """Return a tuple of sub-values to check.

        By default, return the value twice.

        If ``isinstance(value, AsPattern)``, return two values:
        First, the structure to match against.
        Second, by default, the value itself, but if ``value is self``,
        instead return the pattern to bind to.

        The behavior of returning the full AsPattern when ``value is not self``
        is present because it makes it possible to sensically use an AsPattern
        as a target, which I don't know if there's a good reason for, but it
        was easy to implement.
        """
        if isinstance(value, AsPattern):
            # Letting mutmut touch this line thoroughly locked things up.
            if value is self:  # pragma: no mutate
                return (self.structure, self.pattern)
            return (value.structure, value)
        return (value, value)
