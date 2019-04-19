class Action:
    def handle(self, to_process):
        raise NotImplementedError


class Yield(Action):
    def __init__(self, item):
        self.item = item

    def handle(self, _to_process):
        yield self.item


class Extend(Action):
    def __init__(self, iterable=()):
        self.iterable = iterable

    def handle(self, to_process):
        to_process.extend(self.iterable)
        yield from ()


def stack_iter(first, process):
    to_process = [first]
    while to_process:
        yield from process(to_process.pop()).handle(to_process)
