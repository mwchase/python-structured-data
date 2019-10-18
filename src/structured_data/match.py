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
import typing

from . import _attribute_constructor
from ._class_placeholder import placeholder
from ._match.descriptor import function as function_
from ._match.descriptor.property_ import Property
from ._match.destructure import names
from ._match.match_dict import MatchDict
from ._match.matchable import Matchable
from ._match.patterns.basic_patterns import Pattern
from ._match.patterns.bind import Bind
from ._match.patterns.mapping_match import AttrPattern
from ._match.patterns.mapping_match import DictPattern

# In lower-case for aesthetics.
pat = _attribute_constructor.AttributeConstructor(  # pylint: disable=invalid-name
    Pattern
)


# This wraps a function that, for reasons, can't be called directly by the code
# The function body should probably just be a docstring.
def function(func: typing.Callable) -> function_.Function:
    """Convert a function to dispatch by value.

    The original function is not called when the dispatch function is invoked.
    """

    return function_.Function(func)


# This wraps a function that, for reasons, can't be called directly by the code
# The function body should probably just be a docstring.
def method(func: typing.Callable) -> function_.Method:
    """Convert a function to dispatch by value.

    The original function is not called when the dispatch function is invoked.
    """

    return function_.Method(func)


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
    "method",
    "placeholder",
    "names",
    "pat",
]
