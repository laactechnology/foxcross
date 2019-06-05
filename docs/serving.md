# Serving

## Basic Overview
To serve a data science model with `Foxcross`, you must do three things:

* create a class that inherits from `ModelServing`
* define a `predict` method on the class that returns JSON serializable data
* supply test data by defining the class attribute `test_data_path`

directory structure
```
.
+-- data.json
+-- models.py
```
data.json
```json
[1,2,3,4,5]
```
models.py
```python
from foxcross.serving import ModelServing

class AddOneModel(ModelServing):
    test_data_path = "data.json"

    def predict(self, data):
        return [x + 1 for x in data]
```

Doing this gives your model four endpoints:

* `/` (root endpoint)
    * Shows you the different endpoints for you model
    * Allows you to navigate to those endpoints
* `/predict/`
    * Allows users to POST their input data and receive a prediction from your model
* `/predict-test/`
    * Uses the `test_data_path` to read your test data and use it to do a prediction
    * Allows you and your users to test that your prediction is working as expected
    through a GET
* `/input-format/`
    * Reads the `test_data_path` and returns it through a GET
    * Allows you and your users to see what the model expects as input through the predict
    endpoint