"""Wrapper to control documentation visibility."""

from __future__ import annotations

import typing

T = typing.TypeVar("T")


class DocWrapper:
    """Custom descriptor that hides class doc on instances."""

    def __init__(self, doc: typing.Optional[str] = None) -> None:
        self.doc = doc

    @classmethod
    def wrap_class(
        cls: typing.Type[DocWrapper], klass: typing.Type[T]
    ) -> typing.Type[T]:
        """Wrap a class's docstring to conceal it from instances."""
        klass.__doc__ = cls(klass.__doc__)  # type: ignore
        return klass

    def __get__(
        self, instance: typing.Optional[T], owner: typing.Type[T]
    ) -> typing.Optional[str]:
        if instance is None:
            return self.doc
        return vars(instance).get("__doc__")

    def __set__(self, instance: T, value: typing.Optional[str]) -> None:
        vars(instance)["__doc__"] = value

    def __delete__(self, instance: T) -> None:
        vars(instance).pop("__doc__", None)


class ProxyWrapper:
    """Custom descriptor that forwards instance doc to an attribute."""

    def __init__(self, name: str, doc: typing.Optional[str]) -> None:
        self.name = name
        self.doc = doc

    @classmethod
    def wrap_class(cls, name: str) -> typing.Callable[[typing.Type[T]], typing.Type[T]]:
        """Wrap a proxy's docstring to forward it for instances."""

        def decorator(klass: typing.Type[T]) -> typing.Type[T]:
            klass.__doc__ = cls(name, klass.__doc__)  # type: ignore
            return klass

        return decorator

    def __get__(
        self, instance: typing.Optional[T], owner: typing.Type[T]
    ) -> typing.Optional[str]:
        if instance is None:
            return self.doc
        return getattr(instance, self.name).__doc__
