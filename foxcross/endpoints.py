import os
from pathlib import Path

from starlette.requests import Request
from starlette.templating import Jinja2Templates

__location__ = Path(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
)
templates = Jinja2Templates(directory=str(__location__ / "templates"))


async def _index_endpoint(request: Request) -> Jinja2Templates.TemplateResponse:
    mounts = []
    routes = []
    for obj in request.scope["router"].routes:
        if hasattr(obj, "routes"):
            mounts.append(obj)
        elif hasattr(obj, "path"):
            routes.append(obj)
    return templates.TemplateResponse(
        "index.html", {"request": request, "mounts": mounts, "routes": routes}
    )
