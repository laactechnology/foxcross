import os
from pathlib import Path

from starlette.templating import Jinja2Templates

from .filters import has_attr

__location__ = Path(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
)
templates = Jinja2Templates(directory=str(__location__ / "templates"))
templates.env.filters["has_attr"] = has_attr
