"""Utilities for destructuring values using matchables and match targets.

Given a value to destructure, called ``value``:

- Construct a matchable: ``matchable = Matchable(value)``
- The matchable is initially falsy, but it will become truthy if it is passed a
  **match target** that matches ``value``:
  ``assert matchable(some_pattern_that_matches)`` (Matchable returns itself
  from the call, so you can put the calls in an if-elif block, and only make a
  given call at most once.)
- When the matchable is truthy, it can be indexed to access bindings created by
  the target.
"""

from __future__ import annotations

import functools
import inspect
import typing

from . import _attribute_constructor
from . import _destructure
from . import _match_dict
from . import _match_failure
from . import _pep_570_when
from ._match_dict import MatchDict
from ._patterns.basic_patterns import Pattern
from ._patterns.bind import Bind
from ._patterns.mapping_match import AttrPattern
from ._patterns.mapping_match import DictPattern


def names(target) -> typing.List[str]:
    """Return every name bound by a target."""
    return _destructure.DESTRUCTURERS.names(target)


class Matchable:
    """Given a value, attempt to match against a target.

    The truthiness of ``Matchable`` values varies on whether they have bindings
    associated with them. They are truthy exactly when they have bindings.

    ``Matchable`` values provide two basic forms of syntactic sugar.
    ``m_able(target)`` is equivalent to ``m_able.match(target)``, and
    ``m_able[k]`` will return ``m_able.matches[k]`` if the ``Matchable`` is
    truthy, and raise a ``ValueError`` otherwise.
    """

    value: typing.Any
    matches: typing.Optional[MatchDict]

    def __init__(self, value: typing.Any):
        self.value = value
        self.matches = None

    def match(self, target) -> Matchable:
        """Match against target, generating a set of bindings."""
        try:
            self.matches = _match_dict.match(target, self.value)
        except _match_failure.MatchFailure:
            self.matches = None
        return self

    def __call__(self, target) -> Matchable:
        return self.match(target)

    def __getitem__(self, key):
        if self.matches is None:
            raise ValueError
        return self.matches[key]

    def __bool__(self):
        return self.matches is not None


# In lower-case for aesthetics.
pat = _attribute_constructor.AttributeConstructor(  # pylint: disable=invalid-name
    Pattern
)


def _decorate(matchers, structure, func):
    matchers.append((structure, func))
    return func


class Descriptor:
    """Base class for decorator classes."""

    __wrapped__ = None

    def __new__(cls, func, *args, **kwargs):
        new = super().__new__(cls, *args, **kwargs)
        new.__doc__ = None
        if func is None:
            return new
        return functools.wraps(func)(new)


class _DocWrapper:
    def __init__(self, doc=None):
        self.doc = doc

    @classmethod
    def wrap_class(cls, klass):
        """Wrapp a classes docstring to conceal it from instances."""
        klass.__doc__ = cls(klass.__doc__)
        return klass

    def __get__(self, instance, owner):
        if instance is None:
            return self.doc
        return vars(instance).get("__doc__")

    def __set__(self, instance, value):
        vars(instance)["__doc__"] = value

    def __delete__(self, instance):
        vars(instance).pop("__doc__", None)


@_DocWrapper.wrap_class
class Property(Descriptor):
    """Decorator with value-based dispatch. Acts as a property."""

    fset = None
    fdel = None

    protected = False

    def __new__(cls, func=None, fset=None, fdel=None, doc=None, *args, **kwargs):
        del fset, fdel, doc
        return super().__new__(cls, func, *args, **kwargs)

    def __init__(self, func=None, fset=None, fdel=None, doc=None, *args, **kwargs):
        del func
        super().__init__(*args, **kwargs)
        self.fset = fset
        self.fdel = fdel
        if doc is not None:
            self.__doc__ = doc
        self.get_matchers = []
        self.set_matchers = []
        self.delete_matchers = []
        self.protected = True

    def __setattr__(self, name, value):
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__delattr__(name)

    def getter(self, getter):
        """Return a copy of self with the getter replaced."""
        new = Property(getter, self.fset, self.fdel, self.__doc__)
        new.get_matchers.extend(self.get_matchers)
        new.set_matchers.extend(self.set_matchers)
        new.delete_matchers.extend(self.delete_matchers)
        return new

    def setter(self, setter):
        """Return a copy of self with the setter replaced."""
        new = Property(self.__wrapped__, setter, self.fdel, self.__doc__)
        new.get_matchers.extend(self.get_matchers)
        new.set_matchers.extend(self.set_matchers)
        new.delete_matchers.extend(self.delete_matchers)
        return new

    def deleter(self, deleter):
        """Return a copy of self with the deleter replaced."""
        new = Property(self.__wrapped__, self.fset, deleter, self.__doc__)
        new.get_matchers.extend(self.get_matchers)
        new.set_matchers.extend(self.set_matchers)
        new.delete_matchers.extend(self.delete_matchers)
        return new

    def __get__(self, instance, owner):
        if instance is None:
            return self
        matchable = Matchable(instance)
        for (structure, func) in self.get_matchers:
            if matchable(structure):
                return func(**matchable.matches)
        if self.__wrapped__ is None:
            raise ValueError(self)
        return self.__wrapped__(instance)

    def __set__(self, instance, value):
        matchable = Matchable((instance, value))
        for (structure, func) in self.set_matchers:
            if matchable(structure):
                func(**matchable.matches)
                return
        if self.fset is None:
            raise ValueError((instance, value))
        self.fset(instance, value)

    def __delete__(self, instance):
        matchable = Matchable(instance)
        for (structure, func) in self.delete_matchers:
            if matchable(structure):
                func(**matchable.matches)
                return
        if self.fdel is None:
            raise ValueError(instance)
        self.fdel(instance)

    def get_when(self, instance):
        """Add a binding to the getter."""
        structure = instance
        names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.get_matchers, structure)

    def set_when(self, instance, value):
        """Add a binding to the setter."""
        structure = (instance, value)
        names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.set_matchers, structure)

    def delete_when(self, instance):
        """Add a binding to the deleter."""
        structure = instance
        names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.delete_matchers, structure)


