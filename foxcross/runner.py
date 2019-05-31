import importlib
import inspect
import logging
import sys

import uvicorn
from slugify import slugify
from starlette.applications import Starlette
from starlette.types import ASGIApp

from .base_serving import (
    ModelServing,
    _index_endpoint,
    _kubernetes_liveness_endpoint,
    _kubernetes_readiness_endpoint,
)
from .exceptions import NoServingModelsFoundError
from .pandas_serving import DataFrameModelServing

EXCLUDED_SERVING_CLASSES = [ModelServing, DataFrameModelServing]
logger = logging.getLogger(__name__)


def compose_serving_models(module_name: str = "models", debug: bool = False) -> ASGIApp:
    try:
        python_module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        logger.critical(f"Cannot find Python module named {module_name}: {exc}")
        raise exc
    class_members = inspect.getmembers(sys.modules[module_name], inspect.isclass)
    serving_models = [
        class_
        for _, class_ in class_members
        if issubclass(class_, ModelServing) and class_ not in EXCLUDED_SERVING_CLASSES
    ]
    if not serving_models:
        raise NoServingModelsFoundError(f"Could not find any models in {python_module}")
    elif len(serving_models) == 1:
        model_serving = serving_models[0](debug=debug)
    else:
        model_serving = Starlette(debug=debug)
        for asgi_app in serving_models:
            model_serving.mount(f"/{slugify(asgi_app.__name__)}", asgi_app(debug=debug))
        model_serving.add_route("/", _index_endpoint, methods=["GET"])
        model_serving.add_route(
            "/liveness/", _kubernetes_liveness_endpoint, methods=["GET"]
        )
        model_serving.add_route(
            "/readiness/", _kubernetes_readiness_endpoint, methods=["GET"]
        )
    return model_serving


def run_model_serving(module_name: str = "models", debug: bool = False):
    asgi_app = compose_serving_models(module_name, debug)
    uvicorn.run(asgi_app, debug=debug)
