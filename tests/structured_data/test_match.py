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
    structure = (
        match.pat.tup @ (1, match.pat.a),
        TestClass.StrPair(
            match.pat.b, match.pat.c))
    assert matcher.match(structure)
    assert matcher.matches == dict(tup=(1, 2), a=2, b='a', c='b')
    assert matcher.matches[match.pat.a, match.pat.b, match.pat.c, match.pat.tup] == (2, 'a', 'b', (1, 2))
    assert list(matcher.matches) == ['tup', 'a', 'b', 'c']  # Should preserve ordering.
    assert match.names(structure) == ['tup', 'a', 'b', 'c']


def test_as(match):
    pat = match.pat.hello
    assert pat @ match.pat._ is pat


def test_map_interface(match):
    matcher = match.ValueMatcher((1, 2, 3, 4))
    matcher.match((match.pat.a, match.pat._, match.pat._, match.pat.b))
    assert len(matcher.matches) == 2
    with pytest.raises(KeyError):
        assert not matcher.matches[None]

    matcher.matches[match.pat.c] = 7
    del matcher.matches[match.pat.c]

    with pytest.raises(TypeError):
        matcher.matches[None] = None

    with pytest.raises(KeyError):
        del matcher.matches[None]
