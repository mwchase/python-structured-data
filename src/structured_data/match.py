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

import inspect

from . import _attribute_constructor
from . import _descriptor
from ._descriptor import Property
from ._destructure import names
from ._match_dict import MatchDict
from ._matchable import Matchable
from ._patterns.basic_patterns import Pattern
from ._patterns.bind import Bind
from ._patterns.mapping_match import AttrPattern
from ._patterns.mapping_match import DictPattern

# In lower-case for aesthetics.
pat = _attribute_constructor.AttributeConstructor(  # pylint: disable=invalid-name
    Pattern
)


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
        return _descriptor.Function(func)

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
