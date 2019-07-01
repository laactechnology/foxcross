import importlib
import inspect
import logging
import re
import sys
from typing import Any, Dict, Tuple

import uvicorn
from slugify import slugify
from starlette.applications import Starlette
from starlette.types import ASGIApp

from .constants import SLUGIFY_REGEX, SLUGIFY_REPLACE
from .endpoints import _index_endpoint
from .exceptions import NoModelServingFoundError

logger = logging.getLogger(__name__)


class ModelServingRunner:
    def __init__(self, base_class: Any, excluded_classes: Tuple):
        self._excluded_classes = excluded_classes
        self._base_class = base_class

    def compose(self, module_name: str = "models", **kwargs) -> ASGIApp:
        try:
            python_module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            err_msg = f"Cannot find Python module named {module_name}: {exc}"
            logger.critical(err_msg)
            raise ModuleNotFoundError(err_msg)
        class_members = inspect.getmembers(sys.modules[module_name], inspect.isclass)
        serving_models = [
            class_
            for _, class_ in class_members
            if issubclass(class_, self._base_class)
            and class_ not in self._excluded_classes
        ]
        if not serving_models:
            raise NoModelServingFoundError(
                f"Could not find any model serving in {python_module}"
            )
        elif len(serving_models) == 1:
            model_serving = serving_models[0](**kwargs)
        else:
            model_serving = Starlette(**kwargs)
            for asgi_app in serving_models:
                slugified_app_name = slugify(
                    re.sub(SLUGIFY_REGEX, SLUGIFY_REPLACE, asgi_app.__name__)
                )
                model_serving.mount(f"/{slugified_app_name}", asgi_app(**kwargs))
            model_serving.add_route("/", _index_endpoint, methods=["GET"])
        return model_serving

    def run_model_serving(
        self,
        module_name: str = "models",
        starlette_kwargs: Dict = None,
        uvicorn_kwargs: Dict = None,
    ):
        if starlette_kwargs is None:
            starlette_kwargs = {}
        if uvicorn_kwargs is None:
            uvicorn_kwargs = {}
        asgi_app = self.compose(module_name, **starlette_kwargs)
        uvicorn.run(asgi_app, **uvicorn_kwargs)
