import typing

T = typing.TypeVar('T')


def test_main():
    pass


def test_generic_subclass_succeeds():
    import structured_data

    @structured_data.enum
    class TestClass(typing.Generic[T]):
        pass

    assert TestClass.Variant()
