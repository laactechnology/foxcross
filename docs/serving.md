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

## Serving Hooks

### Hook Overview
`Foxcross` contains two sets of hooks. One set that happens on serving startup and one set
that happens during the models prediction. All subclasses of `ModelServing` have access to
these methods and all these methods are **optional** to define.

* `load_model`
* `pre_process_input`
* `post_process_results`

### Hook Process

* **On startup**: run model serving -> `load_model` -> model serving started
    * This process happens when you start serving your model
* **On prediction**: `pre_process_input` -> `predict` -> `post_process_results`
    * This process happens every time the `predict` and `predict-test` endpoint are called

### load_model
This method allows you to load your model **on startup** and **into memory**.

### pre_process_input
The `pre_process_input` method allows you to transform your input data prior to a prediction.

### post_process_results
The `post_process_results` method allows you to transform your prediction results prior to
them being returned.

### Example
directory structure
```
.
+-- data.json
+-- models.py
+-- random_forest.pkl
```
models.py
```python
from sklearn.externals import joblib
from foxcross.serving import ModelServing

class RandomForest(ModelServing):
    test_data_path = "data.json"
    
    def load_model(self):
        self.model = joblib.load("random_forest.pkl")
    
    def pre_process_input(self, data):
        return self.add_missing_values(data)
    
    def add_missing_values(self, data):
        ...
    
    def predict(self, data):
        return self.model.predict(data)
    
    def post_process_results(self, data):
        return self.prep_results(data)
    
    def prep_results(self, data):
        ...
```