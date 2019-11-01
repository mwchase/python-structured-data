"""Property-like descriptors that expose decorators for value-based dispatch."""

from __future__ import annotations

import typing

from ... import _class_placeholder
from ... import _doc_wrapper
from .. import matchable
from . import common

OptionalSetter = typing.Optional[typing.Callable[[typing.Any, typing.Any], None]]
OptionalDeleter = typing.Optional[typing.Callable[[typing.Any], None]]

T = typing.TypeVar("T")
U = typing.TypeVar("U")


@_doc_wrapper.ProxyWrapper.wrap_class("prop")
class PropertyProxy:
    """Wrapper for Property that doesn't expose the when methods."""

    def __init__(self, prop: Property) -> None:
        self.prop = prop

    def getter(self, getter):
        """Return a copy of the wrapped property with the getter replaced."""
        return self.prop.getter(getter)

    def setter(self, setter):
        """Return a copy of the wrapped property with the setter replaced."""
        return self.prop.setter(setter)

    def deleter(self, deleter):
        """Return a copy of the wrapped property with the deleter replaced."""
        return self.prop.deleter(deleter)

    def __get__(self, instance, owner):
        return self.prop.__get__(instance, owner)

    def __set__(self, instance, value):
        self.prop.__set__(instance, value)

    def __delete__(self, instance):
        self.prop.__delete__(instance)


@_doc_wrapper.DocWrapper.wrap_class
class Property(common.Descriptor):
    """Decorator with value-based dispatch. Acts as a property."""

    fset: OptionalSetter = None
    fdel: OptionalDeleter = None

    protected = False

    def __new__(
        cls,
        func: typing.Optional[typing.Callable] = None,
        fset: typing.Optional[typing.Callable] = None,
        fdel: typing.Optional[typing.Callable] = None,
        doc: typing.Optional[str] = None,
    ):
        del fset, fdel, doc
        return super().__new__(cls, func)

    def __init__(
        self,
        func: typing.Optional[typing.Callable] = None,
        fset: typing.Optional[typing.Callable] = None,
        fdel: typing.Optional[typing.Callable] = None,
        doc: typing.Optional[str] = None,
    ) -> None:
        del func
        super().__init__()
        self.fset = fset
        self.fdel = fdel
        if doc is not None:
            self.__doc__ = doc
        # A more specific annotation would be good, but that's waiting on
        # further development.
        self.get_matchers: common.MatchTemplate[typing.Any] = common.MatchTemplate()
        self.set_matchers: common.MatchTemplate[typing.Any] = common.MatchTemplate()
        self.delete_matchers: common.MatchTemplate[typing.Any] = common.MatchTemplate()
        self.protected = True

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__delattr__(name)

    def getter(self, getter) -> Property:
        """Return a copy of self with the getter replaced."""
        new = Property(getter, self.fset, self.fdel, self.__doc__)
        self.get_matchers.copy_into(new.get_matchers)
        self.set_matchers.copy_into(new.set_matchers)
        self.delete_matchers.copy_into(new.delete_matchers)
        return new

    def setter(self, setter) -> Property:
        """Return a copy of self with the setter replaced."""
        new = Property(self.__wrapped__, setter, self.fdel, self.__doc__)
        self.get_matchers.copy_into(new.get_matchers)
        self.set_matchers.copy_into(new.set_matchers)
        self.delete_matchers.copy_into(new.delete_matchers)
        return new

    def deleter(self, deleter) -> Property:
        """Return a copy of self with the deleter replaced."""
        new = Property(self.__wrapped__, self.fset, deleter, self.__doc__)
        self.get_matchers.copy_into(new.get_matchers)
        self.set_matchers.copy_into(new.set_matchers)
        self.delete_matchers.copy_into(new.delete_matchers)
        return new

    def __get__(self, instance, owner):
        if instance is None:
            if common.owns(self, owner):
                return self
            return PropertyProxy(self)
        matchable_ = matchable.Matchable(instance)
        for func in self.get_matchers.match_instance(matchable_, instance):
            return func(**typing.cast(typing.Mapping, matchable_.matches))
        if self.__wrapped__ is None:
            raise ValueError(self)
        # Yes it is.
        return self.__wrapped__(instance)  # pylint: disable=not-callable

    def __set__(self, instance, value) -> None:
        matchable_ = matchable.Matchable((instance, value))
        for func in self.set_matchers.match_instance(matchable_, instance):
            func(**typing.cast(typing.Mapping, matchable_.matches))
            return
        if self.fset is None:
            raise ValueError((instance, value))
        self.fset(instance, value)

    def __delete__(self, instance) -> None:
        matchable_ = matchable.Matchable(instance)
        for func in self.delete_matchers.match_instance(matchable_, instance):
            func(**typing.cast(typing.Mapping, matchable_.matches))
            return
        if self.fdel is None:
            raise ValueError(instance)
        self.fdel(instance)

    def get_when(self, instance):
        """Add a binding to the getter."""
        return common.decorate(self.get_matchers, instance)

    def set_when(self, instance, value):
        """Add a binding to the setter."""
        return common.decorate(self.set_matchers, _placeholder_tuple2(instance, value))

    def delete_when(self, instance):
        """Add a binding to the deleter."""
        return common.decorate(self.delete_matchers, instance)


def _fst_placeholder(
    fst: _class_placeholder.Placeholder[T], snd: U
) -> _class_placeholder.Placeholder[typing.Tuple[T, U]]:
    @_class_placeholder.Placeholder
    def _placeholder(cls: type) -> typing.Tuple[T, U]:
        return (fst.func(cls), snd)

    return _placeholder


def _snd_placeholder(
    fst: T, snd: _class_placeholder.Placeholder[U]
) -> _class_placeholder.Placeholder[typing.Tuple[T, U]]:
    @_class_placeholder.Placeholder
    def _placeholder(cls: type) -> typing.Tuple[T, U]:
        return (fst, snd.func(cls))

    return _placeholder


def _both_placeholder(
    fst: _class_placeholder.Placeholder[T], snd: _class_placeholder.Placeholder[U]
) -> _class_placeholder.Placeholder[typing.Tuple[T, U]]:
    @_class_placeholder.Placeholder
    def _placeholder(cls: type) -> typing.Tuple[T, U]:
        return (fst.func(cls), snd.func(cls))

    return _placeholder


_PLACEHOLDERS: typing.Dict[
    typing.Tuple[bool, bool],
    typing.Callable[
        [typing.Any, typing.Any],
        _class_placeholder.Placeholder[typing.Tuple[typing.Any, typing.Any]],
    ],
] = {
    (True, False): _fst_placeholder,
    (False, True): _snd_placeholder,
    (True, True): _both_placeholder,
}


def _placeholder_tuple2(
    fst: typing.Any, snd: typing.Any
) -> typing.Union[
    _class_placeholder.Placeholder[typing.Tuple[typing.Any, typing.Any]],
    typing.Tuple[typing.Any, typing.Any],
]:
    _placeholder = _PLACEHOLDERS.get(
        (
            isinstance(fst, _class_placeholder.Placeholder),
            isinstance(snd, _class_placeholder.Placeholder),
        )
    )
    if _placeholder:
        return _placeholder(fst, snd)
    return (fst, snd)
