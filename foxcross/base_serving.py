import os
from pathlib import Path
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.applications import Starlette
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
try:
    import ujson as json
    from starlette.responses import UJSONResponse as JSONResponse
except ImportError:
    import json
    from starlette.responses import JSONResponse

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
templates = Jinja2Templates(directory=str(SCRIPT_DIR / "templates"))


async def _index_endpoint(request: Request) -> Jinja2Templates.TemplateResponse:
    return templates.TemplateResponse("index.html",
                                      {"request": request, "routes": request.app.routes})


async def _kubernetes_liveness_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse("No problems")


async def _kubernetes_readiness_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse("No problems")


class ModelServing(Starlette):
    def __init__(self, redirect_https: bool = False, gzip_response: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.add_route("/", _index_endpoint, methods=["GET"])
        self.add_route("/liveness", _kubernetes_liveness_endpoint, methods=["GET"])
        self.add_route("/readiness", _kubernetes_readiness_endpoint, methods=["GET"])
        if gzip_response is True:
            self.add_middleware(GZipMiddleware)
        if redirect_https is True:
            self.add_middleware(HTTPSRedirectMiddleware)
