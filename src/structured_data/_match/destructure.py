"""Classes for destructuring complex data."""

from __future__ import annotations

import typing

from .. import _stack_iter
from .. import _structure
from .._adt.constructor import ADTConstructor
from .._not_in import not_in
from .._unpack import structuring_unpack
from .match_failure import MatchFailure
from .patterns.basic_patterns import Pattern

T = typing.TypeVar("T")


# It's not right to stop this just because, but I don't care,
# and it's hard to see how to hit the branches this misses anyway.
# TODO: get this tested now that it's factored out.
def find_superclass(
    bases: typing.Iterable[type], origin: type
) -> type:  # pragma: nocover
    for super_cls in bases:
        if getattr(super_cls, "__origin__", None) is origin:
            return super_cls.__args__[0]  # type: ignore
    raise ValueError


class Destructurer(typing.Generic[T]):
    """Abstract base class for destructuring third-party code."""

    @classmethod
    def get_type(cls) -> typing.Type[T]:
        return find_superclass(
            cls.__orig_bases__,  # type: ignore
            Destructurer,
        )

    def __init__(self, target: T) -> None:
        self.target = target

    def __call__(
        self, value: _structure.Structure[T]
    ) -> typing.Iterable[_structure.Structure]:
        return self.destructure(value)

    @typing.overload
    def destructure(
        self, value: _structure.Literal[T]
    ) -> typing.Iterable[_structure.Literal]:
        """Literals only destructure to literals."""

    @typing.overload
    def destructure(
        self, value: _structure.Structure[T]
    ) -> typing.Iterable[_structure.Structure]:
        """Don't have more specific typing..."""

    def destructure(
        self, value: _structure.Structure[T]
    ) -> typing.Iterable[_structure.Structure]:
        """Return a sequence of subvalues, or raise MatchFailure."""
        raise NotImplementedError


class ADTDestructurer(Destructurer[ADTConstructor]):
    """Unpack ADT instances into a sequence of values.

    While all ADT instances are tuples in practice, this is ignored.
    """

    @typing.overload
    def destructure(
        self, value: _structure.Literal[ADTConstructor]
    ) -> typing.Iterable[_structure.Literal]:
        """Literals only destructure to literals."""

    @typing.overload
    def destructure(
        self, value: _structure.Structure[ADTConstructor]
    ) -> typing.Iterable[_structure.Structure]:
        """Don't have more specific typing..."""

    def destructure(
        self, value: _structure.Structure[ADTConstructor]
    ) -> typing.Iterable[_structure.Structure]:
        """Unpack a value into a sequence of instances if the classes match."""
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(structuring_unpack(typing.cast(tuple, value)))


class TupleDestructurer(Destructurer[tuple]):
    """Unpack tuples into a sequence of values."""

    @typing.overload
    def destructure(
        self, value: _structure.Literal[tuple]
    ) -> typing.Iterable[_structure.Literal]:
        """Literals only destructure to literals."""

    @typing.overload
    def destructure(
        self, value: _structure.Structure[tuple]
    ) -> typing.Iterable[_structure.Structure]:
        """Don't have more specific typing..."""

    def destructure(
        self, value: _structure.Structure[tuple]
    ) -> typing.Iterable[_structure.Structure]:
        """Match against non-ADT tuple subclasses.

        Fail outright when matching ADTs.

        Given a superclass Sup and a subclass Sub, a value of type Sub can be
        interpreted as a value of type Sup, but a value of type Sup can only be
        interpreted as a value of type Sub if Sub is Sup.
        """
        if isinstance(value, ADTConstructor):
            raise MatchFailure
        if isinstance(value, self.target.__class__) and len(self.target) == len(value):
            return reversed(structuring_unpack(value))
        raise MatchFailure


class DestructurerList(tuple):
    """A list of destructurers, which are tried in order.

    The order of resolution is:

    - First, check on the object to be destructured; some classes provide for
    custom destructuring. This is only classes under the control of the
    library, and explicit subclasses of those.
    - Second, iterate over any custom destructurers defined to deal with
    classes defined outside of the library. Currently, this functionality isn't
    really used.
    - Finally, iterate over the builtin custom destructurers, which deal with
    standard library classes, and ADT classes. (ADT classes do not provide
    their own destructurers because they don't auto-define methods beyond those
    needed to interact properly with the Python runtime.)
    """

    __slots__ = ()

    def __new__(cls, *destructurers: typing.Type[Destructurer]) -> DestructurerList:
        return super().__new__(cls, destructurers)  # type: ignore

    def get_destructurer(
        self, item: typing.Any
    ) -> typing.Optional[
        typing.Callable[[typing.Any], typing.Iterable[_structure.Structure]]
    ]:
        """Return the destructurer for the item, if any.

        In the first case, the item is an instance of ``CompoundMatch``, and
        provides its own destructurer.
        In the second case, the item is an instance of the associated type of
        one of the destructurers, and that destructurer is used to wrap it and
        provide the destructurer.
        In the third case, we assume it's not a structure and therefore can't
        be recursed into.
        """
        if isinstance(item, _structure.CompoundMatch):
            return item.destructure
        for destructurer in self:
            if isinstance(item, destructurer.get_type()):
                return destructurer(item)
        return None

    @classmethod
    def custom(cls, *destructurers: typing.Type[Destructurer]) -> DestructurerList:
        """Construct a new ``DestructurerList``, with custom destructurers.

        Custom destructurers are tried before the builtins.
        """
        return cls(*destructurers, ADTDestructurer, TupleDestructurer)

    def destructure(self, item: typing.Any) -> typing.Iterable[_structure.Structure]:
        """If we can destructure ``item``, do so, otherwise ignore it."""
        destructurer = self.get_destructurer(item)
        if destructurer:
            yield from destructurer(item)

    def stack_iteration(
        self, item: _structure.Structure
    ) -> _stack_iter.Action[_structure.Structure, Pattern]:
        """If ``item`` is a ``Pattern``, yield its name. Otherwise, recurse."""
        if isinstance(item, Pattern):
            return _stack_iter.Yield(item)
        return _stack_iter.Extend(self.destructure(item))

    def names(self, target: _structure.Structure) -> typing.List[str]:
        """Return a list of names bound by the given structure.

        Raise ValueError if there are duplicate names.
        """
        name_list: typing.List[str] = []
        for item in _stack_iter.stack_iter(target, self.stack_iteration):
            not_in(container=name_list, item=item.name)
            name_list.append(item.name)
        return name_list


DESTRUCTURERS = DestructurerList.custom()


def names(target: _structure.Structure) -> typing.List[str]:
    """Return every name bound by a target."""
    return DESTRUCTURERS.names(target)
