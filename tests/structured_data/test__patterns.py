import pytest


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
