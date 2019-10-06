import pytest

NO_ATTRIBUTE = r"^{klass.__name__!r} object has no attribute {name!r}$"
READ_ONLY = r"^{klass.__name__!r} object attribute {name!r} is read-only$"


def test_sum_property(adt):
    class TestSum(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @property
        def prop(self):
            pass

        none = None

    test_value = TestSum.Left(1)
    assert test_value.prop is None
    with pytest.raises(AttributeError):
        test_value.prop = 1
    with pytest.raises(
        AttributeError, match=NO_ATTRIBUTE.format(klass=TestSum.Left, name="dne")
    ):
        test_value.dne = 1
    with pytest.raises(
        AttributeError, match=READ_ONLY.format(klass=TestSum.Left, name="Left")
    ):
        test_value.Left = 1
    with pytest.raises(
        AttributeError, match=READ_ONLY.format(klass=TestSum.Left, name="none")
    ):
        test_value.none = 1
    with pytest.raises(AttributeError):
        del test_value.prop
    with pytest.raises(
        AttributeError, match=NO_ATTRIBUTE.format(klass=TestSum.Left, name="dne")
    ):
        del test_value.dne
    with pytest.raises(
        AttributeError, match=READ_ONLY.format(klass=TestSum.Left, name="Left")
    ):
        del test_value.Left
