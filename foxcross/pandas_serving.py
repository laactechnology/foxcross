import logging
from typing import Dict, Union

from starlette.exceptions import HTTPException

from .runner import ModelServingRunner
from .serving import ModelServing

logger = logging.getLogger(__name__)
try:
    import modin.pandas as pandas
except ImportError:
    try:
        import pandas
    except ImportError:
        raise ImportError(
            f"Cannot import pandas. Please install foxcross using foxcross[pandas] or"
            f" foxcross[modin]"
        )

try:
    import ujson as json
    from starlette.responses import UJSONResponse as JSONResponse
except ImportError:
    import json  # noqa: F401
    from starlette.responses import JSONResponse


class DataFrameModelServing(ModelServing):
    # TODO: probably should limit which choices are available for orient since to_dict and
    # to_json differ
    pandas_orient = "index"

    def predict(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        """
        Method to define how the model performs a prediction.
        Must return a pandas DataFrame or a dictionary of pandas DataFrames
        """
        raise NotImplementedError(
            "You must implement your model serving's predict method"
        )

    def _format_input(
        self, data: Dict
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        try:
            if data.get("multi_dataframe", None) is True:
                return {
                    key: pandas.read_json(value, orient=self.pandas_orient)
                    for key, value in data.items()
                    if key != "multi_dataframe"
                }
            else:
                return pandas.read_json(data, orient=self.pandas_orient)
        except (TypeError, KeyError) as exc:
            err_msg = f"Error reading in json: {exc}"
            logger.warning(err_msg)
            raise HTTPException(status_code=400, detail=err_msg)

    def _format_output(
        self, results: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> JSONResponse:
        try:
            results = results.to_dict(orient=self.pandas_orient)
        except AttributeError:
            results = {
                key: value.to_dict(orient=self.pandas_orient)
                for key, value in results.items()
            }
        return self._get_response(results)


_model_serving_runner = ModelServingRunner(
    ModelServing, [ModelServing, DataFrameModelServing]
)
compose_serving_pandas = _model_serving_runner.compose_serving_models
run_pandas_serving = _model_serving_runner.run_model_serving
