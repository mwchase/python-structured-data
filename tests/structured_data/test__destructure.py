import pytest


def test_tuple(match):

    matchable = match.Matchable((1, 2))
    assert not matchable((3,))
    assert matchable.matches is None
    structure = (1, match.pat.a)
    assert matchable(structure)
    assert matchable.matches is not None
    assert not matchable(())
    assert matchable.matches is None


def test_adt(adt, match):
    @adt.adt
    class TestClass:
        StrPair: adt.Ctor[str, str]
        Str: adt.Ctor[str]

    matchable = match.Matchable(TestClass.StrPair("a", "b"))
    assert not matchable(TestClass.Str("c"))
    assert matchable.matches is None
    structure = TestClass.StrPair(match.pat.a, match.pat.b)
    assert matchable(structure)


def test_cant_use_base_processor():
    from structured_data import _destructure

    with pytest.raises(NotImplementedError):
        assert not (_destructure.Destructurer(None)(None),)


def test_names(adt, match):
    @adt.adt
    class TestClass:
        StrPair: adt.Ctor[str, str]

    structure = (
        match.pat.tup[1, match.pat.a],
        TestClass.StrPair(match.pat.b, match.pat.c),
    )
    assert match.names(structure) == ["tup", "a", "b", "c"]
