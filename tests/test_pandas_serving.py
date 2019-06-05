import os
from pathlib import Path
from typing import Dict, Union

import pytest
from slugify import slugify
from starlette.testclient import TestClient

from foxcross.enums import MediaTypes
from foxcross.pandas_serving import DataFrameModelServing, compose_serving_pandas

try:
    import modin.pandas as pandas
except ImportError:
    try:
        import pandas
    except ImportError:
        raise ImportError(
            f"Cannot import pandas. Please install foxcross using foxcross[pandas] or"
            f" foxcross[modin]"
        )

try:
    import ujson as json
except ImportError:
    import json

__location__ = Path(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
)


with Path(__location__ / "data/interpolate.json").open() as f:
    interpolate_data = json.load(f)

with Path(__location__ / "data/interpolate_multi_frame.json").open() as f:
    interpolate_multi_frame_data = json.load(f)

with Path(__location__ / "data/interpolate_result.json").open() as f:
    interpolate_result_data = json.load(f)

with Path(__location__ / "data/interpolate_multi_frame_result.json").open() as f:
    interpolate_multi_frame_result_data = json.load(f)


class InterpolateModel:
    def __init__(self, direction: str):
        self._direction = direction

    def interpolate(self, data: pandas.DataFrame) -> pandas.DataFrame:
        return data.interpolate(limit_direction=self._direction)


class InterpolateModelServing(DataFrameModelServing):
    test_data_path = "data/interpolate.json"

    def load_model(self):
        self.model = InterpolateModel("both")

    def predict(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        return self.model.interpolate(data)


class InterpolateMultiFrameModelServing(DataFrameModelServing):
    test_data_path = "data/interpolate.json"

    def load_model(self):
        self.model = InterpolateModel("forward")

    def predict(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        return {key: self.model.interpolate(value) for key, value in data.items()}


@pytest.mark.parametrize(
    "model_serving,input_data,expected",
    [
        (InterpolateModelServing, interpolate_data, interpolate_result_data),
        (
            InterpolateMultiFrameModelServing,
            interpolate_multi_frame_data,
            interpolate_multi_frame_result_data,
        ),
    ],
)
def test_predict_single_model_serving(model_serving, input_data, expected):
    app = model_serving(debug=True)
    client = TestClient(app)
    response = client.post(
        "/predict/", headers={"Accept": MediaTypes.JSON.value}, json=input_data
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_predict_multi_model_serving():
    app = compose_serving_pandas(__name__, debug=True)
    client = TestClient(app)
    response = client.post(
        f"{slugify(InterpolateModelServing.__name__)}/predict/",
        headers={"Accept": MediaTypes.JSON.value},
        json=interpolate_data,
    )
    assert response.status_code == 200
    assert response.json() == interpolate_result_data

    multi_response = client.post(
        f"{slugify(InterpolateMultiFrameModelServing.__name__)}/predict/",
        headers={"Accept": MediaTypes.JSON.value},
        json=interpolate_multi_frame_data,
    )
    assert multi_response.status_code == 200
    assert multi_response.json() == interpolate_multi_frame_result_data
