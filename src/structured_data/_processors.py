from ._adt_constructor import ADTConstructor
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns import AsPattern
from ._patterns import Pattern
from ._unpack import unpack


class Destructurer:

    def __init__(self, target):
        self.target = target

    def __call__(self, value):
        raise NotImplementedError

    type = None


class AsPatternDestructurer(Destructurer):

    def __call__(self, value):
        if self.target is value:
            return reversed(self.target)
        return (value, value)

    type = AsPattern


class ADTDestructurer(Destructurer):

    def __call__(self, value):
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(unpack(value))

    type = ADTConstructor


class TupleDestructurer(Destructurer):

    def __call__(self, value):
        if isinstance(value, self.target.__class__) and len(self.target) == len(value):
            return reversed(value)
        raise MatchFailure

    type = tuple


class DestructurerList:

    def __init__(self, *processors):
        self.processors = tuple(processors)

    def get_processor(self, item):
        for processor in self.processors:
            if isinstance(item, processor.type):
                return processor(item)
        return None

    @classmethod
    def custom(cls, *processors):
        return cls(AsPatternDestructurer, ADTDestructurer, *processors, TupleDestructurer)

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
                processor = self.get_processor(item)
                if processor:
                    to_process.extend(processor(item))
        return name_list


PROCESSORS = DestructurerList.custom()
