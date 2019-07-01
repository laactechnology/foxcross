import pytest


def test_pandas_extra():
    with pytest.raises(ImportError):
        import pandas  # noqa: F401


def test_modin_extra():
    with pytest.raises(ImportError):
        import modin  # noqa: F401


def test_ujson_extra():
    with pytest.raises(ImportError):
        import ujson  # noqa: F401


def test_pandas_serving_import():
    with pytest.raises(ImportError):
        from foxcross import pandas_serving  # noqa: F401
