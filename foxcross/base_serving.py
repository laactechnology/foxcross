import os
from pathlib import Path

import aiofiles
from starlette.applications import Starlette
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.templating import Jinja2Templates

try:
    import ujson as json
    from starlette.responses import UJSONResponse as JSONResponse
except ImportError:
    import json
    from starlette.responses import JSONResponse

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
templates = Jinja2Templates(directory=str(SCRIPT_DIR / "templates"))


async def _index_endpoint(request: Request) -> Jinja2Templates.TemplateResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "routes": request.app.routes}
    )


async def _kubernetes_liveness_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse("No problems")


async def _kubernetes_readiness_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse("No problems")


class ModelServing(Starlette):
    def __init__(
        self, redirect_https: bool = False, gzip_response: bool = True, **kwargs
    ):
        super().__init__(**kwargs)
        self.add_route("/", _index_endpoint, methods=["GET"])
        self.add_route("/liveness", _kubernetes_liveness_endpoint, methods=["GET"])
        self.add_route("/readiness", _kubernetes_readiness_endpoint, methods=["GET"])
        self.add_route("/predict", self._predict_endpoint, methods=["HEAD", "POST"])
        if gzip_response is True:
            self.add_middleware(GZipMiddleware)
        if redirect_https is True:
            self.add_middleware(HTTPSRedirectMiddleware)

    async def _read_test_data(self):
        async with aiofiles.open(self.test_data_path, mode="rb") as f:
            contents = await f.read()
        return json.loads(contents.decode("utf-8"))

    async def _predict_endpoint(self, request: Request) -> JSONResponse:
        if request.method == "HEAD":
            return JSONResponse()
        return JSONResponse({"message": "we're good"})
