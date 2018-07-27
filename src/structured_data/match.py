import collections

from ._attribute_constructor import AttributeConstructor
from ._destructure import DESTRUCTURERS
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns import DISCARD
from ._patterns import AttrPattern
from ._patterns import DictPattern
from ._patterns import Pattern


def names(target):
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
    def __init__(self):
        self.data = {}

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


def _match_iteration(destructurers, match_dict, target, value):
    if target is DISCARD:
        return
    if isinstance(target, Pattern):
        not_in(match_dict, target.name)
        match_dict[target.name] = value
        return
    destructurer = destructurers.get_destructurer(target)
    if destructurer:
        yield from zip(destructurer(target), destructurer(value))
    elif target != value:
        raise MatchFailure


def _match(target, value, destructurers):
    match_dict = MatchDict()
    to_process = [(target, value)]
    while to_process:
        to_process.extend(
            _match_iteration(destructurers, match_dict, *to_process.pop())
        )
    return match_dict


class Matchable:
    """Given a value, attempt to match against a target."""

    def __init__(self, value, destructurers=DESTRUCTURERS):
        self.value = value
        self.matches = None
        self.destructurers = destructurers

    def match(self, target):
        """Match against target, generating a set of bindings."""
        try:
            self.matches = _match(target, self.value, self.destructurers)
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


__all__ = ["AttrPattern", "DictPattern", "Pattern", "Matchable", "names", "pat"]
