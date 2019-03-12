import keyword
import sys

from .compound_match import CompoundMatch

DISCARD = object()


class Pattern(tuple):
    """A matcher that binds a value to a name."""

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
    def name(self):
        """Return the name of the matcher."""
        return tuple.__getitem__(self, 0)

    def __getitem__(self, other):
        return AsPattern(self, other)


class AsPattern(CompoundMatch, tuple):
    """A matcher that contains further bindings."""

    __slots__ = ()

    def __new__(cls, pattern: Pattern, structure):
        if structure is DISCARD:
            return pattern
        return super().__new__(cls, (pattern, structure))

    @property
    def pattern(self):
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
