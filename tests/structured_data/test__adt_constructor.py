import pytest


def test_dir(sum_option_class):
    dir_result = dir(sum_option_class.Left(1))
    for method in ("__lt__", "__le__", "__gt__", "__ge__"):
        assert (method in dir_result) == sum_option_class.order


def test_cant_nest(sum_option_class):
    with pytest.raises(AttributeError):
        assert not sum_option_class.Left.Left


def test_cant_pass_extra(sum_option_class):
    with pytest.raises(ValueError):
        assert not sum_option_class.Left(1, 2)


def test_cant_pass_nothing(sum_option_class):
    with pytest.raises(ValueError):
        assert not sum_option_class.Left()


def test_non_existent_dir_entry_is_acceptable(adt):
    class TestDir(adt.Sum):
        Int: adt.Ctor[int]
        Str: adt.Ctor[str]

        def __dir__(self):
            return super().__dir__() + ["123fake"]

    assert "123fake" in dir(TestDir.Int(5))
