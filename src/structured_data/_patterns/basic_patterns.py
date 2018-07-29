import keyword

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
        return super().__new__(cls, (name,))

    @property
    def name(self):
        """Return the name of the matcher."""
        return tuple.__getitem__(self, 0)

    def __getitem__(self, other):
        return AsPattern(self, other)


class AsPattern(CompoundMatch, tuple):
    """A matcher that contains further bindings."""

    __slots__ = ()

    def __new__(cls, matcher: Pattern, match):
        if match is DISCARD:
            return matcher
        return super().__new__(cls, (matcher, match))

    @property
    def matcher(self):
        """Return the left-hand-side of the as-match."""
        return self[0]

    @property
    def match(self):
        """Return the right-hand-side of the as-match."""
        return self[1]

    def destructure(self, value):
        if isinstance(value, AsPattern):
            if value is self:
                return (self.match, self.matcher)
            return (value.match, value)
        return (value, value)
