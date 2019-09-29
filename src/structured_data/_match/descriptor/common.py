import functools

from .. import destructure


def decorate(matchers, structure):
    destructure.names(structure)  # Raise ValueError if there are duplicates

    def decorator(func):
        matchers.append((structure, func))
        return func
    return decorator


class Descriptor:
    """Base class for decorator classes."""

    __wrapped__ = None

    def __new__(cls, func, *args, **kwargs):
        new = super().__new__(cls, *args, **kwargs)
        new.__doc__ = None
        if func is None:
            return new
        return functools.wraps(func)(new)
