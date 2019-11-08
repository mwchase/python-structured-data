"""Matches that extract values via attribute access or dict indexing."""

from __future__ import annotations

import typing

from ... import _structure
from ..match_failure import MatchFailure

T = typing.TypeVar("T")
D = typing.TypeVar("D", bound=dict)


def value_cant_be_smaller(
    target_match_dict: typing.Sized, value_match_dict: typing.Sized
) -> None:
    """If the target is too small, fail."""
    if len(value_match_dict) < len(target_match_dict):
        raise MatchFailure


class AttrPattern(_structure.CompoundMatch[T], tuple):
    """A matcher that destructures an object using attribute access.

    The ``AttrPattern`` constructor takes keyword arguments. Each name-value
    pair is the name of an attribute, and a matcher to apply to that attribute.

    Attributes are checked in the order they were passed.
    """

    __slots__ = ()

    def __new__(cls, /, **kwargs: typing.Any) -> "AttrPattern":  # noqa: E225
        return super().__new__(cls, (tuple(kwargs.items()),))

    @property
    def match_dict(self) -> typing.Tuple[typing.Tuple[str, typing.Any], ...]:
        """Return the dict of matches to check."""
        return self[0]

    @typing.overload
    def destructure(
        self, value: _structure.Literal[T]
    ) -> typing.Union[
        typing.Tuple[()], typing.Tuple[_structure.Literal[T], _structure.Literal]
    ]:
        """Literals return themselves, as needed."""

    @typing.overload
    def destructure(
        self, value: AttrPattern[T]
    ) -> typing.Union[
        typing.Tuple[()],
        typing.Tuple[_structure.Structure[T], _structure.Structure[typing.Any]],
    ]:
        """AttrPatterns break themselves down."""

    def destructure(
        self, value: typing.Union[AttrPattern[T], _structure.Literal[T]]
    ) -> typing.Union[
        typing.Tuple[()],
        typing.Tuple[_structure.Structure[T], _structure.Structure[typing.Any]],
    ]:
        """Return a tuple of sub-values to check.

        If self is empty, return no values from self or the target.

        Special-case matching against another AttrPattern as follows:
        Confirm that the target isn't smaller than self, then
        Extract the first match from the target's match_dict, and
        Return the smaller value, and the first match's value.
        (This works as desired when value is self, but all other cases
        where ``isinstance(value, AttrPattern)`` are unspecified.)

        By default, it takes the first match from the match_dict, and
        returns the original value, and the result of calling ``getattr`` with
        the target and the match's key.
        """
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


def dict_pattern_length(dp_or_d: typing.Sized) -> int:
    """Return the length of the argument for the purposes of ``DictPattern``.

    Normally, this is just the length of the argument, but if the argument is a
    DictPattern, it is the argument's match_dict's length.
    """
    if isinstance(dp_or_d, DictPattern):
        return len(dp_or_d.match_dict)
    return len(dp_or_d)


class DictPattern(_structure.CompoundMatch[D], tuple):
    """A matcher that destructures a dictionary by key.

    The ``DictPattern`` constructor takes a required argument, a dictionary
    where the keys are keys to check, and the values are matchers to apply.
    It also takes an optional keyword argument, "exhaustive", which defaults to
    False.
    If "exhaustive" is True, then the match requires that the matched
    dictionary has no keys not in the ``DictPattern``. Otherwise, "extra" keys
    are ignored.

    Keys are checked in iteration order.
    """

    __slots__ = ()

    def __new__(cls, match_dict: D, *, exhaustive: bool = False) -> DictPattern[D]:
        return super().__new__(cls, (tuple(match_dict.items()), exhaustive))

    @property
    def match_dict(self) -> typing.Tuple[typing.Tuple[typing.Any, typing.Any], ...]:
        """Return the dict of matches to check."""
        return self[0]

    @property
    def exhaustive(self) -> bool:
        """Return whether the target must of the exact keys as self."""
        return self[1]

    def exhaustive_length_must_match(self, value: typing.Sized) -> None:
        """If the match is exhaustive and the lengths differ, fail."""
        if self.exhaustive and dict_pattern_length(value) != dict_pattern_length(self):
            raise MatchFailure

    @typing.overload
    def destructure(
        self, value: _structure.Literal[D]
    ) -> typing.Union[
        typing.Tuple[()], typing.Tuple[_structure.Literal[D], _structure.Literal[typing.Any]]
    ]:
        """Dicts get returned unchanged, and indexed."""

    @typing.overload
    def destructure(
        self, value: DictPattern[D]
    ) -> typing.Union[
        typing.Tuple[()], typing.Tuple[DictPattern[D], _structure.Structure[typing.Any]]
    ]:
        """DictPatterns get reconfigured."""

    def destructure(
        self, value: typing.Union[DictPattern[D], _structure.Literal[D]]
    ) -> typing.Union[
        typing.Tuple[()],
        typing.Tuple[_structure.Structure[D], _structure.Structure[typing.Any]],
    ]:
        """Return a tuple of sub-values to check.

        If self is exhaustive and the lengths don't match, fail.

        If self is empty, return no values from self or the target.

        Special-case matching against another DictPattern as follows:
        Confirm that the target isn't smaller than self, then
        Extract the first match from the target's match_dict, and
        Return the smaller value, and the first match's value.
        Note that the returned DictPattern is never exhaustive; the
        exhaustiveness check is accomplished by asserting that the lengths
        start out the same, and that every key in self is present in value.
        (This works as desired when value is self, but all other cases
        where ``isinstance(value, DictPattern)`` are unspecified.)

        By default, it takes the first match from the match_dict, and
        returns the original value, and the result of indexing the target with
        the match's key.
        """
        self.exhaustive_length_must_match(from_literal(value))
        if not self.match_dict:
            return ()
        if isinstance(value, DictPattern):
            value_cant_be_smaller(self.match_dict, value.match_dict)
            first_match, *remainder = value.match_dict
            return (DictPattern(typing.cast(D, dict(remainder))), first_match[1])
        first_match = self.match_dict[0]
        try:
            return (value, from_literal(value)[first_match[0]])
        except KeyError:
            raise MatchFailure


@typing.overload
def from_literal(value: DictPattern[D]) -> DictPattern[D]:
    """Leave DictPatterns unchanged."""


@typing.overload
def from_literal(value: _structure.Literal[D]) -> D:
    """Through a mysterious process, convert a literal to a value."""


def from_literal(
    value: typing.Union[DictPattern[D], _structure.Literal[D]]
) -> typing.Union[DictPattern[D], D]:
    return value  # type: ignore
