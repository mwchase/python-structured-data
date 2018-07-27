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


class AttrPatternDestructurer(Destructurer):

    def destructure(self, value):
        if isinstance(value, AttrPattern):
            if len(value.match_dict) < len(self.target.match_dict):
                raise MatchFailure
            results = []
            for (target_key, _), (value_key, value_value) in zip(self.target.match_dict, value.match_dict):
                if target_key != value_key:
                    raise MatchFailure
                results.append(value_value)
            return reversed(results)
        try:
            return [getattr(value, target_key) for (target_key, _) in reversed(self.target.match_dict)]
        except AttributeError:
            raise MatchFailure

    type = AttrPattern


class DictPatternDestructurer(Destructurer):

    def destructure(self, value):
        if isinstance(value, DictPattern):
            if len(value.match_dict) < len(self.target.match_dict):
                raise MatchFailure
            if self.target.exhaustive and len(value.match_dict) > len(self.target.match_dict):
                raise MatchFailure
            results = []
            for (target_key, _), (value_key, value_value) in zip(self.target.match_dict, value.match_dict):
                if target_key != value_key:
                    raise MatchFailure
                results.append(value_value)
            return reversed(results)
        if self.target.exhaustive and len(value) != len(self.target.match_dict):
            raise MatchFailure
        try:
            return [value[target_key] for (target_key, _) in reversed(self.target.match_dict)]
        except KeyError:
            raise MatchFailure

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
            AsPatternDestructurer, ADTDestructurer, AttrPatternDestructurer, DictPatternDestructurer, *destructurers, TupleDestructurer)

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
