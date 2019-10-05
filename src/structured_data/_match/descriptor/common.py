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

    def _matchers(self):
        raise NotImplementedError


# Filling these in has to be the last thing to happen in __init_subclass__.


# Product
class UnnamedPlaceholder:

    def __init__(*args, **kwargs):
        self, *args = args
        self.args = args
        self.kwargs = kwargs

    def evaluate(self, cls):
        return cls(*self.args, **self.kwargs)


# Sum
class NamedPlaceholder:

    def __init__(self, name: str):
        self.name = name

    def __call__(*args, **kwargs):
        self, *args = args
        return PlaceholderWithArgs(self.name, args, kwargs)


# Sum
class PlaceholderWithArgs:

    def __init__(self, name: str, args, kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def evaluate(self, cls):
        return getattr(cls, self.name)(*self.args, **self.kwargs)
