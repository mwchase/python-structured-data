def test_dir(option_class):
    dir_result = dir(option_class.Left(1))
    for method in ('__lt__', '__le__', '__gt__', '__ge__'):
        assert (method in dir_result) == option_class.order
