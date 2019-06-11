## 0.6.0 (Next release)
* Added `PreProcessingError` for use with `pre_process_input`
* Added `PostProcessingError` for use with `post_process_results`
* Included home route for every model index page
* Removed `performance` extra install
* Refactored model serving compose interface

## 0.5.0
* Removed kubernetes liveness and readiness endpoints
* Decoupled formatting of input and output data from processing hooks
* Added new exception for undefined tests data path
* Fixed `ujson` OverflowError due to `numpy.NaN`
* Renamed `NoServingModelsFoundError` to `NoModelServingFoundError`
* Removed pre processing from `/input-format/` endpoint
* Refactored model serving compose interface
* Enabled passing of `kwargs` to `ModelServingRunner` methods

## 0.4.0
* Fixed pandas import error
* Reworked running model serving and composing serving models

## 0.3.0
* Reworked API
* Fixed quick start example

## 0.2.0
* First working release

## 0.1.0
* Initial release