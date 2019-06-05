# Pandas Serving
**Make sure you have installed foxcross with the pandas extra using:**

`pip install foxcross[pandas]`

## Basic Example
directory structure:
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

class InterpolateModelServing(DataFrameModelServing):
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