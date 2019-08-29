import typing

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


def test_subclassing(match):
    class NT(typing.NamedTuple):
        fst: int
        snd: str

    tup = (1, "abc")
    n_tup = NT(1, "abc")

    t_matchable = match.Matchable(tup)
    nt_matchable = match.Matchable(n_tup)

    assert nt_matchable(tup)
    assert nt_matchable(n_tup)
    assert t_matchable(tup)
    assert not t_matchable(n_tup)


def test_adt(adt, match):
    class TestClass(adt.Sum):
        StrPair: adt.Ctor[str, str]
        Str: adt.Ctor[str]

    matchable = match.Matchable(TestClass.StrPair("a", "b"))
    tuple_matchable = match.Matchable(("a", "b"))
    assert not matchable(TestClass.Str("c"))
    assert matchable.matches is None
    structure = TestClass.StrPair(match.pat.a, match.pat.b)
    assert matchable(structure)
    assert not tuple_matchable(TestClass.StrPair("a", "b"))
    assert not matchable(("a", "b"))


def test_cant_use_base_processor():
    from structured_data import _destructure

    with pytest.raises(NotImplementedError):
        assert not (_destructure.Destructurer(None)(None),)


def test_names(adt, match):
    class TestClass(adt.Sum):
        StrPair: adt.Ctor[str, str]

    structure = (
        match.pat.tup[1, match.pat.a],
        TestClass.StrPair(match.pat.b, match.pat.c),
    )
    assert match.names(structure) == ["tup", "a", "b", "c"]
