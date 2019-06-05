import pytest


def test_pandas_extra():
    import modin  # noqa: F401
    import pandas  # noqa: F401
    import numpy  # noqa: F401


def test_ujson_extra():
    with pytest.raises(ImportError):
        import ujson  # noqa: F401
