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


def _can_overwrite_kind(parameter: inspect.Parameter) -> None:
    if parameter.kind is inspect.Parameter.POSITIONAL_ONLY:
        raise ValueError("Signature already contains positional-only arguments")
    if parameter.kind is not inspect.Parameter.POSITIONAL_OR_KEYWORD:
        raise ValueError("Cannot overwrite non-POSITIONAL_OR_KEYWORD kind")


def _make_args_positional(func: typing.Callable, positional_until: int) -> None:
    signature = inspect.signature(func)
    new_parameters = list(signature.parameters.values())
    for index, parameter in enumerate(new_parameters[:positional_until]):
        _can_overwrite_kind(parameter)
        new_parameters[index] = parameter.replace(
            kind=inspect.Parameter.POSITIONAL_ONLY
        )
    new_signature = signature.replace(parameters=new_parameters)
    if new_signature != signature:
        func.__signature__ = new_signature  # type: ignore


@typing.overload
def function(
    *, positional_until: int = 0
) -> typing.Callable[[typing.Callable], function_.Function]:
    """Can optionally specify a number of arguments to treat as positional."""


@typing.overload
def function(_func: typing.Callable) -> function_.Function:
    """Can directly decorate a function."""


# This wraps a function that, for reasons, can't be called directly by the code
# The function body should probably just be a docstring.
def function(
    _func: typing.Optional[typing.Callable] = None, *, positional_until: int = 0
) -> typing.Union[
    typing.Callable[[typing.Callable], function_.Function], function_.Function
]:
    """Convert a function to dispatch by value.

    The original function is not called when the dispatch function is invoked.
    """

    def wrap(func: typing.Callable) -> function_.Function:
        _make_args_positional(func, positional_until)
        return function_.Function(func)

    if _func is None:
        return wrap

    return wrap(_func)


@typing.overload
def method(
    *, positional_until: int = 1
) -> typing.Callable[[typing.Callable], function_.Method]:
    """Can optionally specify a number of arguments to treat as positional."""


@typing.overload
def method(_func: typing.Callable) -> function_.Method:
    """Can directly decorate a method."""


# This wraps a function that, for reasons, can't be called directly by the code
# The function body should probably just be a docstring.
def method(
    _func: typing.Optional[typing.Callable] = None, *, positional_until: int = 1
) -> typing.Union[
    typing.Callable[[typing.Callable], function_.Method], function_.Method
]:
    """Convert a function to dispatch by value.

    The original function is not called when the dispatch function is invoked.
    """

    def wrap(func: typing.Callable) -> function_.Method:
        _make_args_positional(func, positional_until)
        return function_.Method(func)

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
    "method",
    "placeholder",
    "names",
    "pat",
]
