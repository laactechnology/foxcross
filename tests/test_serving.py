import os
from pathlib import Path
from typing import Any

import pytest
from slugify import slugify
from starlette.testclient import TestClient

from foxcross.enums import MediaTypes
from foxcross.serving import ModelServing, compose_models_serving

try:
    import ujson as json
except ImportError:
    import json

__location__ = Path(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
)

add_one_data_path = __location__ / "data/add_one.json"
add_five_data_path = __location__ / "data/add_five.json"

with Path(add_one_data_path).open() as f:
    add_one_data = json.load(f)

with Path(__location__ / "data/add_one_result.json").open() as f:
    add_one_result_data = json.load(f)

with Path(add_one_data_path).open() as f:
    add_five_data = json.load(f)

with Path(__location__ / "data/add_five_result.json").open() as f:
    add_five_result_data = json.load(f)


class AddOneModel(ModelServing):
    test_data_path = add_one_data_path

    def predict(self, data: Any) -> Any:
        return [x + 1 for x in data]


class AddAnyModel:
    def __init__(self, add_amount):
        self._add_amount = add_amount

    def add(self, data):
        return [x + self._add_amount for x in data]


class AddFiveModel(ModelServing):
    test_data_path = add_five_data_path

    def load_model(self):
        self.model = AddAnyModel(5)

    def predict(self, data: Any) -> Any:
        return self.model.add(data)


@pytest.mark.parametrize(
    "model_serving,input_data,expected,endpoint",
    [
        (AddOneModel, add_one_data, add_one_result_data, "/predict/"),
        (AddFiveModel, add_five_data, add_five_result_data, "/predict/"),
        (AddOneModel, None, add_one_data, "/input-format/"),
        (AddFiveModel, None, add_five_data, "/input-format/"),
        (AddOneModel, add_one_data, add_one_result_data, "/predict-test/"),
        (AddFiveModel, add_five_data, add_five_result_data, "/predict-test/"),
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


def test_index_single_model_serving():
    app = AddOneModel(debug=True)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_predict_multi_model_serving():
    app = compose_models_serving(__name__, debug=True)
    client = TestClient(app)
    add_one_response = client.post(
        f"{slugify(AddOneModel.__name__)}/predict/",
        headers={"Accept": MediaTypes.JSON.value},
        json=add_one_data,
    )
    assert add_one_response.status_code == 200
    assert add_one_response.json() == add_one_result_data

    add_five_response = client.post(
        f"{slugify(AddFiveModel.__name__)}/predict/",
        headers={"Accept": MediaTypes.JSON.value},
        json=add_five_data,
    )
    assert add_five_response.status_code == 200
    assert add_five_response.json() == add_five_result_data


def test_index_multi_model_serving():
    app = compose_models_serving(__name__, debug=True)
    client = TestClient(app)
    add_one_response = client.get(f"{slugify(AddOneModel.__name__)}/")
    assert add_one_response.status_code == 200

    add_five_response = client.get(f"{slugify(AddFiveModel.__name__)}/")
    assert add_five_response.status_code == 200

    root_response = client.get("/")
    assert root_response.status_code == 200


@pytest.mark.parametrize(
    "endpoint,first_expected,second_expected",
    [
        ("/input-format/", add_one_data, add_five_data),
        ("/predict-test/", add_one_data, add_five_data),
    ],
)
def test_endpoints_multi_model_serving(endpoint, first_expected, second_expected):
    app = compose_models_serving(__name__, debug=True)
    client = TestClient(app)
    add_one_response = client.get(
        f"{slugify(AddOneModel.__name__)}{endpoint}",
        headers={"Accept": MediaTypes.JSON.value},
    )
    assert add_one_response.status_code == 200
    assert add_one_response.json() == first_expected

    add_five_response = client.get(
        f"{slugify(AddFiveModel.__name__)}{endpoint}",
        headers={"Accept": MediaTypes.JSON.value},
    )
    assert add_five_response.status_code == 200
    assert add_five_response.json() == second_expected
