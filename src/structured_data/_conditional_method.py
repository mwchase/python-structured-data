"""Utilities for conditionally proxying method access to another class."""

import functools

from . import _attribute_constructor


class ConditionalMethod:
    """Based on the value of the given attribute, forwards to the superclass or the source class."""
    name = None
    __objclass__ = None

    def __init__(self, source, field_check):
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


def conditional_method(source):
    """Given a source class, return an attribute constructor that makes ConditionalMethods

    It is not recommended to reuse the return value of this function.
    """
    return _attribute_constructor.AttributeConstructor(
        functools.partial(ConditionalMethod, source)
    )
