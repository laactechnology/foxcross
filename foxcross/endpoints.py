import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.templating import Jinja2Templates

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
