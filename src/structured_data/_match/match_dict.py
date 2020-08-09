"""A class for holding match data and allowing rich access."""

from __future__ import annotations

import collections
import typing

from .. import _not_in
from .. import _stack_iter
from .. import _structure
from . import destructure
from . import match_failure
from .patterns import basic_patterns

T = typing.TypeVar("T")


def _stack_iteration(
    item: typing.Tuple[_structure.Structure[T], _structure.Literal[T]]
) -> typing.Optional[
    _stack_iter.Action[
        typing.Tuple[_structure.Structure[T], _structure.Literal[T]],
        typing.Tuple[basic_patterns.Pattern[T], _structure.Literal[T]],
    ]
]:
    target, value = item
    if target is basic_patterns.DISCARD:
        return None
    if isinstance(target, basic_patterns.Pattern):
        return _stack_iter.Yield((target, value))
    destructurer = destructure.DESTRUCTURERS.get_destructurer(target)
    if destructurer:
        return _stack_iter.Extend(zip(destructurer(target), destructurer(value)))
    if target != value:
        raise match_failure.MatchFailure
    return None


def match(target: _structure.Structure[T], value: _structure.Literal[T]) -> MatchDict:
    """Extract all of the matches between target and value."""
    match_dict = MatchDict()
    pattern: basic_patterns.Pattern
    local_value: _structure.Literal[T]
    for pattern, local_value in _stack_iter.stack_iter(
        (target, value), _stack_iteration
    ):
        _not_in.not_in(container=match_dict, item=pattern.name)
        match_dict[pattern.name] = local_value
    return match_dict


Compound = typing.TypeVar("Compound", tuple, dict)
Index = typing.TypeVar("Index", str, tuple, dict)
SimpleKey = typing.Union[Index, basic_patterns.Pattern]


def _as_name(key: SimpleKey) -> typing.Union[str, Index]:
    if isinstance(key, basic_patterns.Pattern):
        return key.name
    return key


def _multi_index(dct: MatchDict, key: Compound) -> Compound:
    if isinstance(key, tuple):
        assert not isinstance(key, dict)  # I don't know what mypy is yelling about.
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

    @typing.overload
    def __getitem__(self, key: typing.Union[str, basic_patterns.Pattern]) -> typing.Any:
        """Indexing a single item gets that item."""

    @typing.overload
    def __getitem__(self, key: Compound) -> Compound:
        """Compound indexing returns a value the same shape."""

    def __getitem__(self, key: SimpleKey) -> typing.Any:
        key = _as_name(key)
        if isinstance(key, str):
            return self.data[key]
        return _multi_index(self, key)

    def __setitem__(self, key: SimpleKey, value: typing.Any) -> None:
        key = _as_name(key)
        if not isinstance(key, str):
            raise TypeError
        self.data[key] = value

    def __delitem__(self, key: SimpleKey) -> None:
        del self.data[_as_name(key)]

    def __iter__(self) -> typing.Iterator[str]:
        yield from self.data

    def __len__(self) -> int:
        return len(self.data)
