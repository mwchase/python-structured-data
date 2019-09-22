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

import collections
import functools
import inspect
import typing

from ._attribute_constructor import AttributeConstructor
from ._destructure import DESTRUCTURERS
from ._match_failure import MatchFailure
from ._not_in import not_in
from ._patterns.basic_patterns import DISCARD
from ._patterns.basic_patterns import Pattern
from ._patterns.bind import Bind
from ._patterns.mapping_match import AttrPattern
from ._patterns.mapping_match import DictPattern
from ._pep_570_when import pep_570_when
from ._stack_iter import Action
from ._stack_iter import Extend
from ._stack_iter import Yield
from ._stack_iter import stack_iter


def names(target) -> typing.List[str]:
    """Return every name bound by a target."""
    return DESTRUCTURERS.names(target)


def _as_name(key):
    if isinstance(key, Pattern):
        return key.name
    return key


def _multi_index(dct, key):
    if isinstance(key, tuple):
        return tuple(dct[sub_key] for sub_key in key)
    if isinstance(key, dict):
        return {name: dct[value] for (name, value) in key.items()}
    raise KeyError(key)


class MatchDict(collections.abc.MutableMapping):
    """A MutableMapping that allows for retrieval into structures.

    The actual keys in the mapping must be string values. Most of the mapping
    methods will only operate on or yield string keys. The exception is
    subscription: the "key" in subscription can be a structure made of tuples
    and dicts. For example, ``md["a", "b"] == (md["a"], md["b"])``, and
    ``md[{1: "a"}] == {1: md["a"]}``. The typical use of this will be to
    extract many match values at once, as in ``a, b, c == md["a", "b", "c"]``.

    The behavior of most of the pre-defined MutableMapping methods is currently
    neither tested nor guaranteed.
    """

    def __init__(self) -> None:
        self.data: typing.Dict[str, typing.Any] = {}

    def __getitem__(self, key):
        key = _as_name(key)
        if isinstance(key, str):
            return self.data[key]
        return _multi_index(self, key)

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


def _stack_iteration(item) -> typing.Optional[Action]:
    target, value = item
    if target is DISCARD:
        return None
    if isinstance(target, Pattern):
        return Yield(item)
    destructurer = DESTRUCTURERS.get_destructurer(target)
    if destructurer:
        return Extend(zip(destructurer(target), destructurer(value)))
    if target != value:
        raise MatchFailure
    return None


def _match(target, value) -> MatchDict:
    local_target = target
    local_value = value
    match_dict = MatchDict()
    for local_target, local_value in stack_iter(
        (local_target, local_value), _stack_iteration
    ):
        not_in(container=match_dict, item=local_target.name)
        match_dict[local_target.name] = local_value
    return match_dict


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
            self.matches = _match(target, self.value)
        except MatchFailure:
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
pat = AttributeConstructor(Pattern)  # pylint: disable=invalid-name


class Function:
    __wrapped__ = None

    def __new__(cls, func, *args, **kwargs):
        return functools.wraps(func)(super().__new__(cls, *args, **kwargs))

    def __init__(self, func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matchers = []

    def __call__(*args, **kwargs):
        # Okay, so, this is a convoluted mess.
        # First, we extract self from the beginning of the argument list
        self, *args = args
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

        matchable = Matchable(values)
        for structure, function in self.matchers:
            if matchable(structure):
                for k, v in matchable.matches.items():
                    if k in bound_kwargs:
                        raise TypeError
                    bound_kwargs[k] = v
                function_sig = inspect.signature(function)
                function_args = function_sig.bind(**bound_kwargs)
                for parameter in function_sig.parameters.values():
                    if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                        function_args.arguments[parameter.name] = bound_args
                function_args.apply_defaults()
                return function(*function_args.args, **function_args.kwargs)
        raise ValueError(values)

    def _decorate(self, structure, function):
        self.matchers.append((structure, function))
        return function

    @pep_570_when
    def when(self, kwargs):
        structure = DictPattern(kwargs, exhaustive=True)
        names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(self._decorate, structure)


# This wraps a function that, for reasons, can't be called directly by the code
# The function body should probably just be a docstring.
def function(_func=None, *, positional_until=0):
    def wrap(func):
        signature = inspect.signature(func)
        new_parameters = []
        for index, parameter in enumerate(signature.parameters.values()):
            if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
                raise ValueError("Signature already contains positional-only arguments")
            if index < positional_until:
                if parameter.kind is not inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    raise ValueError("Cannot overwrite non-POSITIONAL_OR_KEYWORD kind")
                parameter = parameter.replace(kind=inspect.Parameter.POSITIONAL_ONLY)
            new_parameters.append(parameter)
        new_signature = signature.replace(parameters=new_parameters)
        if new_signature != signature:
            func.__signature__ = new_signature
        return Function(func)

    if _func is None:
        return wrap

    return wrap(_func)


def decorate_in_order(*args):
    def decorator(function):
        for arg in args:
            function = arg(function)
        return function

    return decorator


__all__ = [
    "AttrPattern",
    "Bind",
    "DictPattern",
    "MatchDict",
    "Matchable",
    "Pattern",
    "decorate_in_order",
    "function",
    "names",
    "pat",
]
