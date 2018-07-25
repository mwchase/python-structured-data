from ._adt_constructor import ADTConstructor
from ._match_failure import MatchFailure
from ._patterns import AsPattern
from ._unpack import unpack


class Processor:

    def __init__(self, target):
        self.target = target

    def __call__(self, value):
        raise NotImplementedError

    type = None


class AsPatternProcessor(Processor):

    def __call__(self, value):
        if self.target is value:
            return reversed(self.target)
        return (value, value)

    type = AsPattern


class ADTProcessor(Processor):

    def __call__(self, value):
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(unpack(value))

    type = ADTConstructor


class TupleProcessor(Processor):

    def __call__(self, value):
        if isinstance(value, self.target.__class__) and len(self.target) == len(value):
            return reversed(value)
        raise MatchFailure

    type = tuple


class ProcessorList:

    def __init__(self, processors=()):
        self.processors = tuple(processors)

    def get_processor(self, item):
        for processor in self.processors:
            if isinstance(item, processor.type):
                return processor(item)
        return None


PROCESSORS = ProcessorList((
    AsPatternProcessor,
    ADTProcessor,
    TupleProcessor,
))
