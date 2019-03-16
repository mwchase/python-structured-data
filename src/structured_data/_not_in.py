import typing

T = typing.TypeVar("T")


def not_in(container: typing.Container[T], name: T):
    if name in container:
        raise ValueError
