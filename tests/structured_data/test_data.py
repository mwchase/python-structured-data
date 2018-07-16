def test_maybe(data):
    assert data.Maybe.Just(1)
    assert data.Maybe.Nothing()  # No boolean override yet.


def test_result(data):
    assert data.Result.Ok(5)
    assert data.Result.Err('failed')
