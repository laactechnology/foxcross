from pathlib import Path
from typing import Dict, Union

import pytest
from starlette.testclient import TestClient

from foxcross.enums import MediaTypes
from foxcross.pandas_serving import DataFrameModelServing

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


with Path("data/interpolate.json").open() as f:
    interpolate_data = json.load(f)

with Path("data/interpolate_multi_frame.json").open() as f:
    interpolate_multi_frame_data = json.load(f)

with Path("data/interpolate_result.json").open() as f:
    interpolate_result_data = json.load(f)

with Path("data/interpolate_multi_frame_result.json").open() as f:
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
def test_predict_single_model(model_serving, input_data, expected):
    app = model_serving(debug=True)
    client = TestClient(app)
    response = client.post(
        "/predict/", headers={"Accept": MediaTypes.JSON.value}, json=input_data
    )
    assert response.status_code == 200
    assert response.json() == expected
