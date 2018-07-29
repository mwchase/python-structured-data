from .._match_failure import MatchFailure
from .compound_match import CompoundMatch


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
