from starlette.requests import Request
from starlette.templating import Jinja2Templates

from .templates import templates


async def _index_endpoint(request: Request) -> Jinja2Templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {"request": request})
