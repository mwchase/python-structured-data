"""Property-like descriptors that expose decorators for value-based dispatch."""

from __future__ import annotations

import typing

from ... import _class_placeholder
from ... import _doc_wrapper
from ... import _structure
from .. import matchable
from . import common

T = typing.TypeVar("T")
U = typing.TypeVar("U")


@_doc_wrapper.ProxyWrapper.wrap_class("prop")
class PropertyProxy(typing.Generic[T, U]):
    """Wrapper for Property that doesn't expose the when methods."""

    def __init__(self, prop: Property[T, U]) -> None:
        self.prop = prop

    def getter(
        self, getter: typing.Optional[typing.Callable[[T], U]]
    ) -> Property[T, U]:
        """Return a copy of the wrapped property with the getter replaced."""
        return self.prop.getter(getter)

    def setter(
        self, setter: typing.Optional[typing.Callable[[T, U], None]]
    ) -> Property[T, U]:
        """Return a copy of the wrapped property with the setter replaced."""
        return self.prop.setter(setter)

    def deleter(
        self, deleter: typing.Optional[typing.Callable[[T], None]]
    ) -> Property[T, U]:
        """Return a copy of the wrapped property with the deleter replaced."""
        return self.prop.deleter(deleter)

    # We want this to be invariant, but it's not.
    @typing.overload
    def __get__(self, instance: None, owner: typing.Type[T]) -> Property[T, U]:
        """Return self from the defining class."""

    @typing.overload
    def __get__(self, instance: None, owner: type) -> PropertyProxy[T, U]:
        """Return a proxy from other classes."""

    @typing.overload
    def __get__(self, instance: typing.Any, owner: type) -> U:
        """Evaluate the property otherwise."""

    def __get__(
        self, instance: typing.Optional[T], owner: typing.Type[T]
    ) -> typing.Union[Property[T, U], PropertyProxy[T, U], U]:
        return self.prop.__get__(instance, owner)

    def __set__(self, instance: T, value: U) -> None:
        self.prop.__set__(instance, value)

    def __delete__(self, instance: T) -> None:
        self.prop.__delete__(instance)


@_doc_wrapper.DocWrapper.wrap_class
class Property(common.Descriptor[T], typing.Generic[T, U]):
    """Decorator with value-based dispatch. Acts as a property."""

    fset: typing.Optional[typing.Callable[[T, U], None]] = None
    fdel: typing.Optional[typing.Callable[[T], None]] = None

    protected = False

    def __new__(
        cls,
        func: typing.Optional[typing.Callable[[T], U]] = None,
        fset: typing.Optional[typing.Callable[[T, U], None]] = None,
        fdel: typing.Optional[typing.Callable[[T], None]] = None,
        doc: typing.Optional[str] = None,
    ) -> Property[T, U]:
        del fset, fdel, doc
        # ???????????????????????????????????????????????
        return super().__new__(cls, func)  # type: ignore

    def __init__(
        self,
        func: typing.Optional[typing.Callable[[T], U]] = None,
        fset: typing.Optional[typing.Callable[[T, U], None]] = None,
        fdel: typing.Optional[typing.Callable[[T], None]] = None,
        doc: typing.Optional[str] = None,
    ) -> None:
        del func
        super().__init__()
        self.fset = fset
        self.fdel = fdel
        if doc is not None:
            self.__doc__ = doc
        self.get_matchers: common.MatchTemplate[T] = common.MatchTemplate()
        self.set_matchers: common.MatchTemplate[typing.Tuple[T, U]] = common.MatchTemplate()
        self.delete_matchers: common.MatchTemplate[T] = common.MatchTemplate()
        self.protected = True

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__delattr__(name)

    def getter(
        self, getter: typing.Optional[typing.Callable[[T], U]]
    ) -> Property[T, U]:
        """Return a copy of self with the getter replaced."""
        new: Property[T, U] = Property(getter, self.fset, self.fdel, self.__doc__)
        self.get_matchers.copy_into(new.get_matchers)
        self.set_matchers.copy_into(new.set_matchers)
        self.delete_matchers.copy_into(new.delete_matchers)
        return new

    def setter(
        self, setter: typing.Optional[typing.Callable[[T, U], None]]
    ) -> Property[T, U]:
        """Return a copy of self with the setter replaced."""
        new: Property[T, U] = Property(
            self.__wrapped__, setter, self.fdel, self.__doc__
        )
        self.get_matchers.copy_into(new.get_matchers)
        self.set_matchers.copy_into(new.set_matchers)
        self.delete_matchers.copy_into(new.delete_matchers)
        return new

    def deleter(
        self, deleter: typing.Optional[typing.Callable[[T], None]]
    ) -> Property[T, U]:
        """Return a copy of self with the deleter replaced."""
        new: Property[T, U] = Property(
            self.__wrapped__, self.fset, deleter, self.__doc__
        )
        self.get_matchers.copy_into(new.get_matchers)
        self.set_matchers.copy_into(new.set_matchers)
        self.delete_matchers.copy_into(new.delete_matchers)
        return new

    # We want this to be invariant, but it's not.
    @typing.overload
    def __get__(self, instance: None, owner: typing.Type[T]) -> Property[T, U]:
        """Return self from the defining class."""

    @typing.overload
    def __get__(self, instance: None, owner: type) -> PropertyProxy[T, U]:
        """Return a proxy from other classes."""

    @typing.overload
    def __get__(self, instance: typing.Any, owner: type) -> U:
        """Evaluate the property otherwise."""

    def __get__(
        self, instance: typing.Optional[T], owner: typing.Type[T]
    ) -> typing.Union[Property[T, U], PropertyProxy[T, U], U]:
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

    def __set__(self, instance: T, value: U) -> None:
        matchable_ = matchable.Matchable((instance, value))
        for func in self.set_matchers.match_instance(matchable_, instance):
            func(**typing.cast(typing.Mapping, matchable_.matches))
            return
        if self.fset is None:
            raise ValueError((instance, value))
        self.fset(instance, value)

    def __delete__(self, instance: T) -> None:
        matchable_ = matchable.Matchable(instance)
        for func in self.delete_matchers.match_instance(matchable_, instance):
            func(**typing.cast(typing.Mapping, matchable_.matches))
            return
        if self.fdel is None:
            raise ValueError(instance)
        self.fdel(instance)

    def get_when(
        self, instance: common.Matcher[_structure.Structure[T]]
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding to the getter."""
        return common.decorate(self.get_matchers, instance)

    def set_when(
        self,
        instance: common.Matcher[_structure.Structure[T]],
        value: common.Matcher[_structure.Structure[U]],
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding to the setter."""
        # We're missing the tech to interpret a tuple of structures as a structure.
        return common.decorate(self.set_matchers, _placeholder_tuple2(instance, value))  # type: ignore

    def delete_when(
        self, instance: common.Matcher[_structure.Structure[T]]
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
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


def _placeholder_tuple2(
    fst: common.Matcher[T], snd: common.Matcher[U],
) -> common.Matcher[typing.Tuple[T, U]]:
    if isinstance(fst, _class_placeholder.Placeholder):
        if isinstance(snd, _class_placeholder.Placeholder):
            return _both_placeholder(fst, snd)
        return _fst_placeholder(fst, snd)
    if isinstance(snd, _class_placeholder.Placeholder):
        return _snd_placeholder(fst, snd)
    return (fst, snd)
