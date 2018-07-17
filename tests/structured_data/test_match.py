import pytest


def test_cant_use_keyword(match):
    with pytest.raises(ValueError):
        assert not match.Pattern('def')


def test_must_be_identifier(match):
    with pytest.raises(ValueError):
        assert not match.Pattern('1')


def test_matching(enum, match):

    @enum.enum
    class TestClass:
        StrPair: enum.Ctor[str, str]
    matcher = match.ValueMatcher(
        ((1, 2), TestClass.StrPair('a', 'b')))
    assert not matcher.match((
        (match.pat._, 4),
        match.pat._))
    assert matcher.matches is None
    assert matcher.match((
        match.pat.tup @ (1, match.pat.a),
        TestClass.StrPair(
            match.pat.b, match.pat.c)))
    assert matcher.matches == dict(tup=(1, 2), a=2, b='a', c='b')
    assert matcher.matches[match.pat.a, match.pat.b, match.pat.c, match.pat.tup] == (2, 'a', 'b', (1, 2))


def test_as(match):
    pat = match.pat.hello
    assert pat @ match.pat._ is pat
