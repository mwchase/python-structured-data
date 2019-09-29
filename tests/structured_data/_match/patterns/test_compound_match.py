import pytest


def test_cant_use_base_compound():
    from structured_data._match.patterns.compound_match import CompoundMatch

    with pytest.raises(NotImplementedError):
        CompoundMatch().destructure(None)
