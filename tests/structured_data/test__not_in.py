import pytest


def test_duplicated_binding(match):
    structure = (match.pat.a, match.pat.a)
    with pytest.raises(ValueError):
        assert not match.names(structure)