def _dispatch(func, matches, bound_args, bound_kwargs):
    for key, value in matches.items():
        if key in bound_kwargs:
            raise TypeError
        bound_kwargs[key] = value
    function_sig = inspect.signature(func)
    function_args = function_sig.bind(**bound_kwargs)
    for parameter in function_sig.parameters.values():
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            function_args.arguments[parameter.name] = bound_args
    function_args.apply_defaults()
    return func(*function_args.args, **function_args.kwargs)


class Function(Descriptor):
    """Decorator with value-based dispatch. Acts as a function."""

    def __init__(self, func, *args, **kwargs):
        del func
        super().__init__(*args, **kwargs)
        self.matchers = []

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self, instance)

    def _bound_and_values(self, args, kwargs):
        # Then we figure out what signature we're giving the outside world.
        signature = inspect.signature(self)
        # The signature lets us regularize the call and apply any defaults
        bound_arguments = signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        # Extract the *args and **kwargs, if any.
        # These are never used in the matching, just passed to the underlying function
        bound_args = ()
        bound_kwargs = {}
        values = bound_arguments.arguments.copy()
        for parameter in signature.parameters.values():
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                bound_args = values.pop(parameter.name)
            if parameter.kind is inspect.Parameter.VAR_KEYWORD:
                bound_kwargs = values.pop(parameter.name)
        return bound_args, bound_kwargs, values

    def __call__(*args, **kwargs):
        # Okay, so, this is a convoluted mess.
        # First, we extract self from the beginning of the argument list
        self, *args = args

        bound_args, bound_kwargs, values = self._bound_and_values(args, kwargs)

        matchable = Matchable(values)
        for structure, func in self.matchers:
            if matchable(structure):
                return _dispatch(func, matchable.matches, bound_args, bound_kwargs)
        raise ValueError(values)

    @_pep_570_when.pep_570_when
    def when(self, kwargs):
        """Add a binding for this function."""
        structure = DictPattern(kwargs, exhaustive=True)
        names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.matchers, structure)


def _make_args_positional(func, positional_until):
    signature = inspect.signature(func)
    new_parameters = []
    for index, parameter in enumerate(signature.parameters.values()):
        if positional_until and parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
            raise ValueError("Signature already contains positional-only arguments")
        if index < positional_until:
            if parameter.kind is not inspect.Parameter.POSITIONAL_OR_KEYWORD:
                raise ValueError("Cannot overwrite non-POSITIONAL_OR_KEYWORD kind")
            parameter = parameter.replace(kind=inspect.Parameter.POSITIONAL_ONLY)
        new_parameters.append(parameter)
    new_signature = signature.replace(parameters=new_parameters)
    if new_signature != signature:
        func.__signature__ = new_signature


# This wraps a function that, for reasons, can't be called directly by the code
# The function body should probably just be a docstring.
def function(_func=None, *, positional_until=0):
    """Convert a function to dispatch by value.

    The original function is not called when the dispatch function is invoked.
    """

    def wrap(func):
        _make_args_positional(func, positional_until)
        return Function(func)

    if _func is None:
        return wrap

    return wrap(_func)


def decorate_in_order(*args):
    """Apply decorators in the order they're passed to the function."""

    def decorator(func):
        for arg in args:
            func = arg(func)
        return func

    return decorator


__all__ = [
    "AttrPattern",
    "Bind",
    "DictPattern",
    "MatchDict",
    "Matchable",
    "Pattern",
    "Property",
    "decorate_in_order",
    "function",
    "names",
    "pat",
]
