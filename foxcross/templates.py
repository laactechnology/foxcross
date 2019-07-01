import os
from pathlib import Path

from starlette.templating import Jinja2Templates

__location__ = Path(
    os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
)
templates = Jinja2Templates(directory=str(__location__ / "templates"))
templates.env.filters["hasattr"] = hasattr
