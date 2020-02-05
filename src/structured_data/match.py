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

import typing

from . import _attribute_constructor
from ._class_placeholder import Placeholder
from ._match.descriptor import common
from ._match.descriptor import function as function_
from ._match.descriptor import property_
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


@typing.overload
def function(func: typing.Callable) -> function_.Function:
    """Normal functions and methods go to Functions"""


@typing.overload
def function(func: staticmethod) -> function_.StaticMethod:
    """Static methods go to StaticMethods"""


@typing.overload
def function(func: classmethod) -> function_.ClassMethod:
    """Class methods go to ClassMethods."""


@typing.overload
def function(func: property) -> property_.Property:
    """And properties go to Properties."""


def function(func: typing.Any) -> common.Descriptor:
    """Convert a function to dispatch by value.

    The original function is not called when the dispatch function is invoked.
    """
    if isinstance(func, staticmethod):
        return function_.StaticMethod(func.__func__)
    if isinstance(func, classmethod):
        return function_.ClassMethod(func.__func__)
    if isinstance(func, property):
        return property_.Property(func.fget, func.fset, func.fdel, func.__doc__)
    return function_.Function(func)


Deco = typing.Callable[[typing.Callable], typing.Callable]


def decorate_in_order(*args: Deco) -> Deco:
    """Apply decorators in the order they're passed to the function."""

    def decorator(func: typing.Callable) -> typing.Callable:
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
    "Placeholder",
    "decorate_in_order",
    "function",
    "names",
    "pat",
]
