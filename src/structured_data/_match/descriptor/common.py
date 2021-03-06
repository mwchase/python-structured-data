"""Common classes and functions for implementing dynamic matchers."""

from __future__ import annotations

import functools
import typing

from ... import _class_placeholder
from ..._adt import prewritten_methods
from .. import destructure

T = typing.TypeVar("T")  # pylint: disable=invalid-name

Matcher = typing.Union[T, _class_placeholder.Placeholder[T]]


def _apply(structure: Matcher[T], base: typing.Optional[type]) -> T:
    if isinstance(structure, _class_placeholder.Placeholder):
        # The cast is safe because we do the abstract check higher up
        new = structure.func(typing.cast(type, base))
        _check_structure(new)
        return new
    non_placeholder = typing.cast(T, structure)
    _check_structure(non_placeholder)
    return non_placeholder


class MatchTemplate(typing.Generic[T]):
    """The core data type for managing dynamic matching functions."""

    def __init__(self) -> None:
        self._templates: typing.List[typing.Tuple[Matcher[T], typing.Callable]] = []
        self._abstract = False
        self._cache: typing.Dict[
            typing.Optional[type], typing.List[typing.Tuple[T, typing.Callable]]
        ] = {}

    def copy_into(self, other: MatchTemplate[T]) -> None:
        """Given another template, copy this one's contents into it."""
        for structure, func in self._templates:
            other.add_structure(structure, func)

    # @property
    # def abstract(self):
    #     return self._abstract

    def add_structure(self, structure: Matcher[T], func: typing.Callable) -> None:
        """Add the given structure and function to the match template."""
        self._templates.append((structure, func))
        if isinstance(structure, _class_placeholder.Placeholder):
            self._abstract = True
            self._cache.pop(None, None)
        for base, structures in self._cache.items():
            structures.append((_apply(structure, base), func))

    def _get_matchers(
        self, base: type
    ) -> typing.List[typing.Tuple[T, typing.Callable]]:
        if base in self._cache:
            return self._cache[base]
        return self._cache.setdefault(
            base,
            [(_apply(structure, base), func) for (structure, func) in self._templates],
        )

    def match_instance(self, matchable, instance) -> typing.Iterator[typing.Callable]:
        """Get the base associated with instance, if any, and match with it."""
        base = prewritten_methods.sum_base(instance) if self._abstract else None
        yield from self.match(matchable, base)

    def match(self, matchable, base) -> typing.Iterator[typing.Callable]:
        """If there is a match in the context of base, yield implementation."""
        if base is None and self._abstract:
            raise ValueError
        for structure, func in self._get_matchers(base):
            if matchable(structure):
                break
        else:
            return
        # https://github.com/PyCQA/pylint/issues/1175
        yield func  # pylint: disable=undefined-loop-variable


def _check_structure(structure) -> None:
    destructure.names(structure)  # Raise ValueError if there are duplicates


def decorate(matchers: MatchTemplate[T], structure: Matcher[T]):
    """Create a function decorator using the given structure, MatchTemplate."""

    def decorator(func: typing.Callable) -> typing.Callable:
        matchers.add_structure(structure, func)
        return func

    return decorator


class Descriptor:
    """Base class for decorator classes."""

    __wrapped__: typing.Optional[typing.Callable] = None
    __name__: typing.Optional[str] = None

    def __new__(cls, func: typing.Optional[typing.Callable]) -> Descriptor:
        new = super().__new__(cls)
        new.__doc__ = None
        if func is None:
            return new
        return typing.cast(Descriptor, functools.wraps(func)(new))

    def __set_name__(self, owner: type, name: str) -> None:
        vars(self).setdefault("__name__", name)


SENTINEL = object()


def owns(descriptor: Descriptor, owner: type) -> bool:
    """Return whether the given class owns the given descriptor."""
    name = descriptor.__name__
    if name is None:
        return False
    return vars(owner).get(name, SENTINEL) is descriptor
