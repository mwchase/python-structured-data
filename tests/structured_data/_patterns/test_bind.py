def test_bind(match):
    bind = match.Bind(match.pat.a, b=2)
    assert match.names(bind) == ["a", "b"]


def test_binding(match):
    structure = match.Bind(match.pat._, b=1, c=2, a=3)
    assert match.names(structure) == ["b", "c", "a"]
    matchable = match.Matchable(5)
    assert matchable(structure)["b", "c", "a"] == (1, 2, 3)
