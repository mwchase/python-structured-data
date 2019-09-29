import pytest


def test_matching(adt, match):
    class TestClass(adt.Sum):
        StrPair: adt.Ctor[str, str]

    matchable = match.Matchable(((1, 2), TestClass.StrPair("a", "b")))
    structure = match.Bind(
        (match.pat.tup[1, match.pat.a], TestClass.StrPair(match.pat.b, match.pat.c)),
        bound=5,
    )
    assert matchable(structure)
    assert matchable.matches == dict(tup=(1, 2), a=2, b="a", c="b", bound=5)
    assert matchable[match.pat.a, match.pat.b, match.pat.c, match.pat.tup] == (
        2,
        "a",
        "b",
        (1, 2),
    )
    assert list(matchable.matches) == [
        "tup",
        "a",
        "b",
        "c",
        "bound",
    ]  # Should preserve ordering.
    assert match.names(structure) == ["tup", "a", "b", "c", "bound"]
    assert matchable[dict(hello=match.pat.a, world=match.pat.b)] == dict(
        hello=2, world="a"
    )


def test_map_interface(match):
    matchable = match.Matchable((1, 2, 3, 4))
    matchable((match.pat.a, match.pat._, match.pat._, match.pat.b))
    assert len(matchable.matches) == 2
    with pytest.raises(KeyError):
        assert not matchable[None]

    matchable.matches[match.pat.c] = 7
    del matchable.matches[match.pat.c]

    with pytest.raises(TypeError):
        matchable.matches[None] = None

    with pytest.raises(KeyError):
        del matchable.matches[None]
