import pytest


def test_cant_use_keyword(match):
    with pytest.raises(ValueError):
        assert not match.Pattern('def')


def test_must_be_identifier(match):
    with pytest.raises(ValueError):
        assert not match.Pattern('1')


def test_as(match):
    pat = match.pat.hello
    assert pat @ match.pat._ is pat
    as_pat = pat @ match.pat.world
    assert as_pat.matcher is pat
    assert as_pat.match is match.pat.world


def test_name(match):
    assert match.pat.hello.name == 'hello'
