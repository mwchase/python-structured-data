import pytest


def test_sum_property(adt):
    class TestSum(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @property
        def prop(self):
            pass

    test_value = TestSum.Left(1)
    assert test_value.prop is None
    with pytest.raises(AttributeError):
        test_value.prop = 1
    with pytest.raises(AttributeError):
        test_value.dne = 1
    with pytest.raises(AttributeError):
        test_value.Left = 1
    with pytest.raises(AttributeError):
        del test_value.prop
    with pytest.raises(AttributeError):
        del test_value.dne
    with pytest.raises(AttributeError):
        del test_value.Left
