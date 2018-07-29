import keyword

from ._match_failure import MatchFailure
from ._not_in import not_in

DISCARD = object()


class CompoundMatch:

    __slots__ = ()

    def destructure(self, value):
        raise NotImplementedError


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


def value_cant_be_smaller(target_match_dict, value_match_dict):
    if len(value_match_dict) < len(target_match_dict):
        raise MatchFailure


def exhaustive_length_must_match(target, value_match_dict):
    if target.exhaustive and len(value_match_dict) != len(target.match_dict):
        raise MatchFailure


class AttrPattern(CompoundMatch, tuple):
    """A matcher that destructures an object using attribute access."""

    __slots__ = ()

    def __new__(*args, **kwargs):
        cls, *args = args
        if args:
            raise ValueError(args)
        return super(AttrPattern, cls).__new__(cls, (tuple(kwargs.items()),))

    @property
    def match_dict(self):
        return self[0]

    def destructure(self, value):
        if isinstance(value, AttrPattern):
            value_cant_be_smaller(self.match_dict, value.match_dict)
            if value.match_dict:
                first_match, *remainder = value.match_dict
                return (AttrPattern(**dict(remainder)), first_match[1])
        elif self.match_dict:
            first_match = self.match_dict[0]
            try:
                return (value, getattr(value, first_match[0]))
            except AttributeError:
                raise MatchFailure
        return ()


class DictPattern(CompoundMatch, tuple):
    """A matcher that destructures a dictionary by key."""

    __slots__ = ()

    def __new__(cls, match_dict, *, exhaustive=False):
        return super(DictPattern, cls).__new__(
            cls, (tuple(match_dict.items()), exhaustive)
        )

    @property
    def match_dict(self):
        return self[0]

    @property
    def exhaustive(self):
        return self[1]

    def destructure(self, value):
        if isinstance(value, DictPattern):
            value_cant_be_smaller(self.match_dict, value.match_dict)
            exhaustive_length_must_match(self, value.match_dict)
            if value.match_dict:
                first_match, *remainder = value.match_dict
                return (DictPattern(dict(remainder)), first_match[1])
        elif self.match_dict:
            exhaustive_length_must_match(self, value)
            first_match = self.match_dict[0]
            try:
                return (value, value[first_match[0]])
            except KeyError:
                raise MatchFailure
        exhaustive_length_must_match(self, value)
        return ()


class Bind(CompoundMatch, tuple):
    """A wrapper that adds additional bindings to a successful match."""

    __slots__ = ()

    def __new__(*args, **kwargs):
        cls, structure = args
        not_in(kwargs, "_")
        return super(Bind, cls).__new__(cls, (structure, tuple(kwargs.items())))

    @property
    def structure(self):
        return self[0]

    @property
    def bindings(self):
        return self[1]

    def destructure(self, value):
        if value is self:
            return [Pattern(name) for (name, _) in reversed(self.bindings)] + [
                self.structure
            ]
        return [binding_value for (_, binding_value) in reversed(self.bindings)] + [
            value
        ]


class Guard(CompoundMatch, tuple):

    __slots__ = ()

    def __new__(cls, guard, structure=DISCARD):
        if structure is not DISCARD:
            return AsGuard(guard, structure)
        return super().__new__(cls, (guard,))

    def __getitem__(self, key):
        return Guard(self.guard, key)

    @property
    def guard(self):
        return tuple.__getitem__(self, 0)

    def destructure(self, value):
        if value is self or self.guard(value):
            return ()
        raise MatchFailure


class AsGuard(CompoundMatch, tuple):

    __slots__ = ()

    def __new__(cls, guard, structure):
        return super().__new__(cls, (guard, structure))

    @property
    def guard(self):
        return self[0]

    @property
    def structure(self):
        return self[1]

    def destructure(self, value):
        if value is self:
            return (self.structure,)
        if self.guard(value):
            return (value,)
        raise MatchFailure
