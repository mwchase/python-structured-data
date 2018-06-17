import sys
import typing

import pytest

T = typing.TypeVar('T')


def test_main():
    pass


@pytest.mark.skipif(
    sys.version_info >= (3, 6, 6),
    reason='Test fails on newer Pythons')
def test_generic_subclass_fails():
    import structured_data

    with pytest.raises(RuntimeError):
        @structured_data.enum
        class TestClass(typing.Generic[T]):
            Variant: structured_data.Ctor[()]


@pytest.mark.skipif(
    sys.version_info < (3, 6, 6),
    reason='Test fails on older Pythons')
def test_generic_subclass_succeeds():
    import structured_data

    @structured_data.enum
    class TestClass(typing.Generic[T]):
        Variant: structured_data.Ctor[()]

    assert TestClass.Variant()
