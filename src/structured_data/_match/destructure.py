"""Classes for destructuring complex data."""

import typing

from .. import _stack_iter
from .._adt.constructor import ADTConstructor
from .._not_in import not_in
from .._structure import CompoundMatch
from .._unpack import structuring_unpack
from .match_failure import MatchFailure
from .patterns.basic_patterns import Pattern


class Destructurer:
    """Abstract base class for destructuring third-party code."""

    type: typing.ClassVar[type]

    def __init_subclass__(cls, **kwargs) -> None:
        type_: type = kwargs.pop("type")
        super().__init_subclass__(**kwargs)  # type: ignore
        cls.type = type_

    def __init__(self, target):
        self.target = target

    def __call__(self, value):
        return self.destructure(value)

    def destructure(self, value):
        """Return a sequence of subvalues, or raise MatchFailure."""
        raise NotImplementedError


class ADTDestructurer(Destructurer, type=ADTConstructor):
    """Unpack ADT instances into a sequence of values.

    While all ADT instances are tuples in practice, this is ignored.
    """

    def destructure(self, value):
        """Unpack a value into a sequence of instances if the classes match."""
        if value.__class__ is not self.target.__class__:
            raise MatchFailure
        return reversed(structuring_unpack(value))


class TupleDestructurer(Destructurer, type=tuple):
    """Unpack tuples into a sequence of values."""

    def destructure(self, value):
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


T = typing.TypeVar("T", bound="DestructurerList")  # pylint: disable=invalid-name


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

    def __new__(cls, *destructurers):
        return super().__new__(cls, destructurers)

    def get_destructurer(
        self, item
    ) -> typing.Optional[typing.Callable[[typing.Any], typing.Sequence[typing.Any]]]:
        """Return the destructurer for the item, if any.

        In the first case, the item is an instance of ``CompoundMatch``, and
        provides its own destructurer.
        In the second case, the item is an instance of the associated type of
        one of the destructurers, and that destructurer is used to wrap it and
        provide the destructurer.
        In the third case, we assume it's not a structure and therefore can't
        be recursed into.
        """
        if isinstance(item, CompoundMatch):
            return item.destructure
        for destructurer in self:
            if isinstance(item, destructurer.type):
                return destructurer(item)
        return None

    @classmethod
    def custom(cls: typing.Type[T], *destructurers) -> T:
        """Construct a new ``DestructurerList``, with custom destructurers.

        Custom destructurers are tried before the builtins.
        """
        return cls(*destructurers, ADTDestructurer, TupleDestructurer)

    def destructure(self, item) -> typing.Generator:
        """If we can destructure ``item``, do so, otherwise ignore it."""
        destructurer = self.get_destructurer(item)
        if destructurer:
            yield from destructurer(item)

    def stack_iteration(self, item) -> _stack_iter.Action:
        """If ``item`` is a ``Pattern``, yield its name. Otherwise, recurse."""
        if isinstance(item, Pattern):
            return _stack_iter.Yield(item)
        return _stack_iter.Extend(self.destructure(item))

    def names(self, target) -> typing.List[str]:
        """Return a list of names bound by the given structure.

        Raise ValueError if there are duplicate names.
        """
        name_list: typing.List[str] = []
        for item in _stack_iter.stack_iter(target, self.stack_iteration):
            not_in(container=name_list, item=item.name)
            name_list.append(item.name)
        return name_list


DESTRUCTURERS = DestructurerList.custom()


def names(target) -> typing.List[str]:
    """Return every name bound by a target."""
    return DESTRUCTURERS.names(target)
