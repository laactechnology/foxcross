import os
import re
from pathlib import Path
from typing import Dict, Union

import pytest
from slugify import slugify
from starlette.testclient import TestClient

from foxcross.constants import SLUGIFY_REGEX, SLUGIFY_REPLACE
from foxcross.enums import MediaTypes
from foxcross.pandas_serving import DataFrameModelServing, compose_pandas

from .test_serving import AddOneModel, add_one_data, add_one_result_data

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


class PredictMethodNotDefined(DataFrameModelServing):
    test_data_path = interpolate_data_path


class FormatOutputAttributeError(DataFrameModelServing):
    test_data_path = interpolate_data_path

    def predict(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        return {"hi": "there", "my": "friend"}


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
    response = client.post(
        endpoint, headers={"Accept": MediaTypes.JSON.value}, json=input_data
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_index_single_model_serving():
    app = InterpolateMultiFrameModelServing(debug=True)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_predict_multi_model_serving():
    app = compose_pandas(__name__, debug=True)
    client = TestClient(app)
    interp_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateModelServing.__name__)
    )
    response = client.post(
        f"{interp_slugified}/predict/",
        headers={"Accept": MediaTypes.JSON.value},
        json=interpolate_data,
    )
    assert response.status_code == 200
    assert response.json() == interpolate_result_data

    multi_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateMultiFrameModelServing.__name__)
    )
    multi_response = client.post(
        f"{multi_slugified}/predict/",
        headers={"Accept": MediaTypes.JSON.value},
        json=interpolate_multi_frame_data,
    )
    assert multi_response.status_code == 200
    assert multi_response.json() == interpolate_multi_frame_result_data


def test_index_multi_model_serving():
    app = compose_pandas(__name__, debug=True)
    client = TestClient(app)

    interp_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateModelServing.__name__)
    )
    response = client.get(f"{interp_slugified}/")
    assert response.status_code == 200

    multi_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateMultiFrameModelServing.__name__)
    )
    multi_response = client.get(f"{multi_slugified}/")
    assert multi_response.status_code == 200

    root_response = client.get("/")
    assert root_response.status_code == 200


@pytest.mark.parametrize(
    "endpoint,first_expected,second_expected,third_expected",
    [
        ("/input-format/", interpolate_data, interpolate_multi_frame_data, add_one_data),
        (
            "/predict-test/",
            interpolate_result_data,
            interpolate_multi_frame_result_data,
            add_one_result_data,
        ),
    ],
)
def test_endpoints_multi_model_serving(
    endpoint, first_expected, second_expected, third_expected
):
    app = compose_pandas(__name__, debug=True)
    client = TestClient(app)

    interp_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateModelServing.__name__)
    )
    response = client.post(
        f"{interp_slugified}{endpoint}", headers={"Accept": MediaTypes.JSON.value}
    )
    assert response.status_code == 200
    assert response.json() == first_expected

    multi_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateMultiFrameModelServing.__name__)
    )
    multi_response = client.post(
        f"{multi_slugified}{endpoint}", headers={"Accept": MediaTypes.JSON.value}
    )
    assert multi_response.status_code == 200
    assert multi_response.json() == second_expected

    add_one_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, AddOneModel.__name__)
    )
    add_one_response = client.post(
        f"{add_one_slugified}{endpoint}", headers={"Accept": MediaTypes.JSON.value}
    )
    assert add_one_response.status_code == 200
    assert add_one_response.json() == third_expected


def test_predict_method_not_defined():
    app = PredictMethodNotDefined(debug=True)
    client = TestClient(app)
    with pytest.raises(NotImplementedError):
        client.post(
            "/predict/", headers={"Accept": MediaTypes.JSON.value}, json=interpolate_data
        )
    with pytest.raises(NotImplementedError):
        client.post("/predict-test/", headers={"Accept": MediaTypes.JSON.value})


def test_predict_input_issue():
    app = InterpolateMultiFrameModelServing(debug=True)
    client = TestClient(app)
    multi_response = client.post(
        "/predict/", headers={"Accept": MediaTypes.JSON.value}, json=[]
    )
    assert multi_response.status_code == 400


@pytest.mark.parametrize("endpoint", ["/predict/", "/predict-test/", "/input-format/"])
def test_single_model_html_responses(endpoint):
    app = InterpolateMultiFrameModelServing(debug=True)
    client = TestClient(app)
    response = client.get(endpoint, headers={"Accept": MediaTypes.HTML.value})
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", ["/predict/", "/predict-test/", "/input-format/"])
def test_multi_model_html_responses(endpoint):
    app = compose_pandas(__name__, debug=True)
    client = TestClient(app)

    interp_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateModelServing.__name__)
    )
    response = client.get(
        f"{interp_slugified}{endpoint}", headers={"Accept": MediaTypes.HTML.value}
    )
    assert response.status_code == 200

    multi_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, InterpolateMultiFrameModelServing.__name__)
    )
    multi_response = client.get(
        f"{multi_slugified}{endpoint}", headers={"Accept": MediaTypes.HTML.value}
    )
    assert multi_response.status_code == 200

    add_one_slugified = slugify(
        re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, AddOneModel.__name__)
    )
    add_one_response = client.get(
        f"{add_one_slugified}{endpoint}", headers={"Accept": MediaTypes.HTML.value}
    )
    assert add_one_response.status_code == 200


def test_format_output_attribute_error():
    app = FormatOutputAttributeError(debug=True)
    client = TestClient(app)
    response = client.get("/predict-test/")
    assert response.status_code == 500
