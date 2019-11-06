"""A pattern to bind external values to a match."""

from __future__ import annotations

import typing

from ... import _structure
from ..._not_in import not_in
from .basic_patterns import Pattern

T = typing.TypeVar("T")


class Bind(_structure.CompoundMatch[T], tuple):
    """A wrapper that adds additional bindings to a successful match.

    The ``Bind`` constructor takes a single required argument, and any number
    of keyword arguments. The required argument is a matcher. When matching, if
    the match succeeds, the ``Bind`` instance adds bindings corresponding to
    its keyword arguments.

    First, the matcher is checked, then the bindings are added in the order
    they were passed.
    """

    __slots__ = ()

    def __new__(
        cls, structure: _structure.Structure[T], /, **kwargs: typing.Any  # noqa: E225
    ):
        if not kwargs:
            return structure
        not_in(container=kwargs, item="_")
        return super().__new__(cls, (structure, tuple(kwargs.items())))

    @property
    def structure(self) -> _structure.Structure[T]:
        """Return the structure to match against."""
        return self[0]

    @property
    def bindings(self) -> typing.Tuple[typing.Tuple[str, typing.Any], ...]:
        """Return the bindings to add to the match."""
        return self[1]

    @typing.overload
    def destructure(
        self, value: _structure.Literal[T]
    ) -> typing.Sequence[_structure.Literal]:
        """Literals just get passed through, with other values added."""

    @typing.overload
    def destructure(self, value: Bind[T]) -> typing.Sequence[_structure.Structure]:
        """Bindings produce a heterogeneous collection."""

    def destructure(
        self, value: typing.Union[Bind[T], _structure.Literal[T]]
    ) -> typing.Sequence[_structure.Structure]:
        """Return a list of sub-values to check.

        If ``value is self``, return all of the bindings, and the structure.

        Otherwise, return the corresponding bound values, followed by the
        original value.
        """
        beginning: typing.List[_structure.Structure]
        end: _structure.Structure
        # Letting mutmut touch this line thoroughly locked things up.
        if value is self:  # pragma: no mutate
            beginning = [Pattern(name) for (name, _) in reversed(self.bindings)]
            end = self.structure
        else:
            beginning = [
                binding_value for (_, binding_value) in reversed(self.bindings)
            ]
            end = value
        return beginning + [end]
