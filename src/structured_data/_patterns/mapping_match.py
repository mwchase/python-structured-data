import typing

from .._match_failure import MatchFailure
from .compound_match import CompoundMatch


def value_cant_be_smaller(
    target_match_dict: typing.Sized, value_match_dict: typing.Sized
):
    if len(value_match_dict) < len(target_match_dict):
        raise MatchFailure


class AttrPattern(CompoundMatch, tuple):
    """A matcher that destructures an object using attribute access."""

    __slots__ = ()

    def __new__(*args, **kwargs) -> "AttrPattern":
        cls, *args = args  # type: ignore
        if args:
            raise ValueError(args)
        return super(AttrPattern, cls).__new__(cls, (tuple(kwargs.items()),))

    @property
    def match_dict(self):
        return self[0]

    def destructure(
        self, value
    ) -> typing.Union[typing.Tuple[()], typing.Tuple[typing.Any, typing.Any]]:
        if not self.match_dict:
            return ()
        if isinstance(value, AttrPattern):
            value_cant_be_smaller(self.match_dict, value.match_dict)
            first_match, *remainder = value.match_dict
            return (AttrPattern(**dict(remainder)), first_match[1])
        first_match = self.match_dict[0]
        try:
            return (value, getattr(value, first_match[0]))
        except AttributeError:
            raise MatchFailure


def dict_pattern_length(dp_or_d: typing.Sized):
    if isinstance(dp_or_d, DictPattern):
        return len(dp_or_d.match_dict)
    return len(dp_or_d)


class DictPattern(CompoundMatch, tuple):
    """A matcher that destructures a dictionary by key."""

    __slots__ = ()

    def __new__(cls, match_dict, *, exhaustive=False) -> "DictPattern":
        return super().__new__(cls, (tuple(match_dict.items()), exhaustive))

    @property
    def match_dict(self):
        return self[0]

    @property
    def exhaustive(self):
        return self[1]

    def exhaustive_length_must_match(self, value: typing.Sized):
        if self.exhaustive and dict_pattern_length(value) != dict_pattern_length(self):
            raise MatchFailure

    def destructure(
        self, value
    ) -> typing.Union[typing.Tuple[()], typing.Tuple[typing.Any, typing.Any]]:
        self.exhaustive_length_must_match(value)
        if not self.match_dict:
            return ()
        if isinstance(value, DictPattern):
            value_cant_be_smaller(self.match_dict, value.match_dict)
            first_match, *remainder = value.match_dict
            return (DictPattern(dict(remainder)), first_match[1])
        first_match = self.match_dict[0]
        try:
            return (value, value[first_match[0]])
        except KeyError:
            raise MatchFailure
