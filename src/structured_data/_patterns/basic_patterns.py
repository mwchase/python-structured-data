from __future__ import annotations

import keyword
import sys
import typing

from .compound_match import CompoundMatch

DISCARD = object()


class Pattern(tuple):
    """A matcher that binds a value to a name.

    A ``Pattern`` can be indexed with another matcher to produce an
    ``AsPattern``. When matched with a value, an ``AsPattern`` both binds the
    value to the name, and uses the matcher to match the value, thereby
    constraining it to have a particular shape, and possibly introducing
    further bindings.
    """

    __slots__ = ()

    def __new__(cls, name: str):
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

    def __getitem__(self, other) -> AsPattern:
        return AsPattern(self, other)


class AsPattern(CompoundMatch, tuple):
    """A matcher that contains further bindings."""

    __slots__ = ()

    def __new__(cls, pattern: Pattern, structure) -> typing.Union[Pattern, AsPattern]:
        if structure is DISCARD:
            return pattern
        return super().__new__(cls, (pattern, structure))

    @property
    def pattern(self) -> Pattern:
        """Return the left-hand-side of the as-match."""
        return self[0]

    @property
    def structure(self):
        """Return the right-hand-side of the as-match."""
        return self[1]

    def destructure(self, value):
        if isinstance(value, AsPattern):
            if value is self:
                return (self.structure, self.pattern)
            return (value.structure, value)
        return (value, value)
