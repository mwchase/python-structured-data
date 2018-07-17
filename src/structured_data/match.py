import collections
import keyword
import weakref

from ._enum_constructor import EnumConstructor
from ._unpack import unpack

ATTRIBUTE_CONSTRUCTORS = weakref.WeakKeyDictionary()
ATTRIBUTE_CACHE = weakref.WeakKeyDictionary()


class AttributeConstructor:

    __slots__ = ('__weakref__',)

    def __init__(self, constructor):
        ATTRIBUTE_CONSTRUCTORS[self] = constructor
        ATTRIBUTE_CACHE[self] = {}

    def __getattribute__(self, name):
        return ATTRIBUTE_CACHE[self].setdefault(
            name, ATTRIBUTE_CONSTRUCTORS[self](name))


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


def isinstance_predicate(typ):
    def predicate(target):
        return isinstance(target, typ)
    return predicate


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


PROCESSORS = (
    (isinstance_predicate(AsPattern), as_pattern_processor),
    (isinstance_predicate(EnumConstructor), enum_processor),
    (isinstance_predicate(tuple), tuple_processor),
)


def get_processor(processor_pairs, item):
    for predicate, meta in processor_pairs:
        if predicate(item):
            return meta(item)
    return None


def names(target):
    """Return every name bound by a target."""
    name_list = []
    names_seen = set()
    to_process = [target]
    while to_process:
        item = to_process.pop()
        if isinstance(item, Pattern):
            if item.name in names_seen:
                raise ValueError
            names_seen.add(item.name)
            name_list.append(item.name)
        else:
            processor = get_processor(PROCESSORS, item)
            if processor:
                to_process.extend(processor(item))
    return name_list


class MatchDict(collections.abc.MutableMapping):

    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        if isinstance(key, Pattern):
            key = key.name
        if isinstance(key, str):
            return self.data[key]
        if isinstance(key, tuple):
            return tuple(self[sub_key] for sub_key in key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        if isinstance(key, Pattern):
            key = key.name
        if not isinstance(key, str):
            raise TypeError
        self.data[key] = value

    def __delitem__(self, key):
        if isinstance(key, Pattern):
            key = key.name
        del self.data[key]

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
            if target.name in match_dict:
                raise ValueError
            match_dict[target.name] = value
            continue
        processor = get_processor(PROCESSORS, target)
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


__all__ = ['MatchFailure', 'Pattern', 'ValueMatcher', 'desugar', 'names', 'pat']
