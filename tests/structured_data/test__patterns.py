import types

import pytest


def test_cant_use_base_compound():
    from structured_data._patterns.compound_match import CompoundMatch

    with pytest.raises(NotImplementedError):
        CompoundMatch().destructure(None)


def test_cant_use_keyword(match):
    with pytest.raises(ValueError):
        assert not match.Pattern("def")


def test_must_be_identifier(match):
    with pytest.raises(ValueError):
        assert not match.Pattern("1")


def test_as(match):
    pat = match.pat.hello
    assert pat[match.pat._] is pat
    as_pat = pat[match.pat.world]
    assert as_pat.matcher is pat
    assert as_pat.match is match.pat.world


def test_name(match):
    assert match.pat.hello.name == "hello"


def test_match_dict_attr(match):
    match_dict = dict(a=1, b=2, c=3)
    assert dict(match.AttrPattern(**match_dict).match_dict) == match_dict


def test_match_dict_dict(match):
    match_dict = dict(a=1, b=2, c=3)
    assert dict(match.DictPattern(match_dict).match_dict) == match_dict


def test_fail_fast(match):
    with pytest.raises(ValueError):
        assert not match.AttrPattern(None)


@pytest.mark.parametrize("exhaustive", [True, False])
def test_exhaustive(match, exhaustive):
    assert match.DictPattern({}, exhaustive=exhaustive).exhaustive == exhaustive


def test_nested_as(match):
    matchable = match.Matchable(5)
    assert matchable(match.pat.a[match.pat.b[match.pat.c]])
    assert matchable["a", "b", "c"] == (5, 5, 5)


def test_bind(match):
    bind = match.Bind(match.pat.a, b=2)
    assert match.names(bind) == ["a", "b"]


def test_mismatched_as(match):
    """One AsPattern should be able to *partially* destructure another."""
    outer = match.pat.outer
    inner = match.pat.inner
    target = outer[inner]
    structure_inside = match.pat.inside
    structure = match.pat.outside[structure_inside]
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
    assert matchable(match.AttrPattern(c=match.pat.d, a=match.pat.e, b=match.pat.f))
    assert tuple(matchable.matches.items()) == (("d", 3), ("e", 1), ("f", 2))
    assert not matchable(match.AttrPattern(test=True))
    assert matchable(match.AttrPattern(a=1))
    assert not matchable(match.AttrPattern(a=1, b=2, c=3, test=True))


def test_mismatched_attr(match):
    matchable = match.Matchable(match.AttrPattern(a=1, b=2, c=3))
    assert not matchable(match.AttrPattern(a=1, b=2, c=3, d=4))
    assert not matchable(match.AttrPattern(b=2, c=3, a=1))


def test_match_nothing_exhaustive(match):
    matchable = match.Matchable(dict(a=1))
    assert not matchable(match.DictPattern({}, exhaustive=True))


def test_binding(match):
    structure = match.Bind(match.pat._, b=1, c=2, a=3)
    assert match.names(structure) == ["b", "c", "a"]
    matchable = match.Matchable(5)
    assert matchable(structure)["b", "c", "a"] == (1, 2, 3)


def test_guard(match):
    matchable = match.Matchable(0)
    assert matchable(match.FALSY)
    assert not matchable(match.TRUTHY)


def test_as_guard(match):
    matchable = match.Matchable(0)
    assert matchable(match.FALSY[match.pat.test])
    assert matchable["test"] == 0
    assert not matchable(match.TRUTHY[match.pat.test])
