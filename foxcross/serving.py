import logging
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.requests import Request

from .endpoints import _index_endpoint
from .enums import MediaTypes
from .exceptions import BadDataFormatError, TestDataPathUndefinedError
from .runner import ModelServingRunner

try:
    import ujson as json
    from starlette.responses import UJSONResponse as JSONResponse
except ImportError:
    import json
    from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class ModelServing(Starlette):
    test_data_path = None

    def __init__(
        self, redirect_https: bool = False, gzip_response: bool = True, **kwargs
    ):
        try:
            test_data = Path(self.test_data_path)
        except TypeError:
            raise TestDataPathUndefinedError(
                f"Problem loading {self.test_data_path}. Please make sure you have"
                f" defined your test_data_path on your model serving"
            )
        assert test_data.exists(), f"{self.test_data_path} does not exist"
        super().__init__(**kwargs)
        self.load_model()
        self.add_route("/", _index_endpoint, methods=["GET"])
        self.add_route("/predict/", self._predict_endpoint, methods=["HEAD", "POST"])
        self.add_route("/predict-test/", self._predict_test_endpoint, methods=["GET"])
        self.add_route("/input-format/", self._input_format_endpoint, methods=["GET"])
        if gzip_response is True:
            self.add_middleware(GZipMiddleware)
        if redirect_https is True:
            self.add_middleware(HTTPSRedirectMiddleware)
        self._media_types = [
            MediaTypes.ANY.value,
            MediaTypes.ANY_APP.value,
            MediaTypes.JSON.value,
        ]

    def load_model(self):
        """Hook to load a model or models"""
        pass

    def predict(self, data: Any) -> Any:
        """
        Method to define how the model performs a prediction.
        Must return JSON serializable data
        """
        raise NotImplementedError(
            "You must implement your model serving's predict method"
        )

    async def _read_test_data(self) -> Dict:
        async with aiofiles.open(self.test_data_path, mode="rb") as f:
            contents = await f.read()
        try:
            return json.loads(contents.decode("utf-8"))
        except TypeError as exc:
            raise HTTPException(
                status_code=500, detail=f"Failed to load test data: {exc}"
            )

    async def _predict_endpoint(self, request: Request) -> JSONResponse:
        if request.method == "HEAD":
            return JSONResponse()
        self._validate_http_headers(request, "content-type", self._media_types, 415)
        self._validate_http_headers(request, "accept", self._media_types, 406)
        json_data = await request.json()
        formatted_data = self._format_input(json_data)
        pre_processed_input = self.pre_process_input(formatted_data)
        try:
            results = self.predict(pre_processed_input)
        except BadDataFormatError as exc:
            logger.warning(f"Bad data format inputted to the predict endpoint: {exc}")
            raise HTTPException(status_code=400, detail=str(exc))
        processed_results = self.post_process_results(results)
        return self._format_output(processed_results)

    async def _predict_test_endpoint(self, request: Request) -> JSONResponse:
        self._validate_http_headers(request, "accept", self._media_types, 406)
        test_data = await self._read_test_data()
        formatted_data = self._format_input(test_data)
        pre_processed_input = self.pre_process_input(formatted_data)
        results = self.predict(pre_processed_input)
        processed_results = self.post_process_results(results)
        return self._format_output(processed_results)

    async def _input_format_endpoint(self, request: Request) -> JSONResponse:
        self._validate_http_headers(request, "accept", self._media_types, 406)
        test_data = await self._read_test_data()
        return self._get_response(test_data)

    @staticmethod
    def _validate_http_headers(
        request: Request, header: str, media_types: List[str], invalid_status_code: int
    ):
        if not request.headers.get(header):
            err_msg = (
                f"Missing http header {header}. Please provide one with an appropriate"
                f" media type. Possible types are {', '.join(media_types)}"
            )
            logger.warning(err_msg)
            raise HTTPException(status_code=400, detail=err_msg)
        elif not any(x in request.headers[header] for x in media_types):
            err_msg = (
                f"Media types {request.headers[header]} in {header} header are not"
                f" supported. Supported types are {', '.join(media_types)}"
            )
            logger.warning(err_msg)
            raise HTTPException(status_code=invalid_status_code, detail=err_msg)

    @staticmethod
    def _get_response(data: Any) -> JSONResponse:
        try:
            return JSONResponse(data)
        except TypeError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Error trying to serialize response data to JSON: {exc}",
            )

    def pre_process_input(self, data: Any) -> Any:
        """Hook to enable pre-processing of input data"""
        return data

    def post_process_results(self, data: Any) -> Any:
        """Hook to enable post-processing of output data"""
        return data

    def _format_input(self, data: Any) -> Any:
        return data

    def _format_output(self, results: Any) -> JSONResponse:
        return self._get_response(results)


_model_serving_runner = ModelServingRunner(ModelServing, [ModelServing])
compose_models_serving = _model_serving_runner.compose_models_serving
run_model_serving = _model_serving_runner.run_model_serving
