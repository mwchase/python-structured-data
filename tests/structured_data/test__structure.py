import pytest


def test_cant_use_base_compound():
    from structured_data._structure import CompoundMatch

    with pytest.raises(NotImplementedError):
        CompoundMatch().destructure(None)
