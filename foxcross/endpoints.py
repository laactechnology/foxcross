import os
from pathlib import Path

from starlette.requests import Request
from starlette.templating import Jinja2Templates

SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
templates = Jinja2Templates(directory=str(SCRIPT_DIR / "templates"))


async def _index_endpoint(request: Request) -> Jinja2Templates.TemplateResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "routes": request.app.routes}
    )
