import types

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


def test_as(match):

    matchable = match.Matchable((1, 2))
    assert not matchable(match.pat.tup @ (match.pat.a, 3))
    assert matchable.matches is None
    structure = match.pat.tup @ (1, match.pat.a)
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
        match.pat.tup @ (1, match.pat.a),
        TestClass.StrPair(match.pat.b, match.pat.c),
    )
    assert match.names(structure) == ["tup", "a", "b", "c"]


def test_mismatched_as(match):
    """One AsPattern should be able to *partially* destructure another."""
    outer = match.pat.outer
    inner = match.pat.inner
    target = outer @ inner
    structure_inside = match.pat.inside
    structure = match.pat.outside @ structure_inside
    matchable = match.Matchable(structure)
    assert matchable(target)
    assert matchable[outer] is structure
    assert matchable[inner] is structure_inside


def test_dict(match):
    matchable = match.Matchable(dict(a=1, b=2, c=3))
    assert matchable(
        match.DictPattern(dict(c=match.pat.d, a=match.pat.e, b=match.pat.f))
    )
    assert tuple(matchable.matches.items()) == (("d", 3), ("e", 1), ("f", 2))
    assert not matchable(match.DictPattern(dict(test=True)))
    assert matchable(match.DictPattern(dict(a=1)))
    assert not matchable(match.DictPattern(dict(a=1), exhaustive=True))
    assert not matchable(match.DictPattern(dict(a=1, b=2, c=3, test=True)))


def test_mismatched_dict(match):
    matchable = match.Matchable(match.DictPattern(dict(a=1, b=2, c=3)))
    assert not matchable(match.DictPattern({}, exhaustive=True))
    assert not matchable(match.DictPattern(dict(a=1, b=2, c=3, d=4)))
    assert not matchable(match.DictPattern(dict(b=2, c=3, a=1)))


def test_attr(match):
    matchable = match.Matchable(types.SimpleNamespace(a=1, b=2, c=3))
    assert matchable(
        match.AttrPattern(dict(c=match.pat.d, a=match.pat.e, b=match.pat.f))
    )
    assert tuple(matchable.matches.items()) == (("d", 3), ("e", 1), ("f", 2))
    assert not matchable(match.AttrPattern(dict(test=True)))
    assert matchable(match.AttrPattern(dict(a=1)))
    assert not matchable(match.AttrPattern(dict(a=1, b=2, c=3, test=True)))


def test_mismatched_attr(match):
    matchable = match.Matchable(match.AttrPattern(dict(a=1, b=2, c=3)))
    assert not matchable(match.AttrPattern(dict(a=1, b=2, c=3, d=4)))
    assert not matchable(match.AttrPattern(dict(b=2, c=3, a=1)))
