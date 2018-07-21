import collections
import keyword

from ._attribute_constructor import AttributeConstructor
from ._enum_constructor import EnumConstructor
from ._unpack import unpack


class MatchFailure(BaseException):
    """An exception that signals a failure in ADT matching."""


def desugar(constructor: type, instance: tuple) -> tuple:
    """Return the inside of an ADT instance, given its constructor."""
    if instance.__class__ is not constructor:
        raise MatchFailure
    return unpack(instance)


DISCARD = object()


class Pattern(tuple):
    """A matcher that binds a value to a name."""

    __slots__ = ()

    def __new__(cls, name: str):
        if name == '_':
            return DISCARD
        if not name.isidentifier():
            raise ValueError
        if keyword.iskeyword(name):
            raise ValueError
        return super().__new__(cls, (name,))

    @property
    def name(self):
        """Return the name of the matcher."""
        return self[0]

    def __matmul__(self, other):
        return AsPattern(self, other)


class AsPattern(tuple):
    """A matcher that contains further bindings."""

    __slots__ = ()

    def __new__(cls, matcher: Pattern, match):
        if match is DISCARD:
            return matcher
        return super().__new__(cls, (matcher, match))

    @property
    def matcher(self):
        """Return the left-hand-side of the as-match."""
        return self[0]

    @property
    def match(self):
        """Return the right-hand-side of the as-match."""
        return self[1]


def as_pattern_processor(target):
    def processor(value):
        if target is value:
            yield target.match
            yield target.matcher
        else:
            yield value
            yield value
    return processor


def enum_processor(target):
    def processor(value):
        yield from reversed(desugar(type(target), value))
    return processor


def tuple_processor(target):
    def processor(value):
        if isinstance(value, target.__class__) and len(target) == len(value):
            yield from reversed(value)
        else:
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
    (EnumConstructor, enum_processor),
    (tuple, tuple_processor),
))


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


class MatchDict(collections.abc.MutableMapping):

    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        key = _as_name(key)
        if isinstance(key, str):
            return self.data[key]
        if isinstance(key, tuple):
            return tuple(self[sub_key] for sub_key in key)
        if isinstance(key, dict):
            return {name: self[value] for (name, value) in key.items()}
        raise KeyError(key)

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


def _match(target, value):
    match_dict = MatchDict()
    to_process = [(target, value)]
    while to_process:
        target, value = to_process.pop()
        if target is DISCARD:
            continue
        if isinstance(target, Pattern):
            not_in(match_dict, target.name)
            match_dict[target.name] = value
            continue
        processor = PROCESSORS.get_processor(target)
        if processor:
            to_process.extend(zip(processor(target), processor(value)))
        elif target != value:
            raise MatchFailure
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
