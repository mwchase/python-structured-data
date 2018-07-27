import pytest


@pytest.fixture(scope="session")
def classes(_adt_constructor, _prewritten_methods):
    class Base(tuple):

        __slots__ = ()

        __repr__ = _prewritten_methods.PrewrittenMethods.__repr__
        __eq__ = _prewritten_methods.PrewrittenMethods.__eq__
        __ne__ = _prewritten_methods.PrewrittenMethods.__ne__
        __lt__ = _prewritten_methods.PrewrittenMethods.__lt__
        __le__ = _prewritten_methods.PrewrittenMethods.__le__
        __gt__ = _prewritten_methods.PrewrittenMethods.__gt__
        __ge__ = _prewritten_methods.PrewrittenMethods.__ge__
        __hash__ = _prewritten_methods.PrewrittenMethods.__hash__
        __setattr__ = _prewritten_methods.PrewrittenMethods.__setattr__
        __delattr__ = _prewritten_methods.PrewrittenMethods.__delattr__
        __bool__ = _prewritten_methods.PrewrittenMethods.__bool__

    class Derived1(Base):

        __slots__ = ()

        an_attr = None

    class Derived2(Base):

        __slots__ = ()

    Base.__init_subclass__ = _prewritten_methods.PrewrittenMethods.__init_subclass__

    for cls in (Derived1, Derived2):
        _adt_constructor.ENUM_BASES[cls] = Base

    _prewritten_methods.SUBCLASS_ORDER[Base] = (Derived1, Derived2)

    return Base, Derived1, Derived2


def test_repr(classes):
    assert repr(classes[1]()) == "classes.<locals>.Derived1()"


def test_eq(classes):
    assert classes[1]() == classes[1]()
    assert not (classes[1]() == classes[2]())


def test_ne(classes):
    assert not (classes[1]() != classes[1]())
    assert classes[1]() != classes[2]()
    assert classes[1]() != (True,)


def test_lt(classes):
    assert not (classes[1]() < classes[1]())
    assert classes[1]() < classes[2]()
    with pytest.raises(TypeError):
        assert not classes[1]() < (True,)


def test_le(classes):
    assert classes[1]() <= classes[1]()
    assert classes[1]() <= classes[2]()
    with pytest.raises(TypeError):
        assert not classes[1]() <= ()


def test_gt(classes):
    assert not (classes[1]() > classes[1]())
    assert not (classes[1]() > classes[2]())
    with pytest.raises(TypeError):
        assert not not (classes[1]() > (True,))


def test_ge(classes):
    assert classes[1]() >= classes[1]()
    assert not (classes[1]() >= classes[2]())
    with pytest.raises(TypeError):
        assert not classes[1]() >= ()


def test_hash(classes):
    assert hash(classes[1]()) == hash(())


def test_cant_set(classes):
    with pytest.raises(AttributeError):
        classes[1]().attr = None
    with pytest.raises(AttributeError):
        classes[1]().__slots__ = None


def test_cant_del(classes):
    with pytest.raises(AttributeError):
        del classes[1]().attr


def test_bool(classes):
    assert classes[1]()


def test_cant_subclass(classes):
    with pytest.raises(TypeError):

        class Test(classes[0]):
            pass
