from typing import Any

import pytest
from starlette.testclient import TestClient

from foxcross.enums import MediaTypes
from foxcross.exceptions import NoModelServingFoundError, TestDataPathUndefinedError
from foxcross.runner import ModelServingRunner
from foxcross.serving import ModelServing

from .test_serving import add_one_data_path


class NoTestDataDefined(ModelServing):
    def predict(self, data: Any) -> Any:
        return 1


class TestDataDoesNotExist(ModelServing):
    test_data_path = "does_not_exist"

    def predict(self, data: Any) -> Any:
        return 1


class PredictMethodNotDefined(ModelServing):
    test_data_path = add_one_data_path


def test_no_test_data_path_defined():
    with pytest.raises(TestDataPathUndefinedError):
        NoTestDataDefined()


def test_no_model_serving_found_error():
    runner = ModelServingRunner(
        ModelServing,
        [ModelServing, NoTestDataDefined, TestDataDoesNotExist, PredictMethodNotDefined],
    )
    with pytest.raises(NoModelServingFoundError):
        runner.compose(__name__)


def test_module_not_found_error():
    runner = ModelServingRunner(
        ModelServing,
        [ModelServing, NoTestDataDefined, TestDataDoesNotExist, PredictMethodNotDefined],
    )
    with pytest.raises(ModuleNotFoundError):
        runner.compose("this_does_not_exist")


def test_test_data_does_not_exist():
    with pytest.raises(AssertionError):
        TestDataDoesNotExist()


def test_predict_method_not_defined():
    app = PredictMethodNotDefined(debug=True)
    client = TestClient(app)
    with pytest.raises(NotImplementedError):
        client.post("/predict/", headers={"Accept": MediaTypes.JSON.value}, json=1)
    with pytest.raises(NotImplementedError):
        client.get("/predict-test/", headers={"Accept": MediaTypes.JSON.value})
