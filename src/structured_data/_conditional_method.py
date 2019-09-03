"""Utilities for conditionally proxying method access to another class."""

import typing

from . import _attribute_constructor

_T = typing.TypeVar("_T")


class ConditionalMethod(typing.Generic[_T]):
    """Based on the value of the given attribute, forwards to the superclass or the source class."""

    name: str
    __objclass__: typing.Type[_T]

    def __init__(self, source: typing.Type[_T], field_check: str):
        self.source = source
        self.field_check = field_check

    def __set_name__(self, owner, name):
        self.__objclass__ = owner
        self.name = name

    def __get__(self, instance, owner):
        if getattr(owner, self.field_check):
            return getattr(self.source, self.name).__get__(instance, owner)
        target = owner if instance is None else instance
        return getattr(super(self.__objclass__, target), self.name)

    def __set__(self, instance, value):
        # Don't care about this coverage
        raise AttributeError  # pragma: nocover

    def __delete__(self, instance):
        # Don't care about this coverage
        raise AttributeError  # pragma: nocover


def _manual_partial(source: typing.Type[_T]):
    def wrapped(field_check: str):
        return ConditionalMethod(source, field_check)

    return wrapped


def conditional_method(
    source: typing.Type[_T]
) -> _attribute_constructor.AttributeConstructor[ConditionalMethod[_T]]:
    """Given a source class, return an attribute constructor that makes ConditionalMethods

    It is not recommended to reuse the return value of this function.
    """
    return _attribute_constructor.AttributeConstructor(_manual_partial(source))
