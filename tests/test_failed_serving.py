import os
from pathlib import Path
from typing import Any

import pytest
from starlette.testclient import TestClient

from foxcross.enums import MediaTypes
from foxcross.exceptions import NoModelServingFoundError, TestDataPathUndefinedError
from foxcross.runner import ModelServingRunner
from foxcross.serving import ModelServing

from .test_serving import add_one_data_path

__location__ = Path(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
)

bad_data_path = __location__ / "data/bad_data.json"


class NoDataDefined(ModelServing):
    def predict(self, data: Any) -> Any:
        return 1


class DataDoesNotExist(ModelServing):
    test_data_path = "does_not_exist"

    def predict(self, data: Any) -> Any:
        return 1


class BadInputData(ModelServing):
    test_data_path = bad_data_path

    def predict(self, data: Any) -> Any:
        return 1


class PredictMethodNotDefined(ModelServing):
    test_data_path = add_one_data_path


def test_no_test_data_path_defined():
    with pytest.raises(TestDataPathUndefinedError):
        NoDataDefined()


def test_no_model_serving_found_error():
    runner = ModelServingRunner(
        ModelServing,
        (
            ModelServing,
            NoDataDefined,
            DataDoesNotExist,
            PredictMethodNotDefined,
            BadInputData,
        ),
    )
    with pytest.raises(NoModelServingFoundError):
        runner.compose(__name__)


def test_module_not_found_error():
    runner = ModelServingRunner(
        ModelServing,
        (
            ModelServing,
            NoDataDefined,
            DataDoesNotExist,
            PredictMethodNotDefined,
            BadInputData,
        ),
    )
    with pytest.raises(ModuleNotFoundError):
        runner.compose("this_does_not_exist")


def test_test_data_does_not_exist():
    with pytest.raises(AssertionError):
        DataDoesNotExist()


def test_predict_method_not_defined():
    app = PredictMethodNotDefined(debug=True)
    client = TestClient(app)
    with pytest.raises(NotImplementedError):
        client.post("/predict/", headers={"Accept": MediaTypes.JSON.value}, json=1)
    with pytest.raises(NotImplementedError):
        client.get("/predict-test/", headers={"Accept": MediaTypes.JSON.value})


def test_test_data_missing_from_disk(tmpdir):
    data_path = Path(tmpdir / "test_data.json")
    data_path.touch()
    DataDoesNotExist.test_data_path = str(data_path)
    app = DataDoesNotExist(debug=True)
    os.remove(str(data_path))
    client = TestClient(app)
    response = client.get("/input-format/")
    DataDoesNotExist.test_data_path = "does_not_exist"
    assert response.status_code == 500


def test_bad_input_data():
    app = BadInputData(debug=True)
    client = TestClient(app)
    response = client.get("/input-format/")
    assert response.status_code == 500
