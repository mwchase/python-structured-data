from ._adt_constructor import ADTConstructor
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns import AsPattern
from ._patterns import AttrPattern
from ._patterns import DictPattern
from ._patterns import Pattern
from ._unpack import unpack


class Destructurer:
    def __init__(self, target):
        self.target = target

    def __call__(self, value):
        return self.destructure(value)

    def destructure(self, value):
        raise NotImplementedError

    type = None


class AsPatternDestructurer(Destructurer):
    def destructure(self, value):
        if isinstance(value, AsPattern):
            if value is self.target:
                return reversed(value)
            return (value.match, value)
        return (value, value)

    type = AsPattern


class ADTDestructurer(Destructurer):
    def destructure(self, value):
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(unpack(value))

    type = ADTConstructor


def guarded_getattr(value, target_key):
    try:
        return getattr(value, target_key)
    except AttributeError:
        raise MatchFailure


def value_cant_be_smaller(target_match_dict, value_match_dict):
    if len(value_match_dict) < len(target_match_dict):
        raise MatchFailure


def key_destructure(value, match_dict, getter):
    return [getter(value, target_key) for (target_key, _) in reversed(match_dict)]


def same_type_destructure(target_match_dict, value_match_dict):
    for (target_key, _), (value_key, value_value) in zip(
        target_match_dict, value_match_dict
    ):
        if target_key != value_key:
            raise MatchFailure
        yield value_value


class AttrPatternDestructurer(Destructurer):
    def destructure(self, value):
        if isinstance(value, AttrPattern):
            value_cant_be_smaller(self.target.match_dict, value.match_dict)
            return reversed(
                list(same_type_destructure(self.target.match_dict, value.match_dict))
            )
        return key_destructure(value, self.target.match_dict, guarded_getattr)

    type = AttrPattern


def guarded_getitem(value, target_key):
    try:
        return value[target_key]
    except KeyError:
        raise MatchFailure


def exhaustive_length_must_match(target, value_match_dict):
    if target.exhaustive and len(value_match_dict) != len(target.match_dict):
        raise MatchFailure


class DictPatternDestructurer(Destructurer):
    def destructure(self, value):
        if isinstance(value, DictPattern):
            value_cant_be_smaller(self.target.match_dict, value.match_dict)
            exhaustive_length_must_match(self.target, value.match_dict)
            return reversed(
                list(same_type_destructure(self.target.match_dict, value.match_dict))
            )
        exhaustive_length_must_match(self.target, value)
        return key_destructure(value, self.target.match_dict, guarded_getitem)

    type = DictPattern


class TupleDestructurer(Destructurer):
    def destructure(self, value):
        if isinstance(value, self.target.__class__) and len(self.target) == len(value):
            return reversed(value)
        raise MatchFailure

    type = tuple


class DestructurerList(tuple):

    __slots__ = ()

    def __new__(cls, *destructurers):
        return super().__new__(cls, destructurers)

    def get_destructurer(self, item):
        for destructurer in self:
            if isinstance(item, destructurer.type):
                return destructurer(item)
        return None

    @classmethod
    def custom(cls, *destructurers):
        return cls(
            *destructurers,
            AsPatternDestructurer,
            ADTDestructurer,
            AttrPatternDestructurer,
            DictPatternDestructurer,
            TupleDestructurer
        )

    def names(self, target):
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
                destructurer = self.get_destructurer(item)
                if destructurer:
                    to_process.extend(destructurer(item))
        return name_list


DESTRUCTURERS = DestructurerList.custom()
