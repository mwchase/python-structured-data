import pytest


@pytest.fixture(scope='session')
def classes(_enum_constructor, _prewritten_methods):
    class Base(_prewritten_methods.PrewrittenMethods, tuple):

        __slots__ = ()

    class Derived1(Base):

        __slots__ = ()

        an_attr = None

    class Derived2(Base):

        __slots__ = ()

    for cls in (Derived1, Derived2):
        _enum_constructor.ENUM_BASES[cls] = Base

    _prewritten_methods.SUBCLASS_ORDER[Base] = (Derived1, Derived2)

    return Base, Derived1, Derived2


def test_repr(classes):
    assert repr(classes[1]()) == 'classes.<locals>.Derived1()'


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
