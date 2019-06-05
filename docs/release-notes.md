## 0.5.0
* Removed kubernetes liveness and readiness endpoints
* Decoupled formatting of input and output data from processing hooks
* Added new exception for undefined tests data path
* Fixed `ujson` OverflowError with `numpy.NaN`
* Renamed `NoServingModelsFoundError` to `NoModelServingFoundError`

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