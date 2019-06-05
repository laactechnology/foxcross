import os
from pathlib import Path
from typing import Dict, Union

import pytest
from slugify import slugify
from starlette.testclient import TestClient

from foxcross.enums import MediaTypes
from foxcross.pandas_serving import DataFrameModelServing, compose_pandas_serving
from foxcross.serving import ModelServing

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

interpolate_data_path = __location__ / "data/interpolate.json"
interpolate_multi_frame_data_path = __location__ / "data/interpolate_multi_frame.json"

with Path(interpolate_data_path).open() as f:
    interpolate_data = json.load(f)

with Path(interpolate_multi_frame_data_path).open() as f:
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
    test_data_path = interpolate_data_path

    def load_model(self):
        self.model = InterpolateModel("both")

    def predict(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        return self.model.interpolate(data)


class InterpolateMultiFrameModelServing(DataFrameModelServing):
    test_data_path = interpolate_multi_frame_data_path

    def load_model(self):
        self.model = InterpolateModel("forward")

    def predict(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        return {key: self.model.interpolate(value) for key, value in data.items()}


class AddOneModel(ModelServing):
    test_data_path = "data.json"

    def predict(self, data):
        return [x + 1 for x in data]


@pytest.mark.parametrize(
    "model_serving,input_data,expected,endpoint",
    [
        (InterpolateModelServing, interpolate_data, interpolate_result_data, "/predict/"),
        (
            InterpolateMultiFrameModelServing,
            interpolate_multi_frame_data,
            interpolate_multi_frame_result_data,
            "/predict/",
        ),
        (InterpolateModelServing, None, interpolate_data, "/input-format/"),
        (
            InterpolateMultiFrameModelServing,
            None,
            interpolate_multi_frame_data,
            "/input-format/",
        ),
        (
            InterpolateModelServing,
            interpolate_data,
            interpolate_result_data,
            "/predict-test/",
        ),
        (
            InterpolateMultiFrameModelServing,
            interpolate_multi_frame_data,
            interpolate_multi_frame_result_data,
            "/predict-test/",
        ),
    ],
)
def test_endpoints_single_model_serving(model_serving, input_data, expected, endpoint):
    app = model_serving(debug=True)
    client = TestClient(app)
    if endpoint == "/predict/":
        response = client.post(
            endpoint, headers={"Accept": MediaTypes.JSON.value}, json=input_data
        )
    else:
        response = client.get(endpoint, headers={"Accept": MediaTypes.JSON.value})
    assert response.status_code == 200
    assert response.json() == expected


def test_predict_multi_model_serving():
    app = compose_pandas_serving(__name__, debug=True)
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


@pytest.mark.parametrize(
    "endpoint,first_expected,second_expected",
    [
        ("/input-format/", interpolate_data, interpolate_multi_frame_data),
        ("/predict-test/", interpolate_result_data, interpolate_multi_frame_result_data),
    ],
)
def test_endpoints_multi_model_serving(endpoint, first_expected, second_expected):
    app = compose_pandas_serving(__name__, debug=True)
    client = TestClient(app)
    response = client.get(
        f"{slugify(InterpolateModelServing.__name__)}{endpoint}",
        headers={"Accept": MediaTypes.JSON.value},
    )
    assert response.status_code == 200
    assert response.json() == first_expected

    multi_response = client.get(
        f"{slugify(InterpolateMultiFrameModelServing.__name__)}{endpoint}",
        headers={"Accept": MediaTypes.JSON.value},
    )
    assert multi_response.status_code == 200
    assert multi_response.json() == second_expected
