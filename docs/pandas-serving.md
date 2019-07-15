# Pandas Serving
**Make sure you have installed Foxcross with the pandas extra using:**

`pip install foxcross[pandas]`

## Overview
Serving pandas based models works very similar to the basic model serving with a few
caveats:

* The class to subclass changes from `ModelServing` to `DataFrameModelServing`
* The internal data structure for the model should be either a pandas DataFrame or a
dictionary of pandas DataFrames with string keys
* Running the model serving requires using `run_pandas_serving` from `foxcross.pandas_serving`
* Composing serving models requires using `compose_pandas` from `foxcross.pandas_serving`

## Basic Example
directory structure
```
.
+-- data.json
+-- models.py
```
data.json
```json
{
  "A": [12,4,5,null,1],
  "B": [null,2,54,3,null],
  "C": [20,16,null,3,8],
  "D": [14, 3,null,null,6]
}
```
models.py
```python
from foxcross.pandas_serving import DataFrameModelServing, run_pandas_serving
import pandas

class InterpolateModel(DataFrameModelServing):
    test_data_path = "data.json"

    def predict(self, data: pandas.DataFrame) -> pandas.DataFrame:
        return data.interpolate(limit_direction="both")
        
if __name__ == "__main__":
    run_pandas_serving()
```

Run the model locally:
```bash
python models.py
```

Navigate to `localhost:8000/predict-test/` in your web browser, and you should see the
the `null` values replaced. You can visit `localhost:8000/` to see all the available
endpoints for your model.

## Serving a dictionary of DataFrames model

Foxcross `DataFrameModelServing` uses either a pandas DataFrame or a dictionary of pandas
DataFrames as its data structure.

**To serve a dictionary of DataFrames, you must add `"multi_dataframe": true` to your
input data.**

#### Example

data.json
```json
{
  "multi_dataframe": true,
  "interp_dict": {
    "A": [12,4,5,null,1],
    "B": [null,2,54,3,null],
    "C": [20,16,null,3,8],
    "D": [14, 3,null,null,6]
  },
  "interp_list": [
    0.0,  null, -1.0, 1.0,
    null, 2.0, null, null,
    2.0, 3.0, null, 9.0,
    null, 4.0, -4.0, 16.0
  ]
}
```
models.py
```python
from typing import Dict
from foxcross.pandas_serving import DataFrameModelServing
import pandas

class InterpolateMultiDataFrameModel(DataFrameModelServing):
    test_data_path = "data.json"

    def predict(
        self, data: Dict[str, pandas.DataFrame]
    ) -> Dict[str, pandas.DataFrame]:
        return {
            key: value.interpolate(limit_direction="both")
            for key, value in data.items()
        }
```

## Serving pandas and regular models

Foxcross can serve both your regular models that inherit from `ModelServing` and 
`DataFrameModelServing` together. You must use either `run_pandas_serving` or 
`compose_pandas` whenever your models use `DataFrameModelServing`.

#### Example
directory structure
```
.
+-- add.json
+-- interpolate.json
+-- models.py
```
interpolate.json
```json
{
  "A": [12,4,5,null,1],
  "B": [null,2,54,3,null],
  "C": [20,16,null,3,8],
  "D": [14, 3,null,null,6]
}
```
add.json
```json
[1,2,3,4,5]
```
models.py
```python
from foxcross.pandas_serving import DataFrameModelServing, run_pandas_serving
from foxcross.serving import ModelServing
import pandas

class InterpolateModel(DataFrameModelServing):
    test_data_path = "interpolate.json"

    def predict(self, data: pandas.DataFrame) -> pandas.DataFrame:
        return data.interpolate(limit_direction="both")

class AddOneModel(ModelServing):
    test_data_path = "add.json"

    def predict(self, data):
        return [x + 1 for x in data]
        
if __name__ == "__main__":
    run_pandas_serving()
```

Run the model locally:
```bash
python models.py
```

Navigate to `localhost:8000/` in your web browser, and you should see both the
`/addonemodel` and the `/interpolatemodel`.


## Changing the orient of Pandas output

Foxcross uses the Pandas [to_dict](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_dict.html)
method before turning results into JSON. The `to_dict` method uses an `orient` argument to
determine the output format. The default orient used by Foxcross is `index`, but
this can be changed.

#### Example
models.py
```python
from foxcross.pandas_serving import DataFrameModelServing
import pandas

class InterpolateModel(DataFrameModelServing):
    test_data_path = "data.json"
    pandas_orient = "records"

    def predict(self, data: pandas.DataFrame) -> pandas.DataFrame:
        return data.interpolate(limit_direction="both")
```
