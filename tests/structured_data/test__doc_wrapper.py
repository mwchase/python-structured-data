def test_property_is_mostly_immutable(match):
    prop = match.function(property(doc="Hi!"))
    assert prop.__doc__ == "Hi!"
    prop.__doc__ = "Bye!"
    assert prop.__doc__ == "Bye!"
    del prop.__doc__
    assert prop.__doc__ is None

    @prop.getter
    def prop2(self):
        """I'm a docstring!"""

    assert prop2.__doc__ == "I'm a docstring!"


def test_proxy_doc(match):

    class Base:
        @match.function
        @property
        def prop(self):
            """Docstring."""

    class Test(Base):
        pass

    assert Test.prop.__doc__ == "Docstring."
