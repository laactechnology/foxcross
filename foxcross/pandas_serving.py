import logging
from typing import Dict, Union

from starlette.exceptions import HTTPException

from .base_serving import ModelServing

logger = logging.getLogger(__name__)
try:
    import modin.pandas as pandas
except ImportError:
    try:
        import pandas
    except ImportError as e:
        logger.critical(
            f"Cannot import pandas. Please install foxcross using foxcross[pandas] or"
            f" foxcross[modin]"
        )
        raise e

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

    def pre_process_input(
        self, data: Dict
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        pre_processed_data = super().pre_process_input(data)
        try:
            if data.get("multi_dataframe", None) is True:
                return {
                    key: pandas.read_json(value, orient=self.pandas_orient)
                    for key, value in pre_processed_data.items()
                    if key != "multi_dataframe"
                }
            else:
                return pandas.read_json(pre_processed_data, orient=self.pandas_orient)
        except (TypeError, KeyError) as exc:
            err_msg = f"Error reading in json: {exc}"
            logger.warning(err_msg)
            raise HTTPException(status_code=400, detail=err_msg)

    def post_process_results(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> JSONResponse:
        try:
            results = data.to_json(orient=self.pandas_orient)
        except AttributeError:
            results = {
                key: value.to_dict(orient=self.pandas_orient)
                for key, value in data.items()
            }
        return super().post_process_results(results)
