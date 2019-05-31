import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.templating import Jinja2Templates

from .enums import MediaTypes
from .exceptions import BadDataFormat

try:
    import ujson as json
    from starlette.responses import UJSONResponse as JSONResponse
except ImportError:
    import json
    from starlette.responses import JSONResponse

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
templates = Jinja2Templates(directory=str(SCRIPT_DIR / "templates"))
logger = logging.getLogger(__name__)


async def _index_endpoint(request: Request) -> Jinja2Templates.TemplateResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "routes": request.app.routes}
    )


async def _kubernetes_liveness_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse("No problems")


async def _kubernetes_readiness_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse("No problems")


class ModelServing(Starlette):
    test_data_path = None

    def __init__(
        self, redirect_https: bool = False, gzip_response: bool = True, **kwargs
    ):
        try:
            test_data = Path(self.test_data_path)
        except TypeError as exc:
            logger.critical(
                f"Problem loading {self.test_data_path}: {exc}. Please make"
                f" sure you have defined your test_data_path on your model serving"
            )
            raise exc
        assert test_data.exists(), f"{self.test_data_path} does not exist"
        super().__init__(**kwargs)
        self.load_model()
        self.add_route("/", _index_endpoint, methods=["GET"])
        self.add_route("/liveness/", _kubernetes_liveness_endpoint, methods=["GET"])
        self.add_route("/readiness/", _kubernetes_readiness_endpoint, methods=["GET"])
        self.add_route("/predict/", self._predict_endpoint, methods=["HEAD", "POST"])
        self.add_route("/predict-test/", self._predict_test_endpoint, methods=["GET"])
        self.add_route("/input-format/", self._input_format_endpoint, methods=["GET"])
        self.add_route("/liveness/", _kubernetes_liveness_endpoint, methods=["GET"])
        self.add_route("/readiness/", _kubernetes_readiness_endpoint, methods=["GET"])
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

    def predict(self, data: Dict) -> Any:
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
                status_code=500, detail=f"Failed to read test data: {exc}"
            )

    async def _predict_endpoint(self, request: Request) -> JSONResponse:
        if request.method == "HEAD":
            return JSONResponse()
        self._validate_http_headers(request, "content-type", self._media_types, 415)
        self._validate_http_headers(request, "accept", self._media_types, 406)
        json_data = await request.json()
        try:
            results = self.predict(json_data)
        except BadDataFormat as exc:
            logger.warning(f"Bad data format inputted to the predict endpoint: {exc}")
            raise HTTPException(status_code=400, detail=str(exc))
        return self._get_json_response(results)

    async def _predict_test_endpoint(self, request: Request) -> JSONResponse:
        self._validate_http_headers(request, "accept", self._media_types, 406)
        test_data = await self._read_test_data()
        results = self.predict(test_data)
        return self._get_json_response(results)

    async def _input_format_endpoint(self, request: Request) -> JSONResponse:
        self._validate_http_headers(request, "accept", self._media_types, 406)
        test_data = await self._read_test_data()
        return self._get_json_response(test_data)

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
    def _get_json_response(data: Any) -> JSONResponse:
        try:
            return JSONResponse(json.dumps(data))
        except TypeError as exc:
            raise HTTPException(
                status_code=500, detail=f"Error trying to serialize data to JSON: {exc}"
            )
