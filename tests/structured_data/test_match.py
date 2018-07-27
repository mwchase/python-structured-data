import pytest


def test_matching(adt, match):
    @adt.adt
    class TestClass:
        StrPair: adt.Ctor[str, str]

    matchable = match.Matchable(((1, 2), TestClass.StrPair("a", "b")))
    assert not matchable(((match.pat._, 4), match.pat._))
    assert matchable.matches is None
    with pytest.raises(ValueError):
        assert not matchable[None]
    structure = (
        match.pat.tup @ (1, match.pat.a),
        TestClass.StrPair(match.pat.b, match.pat.c),
    )
    assert matchable(structure)
    assert matchable.matches == dict(tup=(1, 2), a=2, b="a", c="b")
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
    ]  # Should preserve ordering.
    assert match.names(structure) == ["tup", "a", "b", "c"]
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


def test_different_length_tuples(match):
    assert not match.Matchable((1,))((1, 1))


def test_different_constructors(adt, match):
    @adt.adt
    class TestClass:
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

    matchable = match.Matchable(TestClass.Left(5))
    assert not matchable(TestClass.Right("abc"))
