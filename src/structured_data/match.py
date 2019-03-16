import collections
import operator
import typing

from ._attribute_constructor import AttributeConstructor
from ._destructure import DESTRUCTURERS
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns.basic_patterns import DISCARD
from ._patterns.basic_patterns import Pattern
from ._patterns.bind import Bind
from ._patterns.guard import Guard
from ._patterns.mapping_match import AttrPattern
from ._patterns.mapping_match import DictPattern


def names(target) -> typing.List[str]:
    """Return every name bound by a target."""
    return DESTRUCTURERS.names(target)


def _as_name(key):
    if isinstance(key, Pattern):
        return key.name
    return key


def _multi_index(dct, key):
    if isinstance(key, tuple):
        return tuple(dct[sub_key] for sub_key in key)
    if isinstance(key, dict):
        return {name: dct[value] for (name, value) in key.items()}
    raise KeyError(key)


class MatchDict(collections.abc.MutableMapping):
    def __init__(self) -> None:
        self.data: typing.Dict[str, typing.Any] = {}

    def __getitem__(self, key):
        key = _as_name(key)
        if isinstance(key, str):
            return self.data[key]
        return _multi_index(self, key)

    def __setitem__(self, key, value):
        key = _as_name(key)
        if not isinstance(key, str):
            raise TypeError
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[_as_name(key)]

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)


def _match_iteration(match_dict: MatchDict, target, value):
    if target is DISCARD:
        return
    if isinstance(target, Pattern):
        not_in(match_dict, target.name)
        match_dict[target.name] = value
        return
    destructurer = DESTRUCTURERS.get_destructurer(target)
    if destructurer:
        yield from zip(destructurer(target), destructurer(value))
    elif target != value:
        raise MatchFailure


def _match(target, value) -> MatchDict:
    match_dict = MatchDict()
    to_process = [(target, value)]
    while to_process:
        to_process.extend(_match_iteration(match_dict, *to_process.pop()))
    return match_dict


class Matchable:
    """Given a value, attempt to match against a target."""

    def __init__(self, value):
        self.value = value
        self.matches = None

    def match(self, target) -> "Matchable":
        """Match against target, generating a set of bindings."""
        try:
            self.matches = _match(target, self.value)
        except MatchFailure:
            self.matches = None
        return self

    def __call__(self, target):
        return self.match(target)

    def __getitem__(self, key):
        if self.matches is None:
            raise ValueError
        return self.matches[key]

    def __bool__(self):
        return self.matches is not None


pat = AttributeConstructor(Pattern)

TRUTHY = Guard(operator.truth)
FALSY = Guard(operator.not_)


__all__ = [
    "AttrPattern",
    "Bind",
    "DictPattern",
    "FALSY",
    "Guard",
    "Matchable",
    "Pattern",
    "TRUTHY",
    "names",
    "pat",
]
