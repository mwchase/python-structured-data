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
        if matcher is DISCARD:
            return match
        return super().__new__(cls, (matcher, match))

    @property
    def matcher(self):
        """Return the left-hand-side of the as-match."""
        return self[0]

    @property
    def match(self):
        """Return the right-hand-side of the as-match."""
        return self[1]


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
        elif isinstance(item, AsPattern):
            to_process.append(item.match)
            to_process.append(item.matcher)
        elif isinstance(item, EnumConstructor):
            to_process.extend(reversed(unpack(item)))
        elif isinstance(item, tuple):
            to_process.extend(reversed(item))
    yield from name_list


def _match(target, value):
    match_dict = collections.OrderedDict()
    to_process = [(target, value)]
    while to_process:
        target, value = to_process.pop()
        if target is DISCARD:
            pass
        elif isinstance(target, Pattern):
            if target.name in match_dict:
                raise ValueError
            match_dict[target.name] = value
        elif isinstance(target, AsPattern):
            to_process.append((target.match, value))
            to_process.append((target.matcher, value))
        elif isinstance(target, EnumConstructor):
            to_process.extend(zip(reversed(unpack(target)),
                                  reversed(desugar(type(target), value))))
        elif (isinstance(target, tuple) and
              target.__class__ is value.__class__ and
              len(target) == len(value)):
            to_process.extend(zip(reversed(target), reversed(value)))
        elif isinstance(target, tuple) or target != value:
            raise MatchFailure
    return match_dict


def get_values(dct, keys):
    """Unpack a dict, in order."""
    for key in keys:
        yield dct[key]


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
