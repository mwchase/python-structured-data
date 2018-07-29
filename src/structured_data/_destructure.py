from ._adt_constructor import ADTConstructor
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns import Bind
from ._patterns import CompoundMatch
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


class ADTDestructurer(Destructurer):
    def destructure(self, value):
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(unpack(value))

    type = ADTConstructor


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
        if isinstance(item, CompoundMatch):
            return item.destructure
        for destructurer in self:
            if isinstance(item, destructurer.type):
                return destructurer(item)
        return None

    @classmethod
    def custom(cls, *destructurers):
        return cls(
            *destructurers,
            ADTDestructurer,
            TupleDestructurer
        )

    def names(self, target):
        name_list = []
        extra_names = ()
        if isinstance(target, Bind):
            extra_names = target.bindings
            target = target.structure
        to_process = [target]
        while to_process:
            item = to_process.pop()
            if isinstance(item, Pattern):
                not_in(name_list, item.name)
                name_list.append(item.name)
            else:
                destructurer = self.get_destructurer(item)
                if destructurer:
                    to_process.extend(destructurer(item))
        for (name, _) in extra_names:
            not_in(name_list, name)
            name_list.append(name)
        return name_list


DESTRUCTURERS = DestructurerList.custom()
