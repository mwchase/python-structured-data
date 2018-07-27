import pytest


def test_dir(option_class):
    dir_result = dir(option_class.Left(1))
    for method in ("__lt__", "__le__", "__gt__", "__ge__"):
        assert (method in dir_result) == option_class.order


def test_cant_nest(option_class):
    with pytest.raises(AttributeError):
        assert not option_class.Left.Left


def test_cant_pass_extra(option_class):
    with pytest.raises(ValueError):
        assert not option_class.Left(1, 2)


def test_cant_pass_nothing(option_class):
    with pytest.raises(ValueError):
        assert not option_class.Left()
