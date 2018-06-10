"""Class decorator for defining abstract data types."""

import ast
import collections
import inspect
import keyword
import sys
import typing

# pylint disables, pending config file
# pylint: disable=too-few-public-methods


_CTOR_CACHE = {}

__version__ = '0.1.0'


class _CtorMeta(type):

    def __getitem__(cls, key):
        if cls is not Ctor:
            raise TypeError
        if not isinstance(key, tuple):
            key = (key,)

        class SpecializedCtor(cls):
            """Generated subclass of Ctor, for type annotations."""
            __args__ = key
        return _CTOR_CACHE.setdefault(key, SpecializedCtor)


class Ctor(metaclass=_CtorMeta):
    """Marker class for enum constructors.

    To use, index with a sequence of types, and annotate a variable in an
    enum-decorated class with it.
    """


@staticmethod
def __new__(cls, name, bases, namespace):
    if bases != (Ctor,):
        raise TypeError
    return super(_CtorMeta, cls).__new__(cls, name, bases, namespace)


_CtorMeta.__new__ = __new__


def _args_length(constructor, global_ns):
    # Handle forward declarations. Needed for 3.7 compatinility.
    if isinstance(constructor, str):
        # Leverage Python's parser instead of trying to parse by hand.
        ctor_ast = ast.parse(constructor, mode='eval')
        # The top-level operation must be a subscript, with normal indexing.
        if (
                isinstance(ctor_ast.body, ast.Subscript)
                and isinstance(ctor_ast.body.slice, ast.Index)):
            # Pull out the index argument
            index = ctor_ast.body.slice.value
            # This basically gets rid of the brackets and index.
            # Next, try to evaluate the result.
            # This relies on Ctor being globally visible at definition time,
            # which seems like a reasonable requirement.
            ctor_ast.body = ctor_ast.body.value
            try:
                value = eval(
                    compile(ctor_ast, '<annotation>', 'eval'), global_ns)
            except Exception:
                # We couldn't tell what it was, so it's probably not Ctor.
                return None
            if value is Ctor:
                # Pull the information directly off a Tuple node.
                if isinstance(index, ast.Tuple):
                    return len(index.elts)
                # Otherwise, assume it's a sequence of length 1.
                # It's possible for this heuristic to return false answers, BUT
                # it seems like everywhere that AST inspection and evaluation
                # disagree, it needs syntax that breaks mypy, so it's sort of
                # like it doesn't matter.
                return 1
        try:
            # If the above conditions didn't hold, maybe it's an alias.
            # We could try to validate the AST, but we need to know the value
            # anyway if it's valid.
            constructor = eval(constructor, global_ns)
        except Exception:
            # This return is a little concerning. It's basically for "We tried
            # to evaluate a forward reference of some kind, and failed."
            # This might reject input at runtime that mypy would accept.
            # The basic solution is to document that you can have forward
            # references FROM a Ctor, but not within a decorated class.
            return None
    # We were given or constructed a Ctor, so just look at it.
    if issubclass(constructor, Ctor) and constructor is not Ctor:
        return len(constructor.__args__)
    # It wasn't a Ctor, so ignore it.
    return None


def _name(cls, function) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


def _set_new_functions(cls, *functions) -> typing.Optional[str]:
    """Attempt to set the attributes corresponding to the functions on cls.

    If any attributes are already defined, fail before setting any, and return
    the already-defined name.
    """
    for function in functions:
        if _name(cls, function) in cls.__dict__:
            return _name(cls, function)
    for function in functions:
        setattr(cls, _name(cls, function), function)
    return None


class MatchFailure(BaseException):
    """An exception that signals a failure in ADT matching."""


def desugar(constructor: type, instance: tuple) -> tuple:
    """Return the inside of an ADT instance, given its constructor."""
    if instance.__class__ is not constructor:
        raise MatchFailure
    return tuple.__getitem__(instance, slice(None))


