import typing

from ._adt_constructor import ADTConstructor
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns.basic_patterns import Pattern
from ._patterns.compound_match import CompoundMatch
from ._unpack import unpack

_TYPE = type


class Destructurer:
    def __init_subclass__(cls, type, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.type: _TYPE = type

    def __init__(self, target):
        self.target = target

    def __call__(self, value):
        return self.destructure(value)

    def destructure(self, value):
        raise NotImplementedError


class ADTDestructurer(Destructurer, type=ADTConstructor):
    def destructure(self, value):
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(unpack(value))


class TupleDestructurer(Destructurer, type=tuple):
    def destructure(self, value):
        if isinstance(value, self.target.__class__) and len(self.target) == len(value):
            return reversed(value)
        raise MatchFailure


T = typing.TypeVar("T", bound="DestructurerList")


class DestructurerList(tuple):

    __slots__ = ()

    def __new__(cls, *destructurers):
        return super().__new__(cls, destructurers)

    def get_destructurer(
        self, item
    ) -> typing.Optional[typing.Callable[[typing.Any], typing.Sequence[typing.Any]]]:
        if isinstance(item, CompoundMatch):
            return item.destructure
        for destructurer in self:
            if isinstance(item, destructurer.type):
                return destructurer(item)
        return None

    @classmethod
    def custom(cls: typing.Type[T], *destructurers) -> T:
        return cls(*destructurers, ADTDestructurer, TupleDestructurer)

    def stack_iter(self, target):
        to_process = [target]
        while to_process:
            item = to_process.pop()
            if isinstance(item, Pattern):
                yield item
            else:
                destructurer = self.get_destructurer(item)
                if destructurer:
                    to_process.extend(destructurer(item))

    def names(self, target) -> typing.List[str]:
        name_list: typing.List[str] = []
        for item in self.stack_iter(target):
            not_in(name_list, item.name)
            name_list.append(item.name)
        return name_list


DESTRUCTURERS = DestructurerList.custom()
