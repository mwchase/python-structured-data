import types

import pytest


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
