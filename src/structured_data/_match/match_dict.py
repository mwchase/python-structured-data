from __future__ import annotations

import collections
import typing

from .. import _not_in
from .. import _stack_iter
from . import destructure
from . import match_failure
from .patterns import basic_patterns


def _stack_iteration(item) -> typing.Optional[_stack_iter.Action]:
    target, value = item
    if target is basic_patterns.DISCARD:
        return None
    if isinstance(target, basic_patterns.Pattern):
        return _stack_iter.Yield(item)
    destructurer = destructure.DESTRUCTURERS.get_destructurer(target)
    if destructurer:
        return _stack_iter.Extend(zip(destructurer(target), destructurer(value)))
    if target != value:
        raise match_failure.MatchFailure
    return None


def match(target, value) -> MatchDict:
    local_target = target
    local_value = value
    match_dict = MatchDict()
    for local_target, local_value in _stack_iter.stack_iter(
        (local_target, local_value), _stack_iteration
    ):
        _not_in.not_in(container=match_dict, item=local_target.name)
        match_dict[local_target.name] = local_value
    return match_dict


def _as_name(key):
    if isinstance(key, basic_patterns.Pattern):
        return key.name
    return key


def _multi_index(dct, key):
    if isinstance(key, tuple):
        return tuple(dct[sub_key] for sub_key in key)
    if isinstance(key, dict):
        return {name: dct[value] for (name, value) in key.items()}
    raise KeyError(key)


class MatchDict(collections.abc.MutableMapping):
    """A MutableMapping that allows for retrieval into structures.

    The actual keys in the mapping must be string values. Most of the mapping
    methods will only operate on or yield string keys. The exception is
    subscription: the "key" in subscription can be a structure made of tuples
    and dicts. For example, ``md["a", "b"] == (md["a"], md["b"])``, and
    ``md[{1: "a"}] == {1: md["a"]}``. The typical use of this will be to
    extract many match values at once, as in ``a, b, c == md["a", "b", "c"]``.

    The behavior of most of the pre-defined MutableMapping methods is currently
    neither tested nor guaranteed.
    """

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
