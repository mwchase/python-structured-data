import typing

T = typing.TypeVar("T")


class Action:
    def handle(self, to_process: typing.List[T]):
        raise NotImplementedError


class Yield(Action):
    def __init__(self, item) -> None:
        self.item = item

    def handle(self, to_process):
        del to_process
        yield self.item


class Extend(Action):
    def __init__(self, iterable) -> None:
        self.iterable = iterable

    def handle(self, to_process):
        to_process.extend(self.iterable)
        yield from ()


def handle(action: typing.Optional[Action], to_process):
    if action is not None:
        yield from action.handle(to_process)


def stack_iter(first: T, process: typing.Callable[[T], typing.Optional[Action]]):
    to_process = [first]
    while to_process:
        yield from handle(process(to_process.pop()), to_process)
