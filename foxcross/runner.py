import importlib
import inspect
import logging
import sys
from typing import Any, List

import uvicorn
from slugify import slugify
from starlette.applications import Starlette
from starlette.types import ASGIApp

from .endpoints import _index_endpoint
from .exceptions import NoModelServingFoundError

logger = logging.getLogger(__name__)


class ModelServingRunner:
    def __init__(self, base_class: Any, excluded_classes: List):
        self._excluded_classes = excluded_classes
        self._base_class = base_class

    def compose_models_serving(
        self, module_name: str = "models", debug: bool = False
    ) -> ASGIApp:
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
            model_serving = serving_models[0](debug=debug)
        else:
            model_serving = Starlette(debug=debug)
            for asgi_app in serving_models:
                model_serving.mount(
                    f"/{slugify(asgi_app.__name__)}", asgi_app(debug=debug)
                )
            model_serving.add_route("/", _index_endpoint, methods=["GET"])
        return model_serving

    def run_model_serving(self, module_name: str = "models", debug: bool = False):
        asgi_app = self.compose_models_serving(module_name, debug)
        uvicorn.run(asgi_app, debug=debug)
