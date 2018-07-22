from ._adt_constructor import ADTConstructor
from ._match_failure import MatchFailure
from ._patterns import AsPattern
from ._unpack import unpack


def as_pattern_processor(target):
    def processor(value):
        if target is value:
            return reversed(target)
        return (value, value)
    return processor


def adt_processor(target):
    def processor(value):
        if value.__class__ is not target.__class__:
            raise MatchFailure
        return reversed(unpack(value))
    return processor


def tuple_processor(target):
    def processor(value):
        if isinstance(value, target.__class__) and len(target) == len(value):
            return reversed(value)
        raise MatchFailure
    return processor


class ProcessorList:

    def __init__(self, processors=()):
        self.processors = list(processors)

    def get_processor(self, item):
        for typ, meta_processor in self.processors:
            if isinstance(item, typ):
                return meta_processor(item)
        return None


PROCESSORS = ProcessorList((
    (AsPattern, as_pattern_processor),
    (ADTConstructor, adt_processor),
    (tuple, tuple_processor),
))
