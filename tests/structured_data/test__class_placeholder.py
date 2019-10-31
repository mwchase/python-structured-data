def test_method(adt, match):
    @match.Placeholder
    def left_number(cls):
        return cls.Left(match.pat.number)

    @match.Placeholder
    def right_string(cls):
        return cls.Right(match.pat.string)

    class TestEither(adt.Sum):
        Left: adt.Ctor[int]
        Right: adt.Ctor[str]

        @match.function
        def invert(self):
            """Reverse the the object according to some criteria."""

        @invert.when(self=left_number)
        def __negate(number):
            return TestEither.Left(-number)

        @invert.when(self=right_string)
        def __reverse(string):
            return TestEither.Right(string[::-1])

    assert TestEither.Left(10).invert() == TestEither.Left(-10)
    assert TestEither.Right("abc").invert() == TestEither.Right("cba")
    assert TestEither.invert(TestEither.Left(5)) == TestEither.Left(-5)
