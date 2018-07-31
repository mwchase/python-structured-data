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
    assert as_pat.pattern is pat
    assert as_pat.structure is match.pat.world


def test_name(match):
    assert match.pat.hello.name == "hello"


def test_nested_as(match):
    matchable = match.Matchable(5)
    assert matchable(match.pat.a[match.pat.b[match.pat.c]])
    assert matchable["a", "b", "c"] == (5, 5, 5)


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
