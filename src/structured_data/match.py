import collections

from ._attribute_constructor import AttributeConstructor
from ._match_failure import MatchFailure
from ._patterns import DISCARD
from ._patterns import Pattern
from ._processors import PROCESSORS


def not_in(container, name):
    if name in container:
        raise ValueError


def names(target):
    """Return every name bound by a target."""
    name_list = []
    names_seen = set()
    to_process = [target]
    while to_process:
        item = to_process.pop()
        if isinstance(item, Pattern):
            not_in(names_seen, item.name)
            names_seen.add(item.name)
            name_list.append(item.name)
        else:
            processor = PROCESSORS.get_processor(item)
            if processor:
                to_process.extend(processor(item))
    return name_list


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


def _match_iteration(match_dict, target, value):
    if target is DISCARD:
        return
    if isinstance(target, Pattern):
        not_in(match_dict, target.name)
        match_dict[target.name] = value
        return
    processor = PROCESSORS.get_processor(target)
    if processor:
        yield from zip(processor(target), processor(value))
    elif target != value:
        raise MatchFailure


def _match(target, value):
    match_dict = MatchDict()
    to_process = [(target, value)]
    while to_process:
        to_process.extend(_match_iteration(match_dict, *to_process.pop()))
    return match_dict


class ValueMatcher:
    """Given a value, attempt to match against a target."""

    def __init__(self, value):
        self.value = value
        self.matches = None

    def match(self, target):
        """Match against target, generating a set of bindings."""
        try:
            self.matches = _match(target, self.value)
        except MatchFailure:
            self.matches = None
        return self.matches is not None


pat = AttributeConstructor(Pattern)


__all__ = ['Pattern', 'ValueMatcher', 'names', 'pat']
