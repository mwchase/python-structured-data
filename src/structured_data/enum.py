"""Class decorator for defining abstract data types."""

import ast
import sys
import typing
import weakref

from ._enum_constructor import make_constructor
from ._prewritten_methods import PrewrittenMethods, SUBCLASS_ORDER

# pylint disables, pending config file
# pylint: disable=too-few-public-methods


_CTOR_CACHE = {}

__version__ = '0.2.1'


ARGS = weakref.WeakKeyDictionary()


class Ctor:
    """Marker class for enum constructors.

    To use, index with a sequence of types, and annotate a variable in an
    enum-decorated class with it.
    """

    args = ()

    def __new__(cls, args):
        if args == ():
            return cls
        self = object.__new__(cls)
        object.__setattr__(self, 'args', args)
        return _CTOR_CACHE.setdefault(args, self)

    def __setattr__(self, name, value):
        raise AttributeError(name)

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def __class_getitem__(cls, args):
        if not isinstance(args, tuple):
            args = (args,)
        return cls(args)


def _is_ctor(ctor):
    return Ctor in (ctor, ctor.__class__)


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
    if _is_ctor(constructor):
        return len(constructor.args)
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
        make_constructor(_cls, name, length, subclasses, subclass_order)

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

    _set_new_functions(
        _cls, PrewrittenMethods.__setattr__, PrewrittenMethods.__delattr__)
    _set_new_functions(_cls, PrewrittenMethods.__bool__)

    if _repr:
        _set_new_functions(_cls, PrewrittenMethods.__repr__)

    equality_methods_were_set = False

    if eq:
        equality_methods_were_set = not _set_new_functions(
            _cls, PrewrittenMethods.__eq__, PrewrittenMethods.__ne__)

    if equality_methods_were_set:
        _cls.__hash__ = PrewrittenMethods.__hash__

    if order:
        if not equality_methods_were_set:
            raise ValueError(
                "Can't add ordering methods if equality methods are provided.")
        collision = _set_new_functions(
            _cls,
            PrewrittenMethods.__lt__,
            PrewrittenMethods.__le__,
            PrewrittenMethods.__gt__,
            PrewrittenMethods.__ge__
            )
        if collision:
            raise TypeError(
                'Cannot overwrite attribute {collision} in class '
                '{name}. Consider using functools.total_ordering'.format(
                    collision=collision, name=_cls.__name__))

    SUBCLASS_ORDER[_cls] = tuple(subclass_order)

    return _cls


def enum(_cls=None, *, repr=True, eq=True, order=False):
    """Decorate a class to be an algebraic data type."""

    def wrap(cls):
        """Return the processed class."""
        return _process_class(cls, repr, eq, order)

    if _cls is None:
        return wrap

    return wrap(_cls)


__all__ = ['Ctor', 'enum']