def _unpack(instance: tuple) -> tuple:
    """Return the inside of any ADT instance.

    This function is not meant for general use.
    """
    return desugar(type(instance), instance)


def _enum_base(obj):
    return getattr(obj.__class__, '__enum_base__', None)


_SHADOWED_ATTRIBUTES = {
    '__add__',
    '__contains__',
    '__getitem__',
    '__iter__',
    '__len__',
    '__mul__',
    '__rmul__',
    'count',
    'index',
    '__hash__',
    '__eq__',
    '__ne__',
    '__lt__',
    '__le__',
    '__gt__',
    '__ge__',
}


class EnumConstructor:

    """Base class for ADT Constructor classes."""

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        """Explicitly forward to base class."""
        return super().__new__(cls, *args, **kwargs)

    def __dir__(self):
        super_dir = super().__dir__()
        my_dir = []
        for attribute in super_dir:
            static_attribute = inspect.getattr_static(self, attribute)
            if attribute in _SHADOWED_ATTRIBUTES and static_attribute is None:
                continue
            if isinstance(static_attribute, _EnumMember):
                continue
            my_dir.append(attribute)
        return my_dir


for _attribute in _SHADOWED_ATTRIBUTES:
    setattr(EnumConstructor, _attribute, None)


def __repr__(self):
    return '{}({})'.format(
        self.__class__.__qualname__,
        ", ".join(repr(item) for item in _unpack(self)))


def __eq__(self, other):
    if other.__class__ is self.__class__:
        return _unpack(self) == _unpack(other)
    if _enum_base(other) is _enum_base(self):
        return False
    return NotImplemented


def __ne__(self, other):
    if other.__class__ is self.__class__:
        return _unpack(self) != _unpack(other)
    if _enum_base(other) is _enum_base(self):
        return True
    return NotImplemented


def __lt__(self, other):
    if other.__class__ is self.__class__:
        return _unpack(self) < _unpack(other)
    if _enum_base(other) is _enum_base(self):
        order = _enum_base(self).__subclass_order__
        self_index = order.index(self.__class__)
        other_index = order.index(other.__class__)
        return self_index < other_index
    return NotImplemented


def __le__(self, other):
    if other.__class__ is self.__class__:
        return _unpack(self) <= _unpack(other)
    if _enum_base(other) is _enum_base(self):
        order = _enum_base(self).__subclass_order__
        self_index = order.index(self.__class__)
        other_index = order.index(other.__class__)
        return self_index <= other_index
    return NotImplemented


def __gt__(self, other):
    if other.__class__ is self.__class__:
        return _unpack(self) > _unpack(other)
    if _enum_base(other) is _enum_base(self):
        order = _enum_base(self).__subclass_order__
        self_index = order.index(self.__class__)
        other_index = order.index(other.__class__)
        return self_index > other_index
    return NotImplemented


def __ge__(self, other):
    if other.__class__ is self.__class__:
        return _unpack(self) >= _unpack(other)
    if _enum_base(other) is _enum_base(self):
        order = _enum_base(self).__subclass_order__
        self_index = order.index(self.__class__)
        other_index = order.index(other.__class__)
        return self_index >= other_index
    return NotImplemented


def __hash__(self):
    return hash(_unpack(self))


_MISSING = object()


def _cant_modify(self, name):
    class_repr = repr(self.__class__.__name__)
    name_repr = repr(name)
    if inspect.getattr_static(self, name, _MISSING) is _MISSING:
        format_msg = '{class_repr} object has no attribute {name_repr}'
    else:
        format_msg = '{class_repr} object attribute {name_repr} is read-only'
    raise AttributeError(
        format_msg.format(class_repr=class_repr, name_repr=name_repr))


def __setattr__(self, name, value):
    _cant_modify(self, name)


def __delattr__(self, name):
    _cant_modify(self, name)


