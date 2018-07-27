def test_maybe(data):
    assert data.Maybe.Just(1)
    assert data.Maybe.Nothing()  # No boolean override yet.
    assert data.Maybe.Nothing() != ()


def test_result(data):
    assert data.Either.Left("failed")
    assert data.Either.Right(5)
