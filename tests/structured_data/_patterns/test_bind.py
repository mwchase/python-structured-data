def test_bind(match):
    bind = match.Bind(match.pat.a, b=2)
    assert match.names(bind) == ["a", "b"]


def test_binding(match):
    structure = match.Bind(match.pat._, b=1, c=2, a=3)
    assert match.names(structure) == ["b", "c", "a"]
    matchable = match.Matchable(5)
    assert matchable(structure)["b", "c", "a"] == (1, 2, 3)


def test_empty(match):
    assert match.Bind(match.pat._) is match.pat._


def test_no_collide(match):
    structure = match.Bind(match.pat._, structure="hello", args="world", kwargs="!")
    assert match.names(structure) == ["structure", "args", "kwargs"]
    matchable = match.Matchable(5)
    assert matchable(structure)["structure", "args", "kwargs"] == (
        "hello",
        "world",
        "!",
    )
