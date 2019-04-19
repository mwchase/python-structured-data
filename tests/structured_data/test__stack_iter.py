import pytest


def test_cant_abstract(_stack_iter):
    with pytest.raises(NotImplementedError):
        _stack_iter.Action().handle(None)


def test_stack_iter(_stack_iter):
    def double_dec(item):
        if item:
            return _stack_iter.Extend((item - 1, item - 1))
        return _stack_iter.Yield(item)

    assert tuple(_stack_iter.stack_iter(3, double_dec)) == (0,) * 8


def test_none(_stack_iter):
    def nothing(item):
        pass

    assert tuple(_stack_iter.stack_iter(None, nothing)) == ()
