import logging
from typing import Any, Dict, Union

from starlette.exceptions import HTTPException

from .runner import ModelServingRunner
from .serving import ModelServing

try:
    import modin.pandas as pandas
    import numpy
except ImportError:
    try:
        import pandas
        import numpy
    except ImportError:
        raise ImportError(
            f"Cannot import pandas. Please install foxcross using foxcross[pandas] or"
            f" foxcross[modin]"
        )

logger = logging.getLogger(__name__)


class DataFrameModelServing(ModelServing):
    # TODO: probably should limit to orient choices
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
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        """Hook to enable pre-processing of input data"""
        return super().pre_process_input(data)

    def post_process_results(
        self, data: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        """Hook to enable post-processing of output data"""
        return super().post_process_results(data)

    def _format_input(
        self, data: Dict
    ) -> Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]:
        try:
            if data.pop("multi_dataframe", None) is True:
                return {key: pandas.DataFrame(value) for key, value in data.items()}
            else:
                return pandas.DataFrame(data)
        except (TypeError, KeyError) as exc:
            err_msg = f"Error reading in json: {exc}"
            logger.warning(err_msg)
            raise HTTPException(status_code=400, detail=err_msg)

    def _format_output(
        self, results: Union[pandas.DataFrame, Dict[str, pandas.DataFrame]]
    ) -> Any:
        # Convert NaNs to Nones to handle ujson OverflowError
        try:
            output = results.replace({numpy.nan: None}).to_dict(orient=self.pandas_orient)
        except AttributeError:
            try:
                output = {
                    key: value.replace({numpy.nan: None}).to_dict(
                        orient=self.pandas_orient
                    )
                    for key, value in results.items()
                }
                output["multi_dataframe"] = True
            except (TypeError, AttributeError):
                err_msg = f"Failed to format prediction results"
                logger.exception(err_msg)
                raise HTTPException(status_code=500, detail=err_msg)
        return output


_model_serving_runner = ModelServingRunner(
    ModelServing, (ModelServing, DataFrameModelServing)
)
compose_pandas = _model_serving_runner.compose
run_pandas_serving = _model_serving_runner.run_model_serving
