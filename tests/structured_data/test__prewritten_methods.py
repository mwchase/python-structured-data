import pytest


@pytest.fixture(scope="session")
def classes(_adt_constructor, _prewritten_methods):
    class Base(tuple):

        __slots__ = ()

        __repr__ = _prewritten_methods.PrewrittenSumMethods.__repr__
        __eq__ = _prewritten_methods.PrewrittenSumMethods.__eq__
        __ne__ = _prewritten_methods.PrewrittenSumMethods.__ne__
        __lt__ = _prewritten_methods.PrewrittenSumMethods.__lt__
        __le__ = _prewritten_methods.PrewrittenSumMethods.__le__
        __gt__ = _prewritten_methods.PrewrittenSumMethods.__gt__
        __ge__ = _prewritten_methods.PrewrittenSumMethods.__ge__
        __hash__ = _prewritten_methods.PrewrittenSumMethods.__hash__
        __setattr__ = _prewritten_methods.PrewrittenSumMethods.__setattr__
        __delattr__ = _prewritten_methods.PrewrittenSumMethods.__delattr__
        __bool__ = _prewritten_methods.PrewrittenSumMethods.__bool__

    class Derived1(Base):

        __slots__ = ()

        an_attr = None

    class Derived2(Base):

        __slots__ = ()

    Base.__init_subclass__ = _prewritten_methods.PrewrittenSumMethods.__init_subclass__

    for cls in (Derived1, Derived2):
        _adt_constructor.ADT_BASES[cls] = Base

    _prewritten_methods.SUBCLASS_ORDER[Base] = (Derived1, Derived2)

    return Base, Derived1, Derived2


@pytest.fixture(scope="session")
def product_class(_prewritten_methods):
    class Product(tuple):

        __slots__ = ()

        __repr__ = _prewritten_methods.PrewrittenProductMethods.__repr__
        __eq__ = _prewritten_methods.PrewrittenProductMethods.__eq__
        __ne__ = _prewritten_methods.PrewrittenProductMethods.__ne__
        __lt__ = _prewritten_methods.PrewrittenProductMethods.__lt__
        __le__ = _prewritten_methods.PrewrittenProductMethods.__le__
        __gt__ = _prewritten_methods.PrewrittenProductMethods.__gt__
        __ge__ = _prewritten_methods.PrewrittenProductMethods.__ge__
        __hash__ = _prewritten_methods.PrewrittenProductMethods.__hash__
        __setattr__ = _prewritten_methods.PrewrittenProductMethods.__setattr__
        __delattr__ = _prewritten_methods.PrewrittenProductMethods.__delattr__
        __bool__ = _prewritten_methods.PrewrittenProductMethods.__bool__

    return Product


def test_sum_repr(classes):
    assert repr(classes[1]()) == "classes.<locals>.Derived1()"


def test_product_repr(product_class):
    assert repr(product_class()) == "product_class.<locals>.Product()"


def test_sum_eq(classes):
    assert classes[1]() == classes[1]()
    assert not (classes[1]() == classes[2]())


def test_product_eq(product_class):
    assert product_class() == product_class()


def test_sum_ne(classes):
    assert not (classes[1]() != classes[1]())
    assert classes[1]() != classes[2]()
    assert classes[1]() != (True,)


def test_product_ne(product_class):
    assert not (product_class() != product_class())
    assert product_class() != (True,)


def test_sum_lt(classes):
    assert not (classes[1]() < classes[1]())
    assert classes[1]() < classes[2]()
    with pytest.raises(TypeError):
        assert not classes[1]() < (True,)


def test_product_lt(product_class):
    assert not (product_class() < product_class())
    with pytest.raises(TypeError):
        assert not product_class() < (True,)


def test_sum_le(classes):
    assert classes[1]() <= classes[1]()
    assert classes[1]() <= classes[2]()
    with pytest.raises(TypeError):
        assert not classes[1]() <= ()


def test_product_le(product_class):
    assert product_class() <= product_class()
    with pytest.raises(TypeError):
        assert not product_class() <= ()


def test_sum_gt(classes):
    assert not (classes[1]() > classes[1]())
    assert not (classes[1]() > classes[2]())
    with pytest.raises(TypeError):
        # TODO: wait, what?
        assert not not (classes[1]() > (True,))


def test_product_gt(product_class):
    assert not (product_class() > product_class())
    with pytest.raises(TypeError):
        # TODO: wait, what?
        assert not not (product_class() > (True,))


def test_sum_ge(classes):
    assert classes[1]() >= classes[1]()
    assert not (classes[1]() >= classes[2]())
    with pytest.raises(TypeError):
        assert not classes[1]() >= ()


def test_product_ge(product_class):
    assert product_class() >= product_class()
    with pytest.raises(TypeError):
        assert not product_class() >= ()


def test_sum_hash(classes):
    assert hash(classes[1]()) == hash(())


def test_product_hash(product_class):
    assert hash(product_class()) == hash(())


def test_sum_cant_set(classes):
    with pytest.raises(AttributeError):
        classes[1]().attr = None
    with pytest.raises(AttributeError):
        classes[1]().__slots__ = None


def test_product_cant_set(product_class):
    with pytest.raises(AttributeError):
        product_class().attr = None
    with pytest.raises(AttributeError):
        product_class().__slots__ = None


def test_sum_cant_del(classes):
    with pytest.raises(AttributeError):
        del classes[1]().attr


def test_product_cant_del(product_class):
    with pytest.raises(AttributeError):
        del product_class().attr


def test_sum_bool(classes):
    assert classes[1]()


def test_product_bool(product_class):
    assert product_class()


def test_sum_cant_subclass(classes):
    with pytest.raises(TypeError):

        class Test(classes[0]):
            pass


def test_product_can_subclass(product_class):
    class Test(product_class):
        __slots__ = ()

    assert Test
    assert Test()
