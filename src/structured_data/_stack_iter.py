"""Classes and functions for implementing self-referential iterators."""

import typing

# Name type variables like type variables.
T = typing.TypeVar("T")  # pylint: disable=invalid-name


class Action:
    """Abstract base class for reified stack iteration actions."""
    def handle(self, to_process: typing.List[T]):
        """Yield a value or mutate the stack."""
        raise NotImplementedError


class Yield(Action):
    """Reified action for yielding an output value."""
    def __init__(self, item) -> None:
        self.item = item

    def handle(self, to_process):
        """Yield out ``self.item``"""
        del to_process
        yield self.item


class Extend(Action):
    """Reified action for pushing to the stack."""
    def __init__(self, iterable) -> None:
        self.iterable = iterable

    def handle(self, to_process):
        """Extend the process list with ``iterable``, and yield nothing."""
        to_process.extend(self.iterable)
        yield from ()


def handle(action: typing.Optional[Action], to_process):
    """If ``action`` is an ``Action``, delegate to its ``handle`` method."""
    if action is not None:
        yield from action.handle(to_process)


def stack_iter(first: T, process: typing.Callable[[T], typing.Optional[Action]]):
    """Stack iterate over the initial value using the processing function.

    To "stack iterate" is to build a stack, starting with the initial value.
    Then, as long as the stack is non-empty, pop the top value, pass it to the
    processing function, and use the ``handle`` helper to ignore ``None``
    values. If the processing function returns a value, it will be a subclass
    of Action, and its ``handle`` method can yield values or mutate the stack
    arbitrarily.

    The point of this setup is to write very little code in the service of
    desctructuring nested data without relying on unbounded recursion.
    """
    to_process = [first]
    while to_process:
        yield from handle(process(to_process.pop()), to_process)
