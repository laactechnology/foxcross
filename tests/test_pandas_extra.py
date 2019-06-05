import pytest


def test_pandas_extra():
    import pandas  # noqa: F401
    import numpy  # noqa: F401


def test_modin_extra():
    with pytest.raises(ImportError):
        import modin  # noqa: F401


def test_ujson_extra():
    with pytest.raises(ImportError):
        import ujson  # noqa: F401
