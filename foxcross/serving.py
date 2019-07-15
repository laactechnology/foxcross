import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Union

import aiofiles
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from .constants import SLUGIFY_REGEX, SLUGIFY_REPLACE
from .endpoints import _index_endpoint
from .enums import MediaTypes
from .exceptions import (
    PostProcessingError,
    PredictionError,
    PreProcessingError,
    TestDataPathUndefinedError,
)
from .runner import ModelServingRunner
from .templates import templates

try:
    import ujson as json
    from starlette.responses import UJSONResponse as JSONResponse
except ImportError:
    import json
    from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class ModelServing(Starlette):
    test_data_path = None
    model_name = None
    _download_format_options = (MediaTypes.JSON,)

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
        self.add_route("/predict/", self._predict_endpoint, methods=["GET", "POST"])
        self.add_route(
            "/predict-test/", self._predict_test_endpoint, methods=["GET", "POST"]
        )
        self.add_route(
            "/input-format/", self._input_format_endpoint, methods=["GET", "POST"]
        )
        if gzip_response is True:
            self.add_middleware(GZipMiddleware)
        if redirect_https is True:
            self.add_middleware(HTTPSRedirectMiddleware)
        if self.model_name is None:
            self.model_name = re.sub(
                SLUGIFY_REGEX, SLUGIFY_REPLACE, self.__class__.__name__
            )

    def load_model(self):
        """Hook to load a model or models"""
        pass

    def predict(self, data: Any) -> Any:
        """
        Method to define how the model performs a prediction.
        Must return JSON serializable data
        """
        raise NotImplementedError(
            "You must implement your model serving's predict method and it must return"
            " JSON serializable data"
        )

    async def _read_test_data(self) -> Any:
        try:
            async with aiofiles.open(self.test_data_path, mode="rb") as f:
                contents = await f.read()
        except FileNotFoundError:
            err_msg = f"Error reading {self.test_data_path}"
            logger.exception(err_msg)
            raise HTTPException(status_code=500, detail=err_msg)
        try:
            return json.loads(contents.decode("utf-8"))
        except (TypeError, ValueError):
            err_msg = f"Failed to load test data into JSON"
            logger.exception(err_msg)
            raise HTTPException(status_code=500, detail=err_msg)

    async def _predict_endpoint(
        self, request: Request
    ) -> Union[JSONResponse, Jinja2Templates.TemplateResponse]:
        if request.method == "GET":
            self._validate_http_headers(
                request, "accept", MediaTypes.html_media_types(), 406
            )
            return templates.TemplateResponse("predict.html", {"request": request})
        elif request.method == "POST":
            self._validate_http_headers(
                request, "accept", MediaTypes.json_media_types(), 406
            )
            self._validate_http_headers(
                request, "content-type", MediaTypes.json_media_types(), 415
            )
            json_data = await request.json()
            formatted_data = self._format_input(json_data)
            processed_results = self._process_prediction(formatted_data)
            formatted_output = self._format_output(processed_results)
            return self._get_json_response(formatted_output)

    async def _predict_test_endpoint(
        self, request: Request
    ) -> Union[JSONResponse, Jinja2Templates.TemplateResponse]:
        if request.method == "GET":
            self._validate_http_headers(
                request, "accept", MediaTypes.html_media_types(), 406
            )
        elif request.method == "POST":
            self._validate_http_headers(
                request, "accept", MediaTypes.json_media_types(), 406
            )
        test_data = await self._read_test_data()
        formatted_data = self._format_input(test_data)
        processed_results = self._process_prediction(formatted_data)
        formatted_output = self._format_output(processed_results)
        if request.method == "GET":
            return templates.TemplateResponse(
                "predict_test.html",
                {
                    "request": request,
                    "data_format_options": self._download_format_options,
                    "output_data": formatted_output,
                },
            )
        elif request.method == "POST":
            return self._get_json_response(
                formatted_output,
                extra_headers={
                    "Content-Disposition": "attachment; filename=predict-output.json"
                },
            )

    def _process_prediction(self, formatted_data):
        try:
            pre_processed_input = self.pre_process_input(formatted_data)
        except PreProcessingError as exc:
            logger.warning(str(exc))
            raise HTTPException(status_code=exc.http_status_code, detail=str(exc))
        try:
            results = self.predict(pre_processed_input)
        except PredictionError as exc:
            logger.warning(str(exc))
            raise HTTPException(status_code=exc.http_status_code, detail=str(exc))
        try:
            processed_results = self.post_process_results(results)
        except PostProcessingError as exc:
            logger.warning(str(exc))
            raise HTTPException(status_code=exc.http_status_code, detail=str(exc))
        return processed_results

    async def _input_format_endpoint(
        self, request: Request
    ) -> Union[JSONResponse, Jinja2Templates.TemplateResponse]:
        if request.method == "GET":
            self._validate_http_headers(
                request, "accept", MediaTypes.html_media_types(), 406
            )
        elif request.method == "POST":
            self._validate_http_headers(
                request, "accept", MediaTypes.json_media_types(), 406
            )
        test_data = await self._read_test_data()
        if request.method == "GET":
            return templates.TemplateResponse(
                "input_format.html",
                {
                    "request": request,
                    "data_format_options": self._download_format_options,
                    "output_data": test_data,
                },
            )
        elif request.method == "POST":
            return self._get_json_response(
                test_data,
                extra_headers={
                    "Content-Disposition": "attachment; filename=input-format.json"
                },
            )

    @staticmethod
    def _validate_http_headers(
        request: Request,
        header: str,
        media_types: Iterable[str],
        invalid_status_code: int,
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
    def _get_json_response(
        data: Any, extra_headers: Dict[str, str] = None
    ) -> JSONResponse:
        try:
            if extra_headers:
                return JSONResponse(data, headers=extra_headers)
            else:
                return JSONResponse(data)
        except (TypeError, ValueError):
            err_msg = f"Error trying to serialize response data to JSON"
            logger.exception(err_msg)
            raise HTTPException(status_code=500, detail=err_msg)

    def pre_process_input(self, data: Any) -> Any:
        """Hook to enable pre-processing of input data"""
        return data

    def post_process_results(self, data: Any) -> Any:
        """Hook to enable post-processing of output data"""
        return data

    def _format_input(self, data: Any) -> Any:
        return data

    def _format_output(self, results: Any) -> Any:
        return results


_model_serving_runner = ModelServingRunner(ModelServing, (ModelServing,))
compose_models = _model_serving_runner.compose
run_model_serving = _model_serving_runner.run_model_serving