class _EnumMember:

    def __init__(self, cls, subcls):
        if not issubclass(subcls, cls):
            raise ValueError
        self.cls = cls
        self.subcls = subcls

    def __get__(self, obj, cls):
        if cls is self.cls and obj is None:
            return self.subcls
        raise AttributeError('Can only access enum members through base class.')


def _make_constructor(_cls, name, length, subclasses, subclass_order):
    class Constructor(_cls, EnumConstructor, tuple):
        """Auto-generated subclass of an ADT."""
        __slots__ = ()

        __enum_base__ = _cls

        def __new__(cls, *args):
            if len(args) != length:
                raise ValueError
            return super().__new__(cls, args)

    Constructor.__name__ = name
    Constructor.__qualname__ = '{qualname}.{name}'.format(
        qualname=_cls.__qualname__, name=name)

    subclasses.add(Constructor)
    setattr(_cls, name, _EnumMember(_cls, Constructor))
    subclass_order.append(Constructor)


def _allow_subclassing_generic(cls):
    return hasattr(
        typing, 'GenericMeta') and isinstance(cls, typing.GenericMeta)


_SUBCLASS_CHECKS = [_allow_subclassing_generic]


def add_subclass_check(predicate):
    """Allow additional subclasses."""
    _SUBCLASS_CHECKS.append(predicate)


def _process_class(_cls, _repr, eq, order):
    if order and not eq:
        raise ValueError('eq must be true if order is true')

    lengths = {}
    subclasses = set()
    subclass_order = []
    for cls in reversed(_cls.__mro__):
        for key, value in getattr(cls, '__annotations__', {}).items():
            length = _args_length(value, sys.modules[cls.__module__].__dict__)
            # Shadow redone annotations.
            if length is None:
                lengths.pop(key, None)
            else:
                lengths[key] = length

    for name, length in lengths.items():
        _make_constructor(
            _cls, name, length, subclasses, subclass_order)

    if any(predicate(_cls) for predicate in _SUBCLASS_CHECKS):
        @classmethod
        def __init_subclass__(cls, **kwargs):
            if issubclass(cls, tuple(subclasses)):
                raise TypeError
            # Allow it to go through otherwise, because Generic.
            return super(_cls, cls).__init_subclass__(**kwargs)
    else:
        @classmethod
        def __init_subclass__(cls, **kwargs):
            raise TypeError

    _cls.__init_subclass__ = __init_subclass__

    @staticmethod
    def __new__(cls, args):
        if cls not in subclasses:
            raise TypeError
        return super(_cls, cls).__new__(cls, args)

    if _set_new_functions(_cls, __new__):
        base__new__ = _cls.__new__

        @staticmethod
        def __new__(cls, args):
            if cls not in subclasses:
                raise TypeError
            return base__new__(cls, args)

        _cls.__new__ = __new__

    _set_new_functions(_cls, __setattr__, __delattr__)

    if _repr:
        _set_new_functions(_cls, __repr__)

    equality_methods_were_set = False

    if eq:
        equality_methods_were_set = not _set_new_functions(
            _cls, __eq__, __ne__)

    if equality_methods_were_set:
        _cls.__hash__ = __hash__

    if order:
        if not equality_methods_were_set:
            raise ValueError(
                "Can't add ordering methods if equality methods are provided.")
        collision = _set_new_functions(_cls, __lt__, __le__, __gt__, __ge__)
        if collision:
            raise TypeError(
                'Cannot overwrite attribute {collision} in class '
                '{name}. Consider using functools.total_ordering'.format(
                    collision=collision, name=_cls.__name__))

    _cls.__subclass_order__ = tuple(subclass_order)

    return _cls


def enum(_cls=None, *, repr=True, eq=True, order=False):
    """Decorate a class to be an algebraic data type."""

    def wrap(cls):
        """Return the processed class."""
        return _process_class(cls, repr, eq, order)

    if _cls is None:
        return wrap

    return wrap(_cls)


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
            to_process.extend(reversed(_unpack(item)))
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
            to_process.extend(zip(reversed(_unpack(target)),
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