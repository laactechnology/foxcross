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

## Serving Endpoints
Subclassing any class that inherits from `ModelServing` gives you four endpoints:

* `/` (root endpoint)
    * Shows you the different endpoints and HTTP methods for your model
    * Allows you to navigate to those endpoints
* `/predict/`
    * Allows users to POST their input data and receive a prediction from your model
* `/predict-test/`
    * Uses the `test_data_path` to read your test data and do a prediction with the test data
    * Allows you and your users to test that your prediction is working as expected
    through a GET request
* `/input-format/`
    * Reads the `test_data_path` and returns the data through a GET request
    * Allows you and your users to see what the model expects as input for the predict
    endpoint

## Serving Hooks

### Hook Overview
`Foxcross` contains two sets of hooks. One set that happens on serving startup and one set
that happens during the models prediction. All subclasses of `ModelServing` have access to
these methods, and all these methods are **optional** to define.

* `load_model`
    * Allows you to load your model **on startup** and **into memory**.
* `pre_process_input`
    * Allows you to transform your input data prior to a prediction.
* `post_process_results`
    * Allows you to transform your prediction results prior to them being returned.

### Hook Process

* **On startup**: run model serving -> `load_model` -> model serving started
    * This process happens when you start serving your model
* **On prediction**: `pre_process_input` -> `predict` -> `post_process_results`
    * This process happens every time the `predict` and `predict-test` endpoints are called

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

## Serving multiple models

`Foxcross` enables you to compose and serve multiple models from a single place.

#### Example
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
from foxcross.serving import ModelServing, run_model_serving

class AddOneModel(ModelServing):
    test_data_path = "data.json"

    def predict(self, data):
        return [x + 1 for x in data]

class AddTwoModel(ModelServing):
    test_data_path = "data.json"
    
    def predict(self, data):
        return [y + 2 for y in data] 

if __name__ == "__main__":
    run_model_serving()
```

Navigate to `localhost:8000/` in your web browser. You should see routes to both the
`AddOneModel` and the `AddTwoModel`. Clicking on one of the model routes show you that
both models come with the same set of endpoints and both perform predictions.

#### How does this work?
Foxcross finds all classes inside your `models.py` file that subclass `ModelServing` and
combines those into a single model serving. Foxcross uses the name of the class such as
`AddOneModel` and `AddTwoModel` to define the routes where those models live.

## Running in Production

`Foxcross` leverages [uvicorn](https://github.com/encode/uvicorn) to run model serving.

We recommend using [gunicorn](https://github.com/benoitc/gunicorn) to serve models in
production. Details about running uvicorn with gunicorn can be found
[here](https://www.uvicorn.org/deployment/#gunicorn)

#### Example
directory structure
```
.
+-- data.json
+-- models.py
+-- app.py
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

class AddTwoModel(ModelServing):
    test_data_path = "data.json"
    
    def predict(self, data):
        return [y + 2 for y in data] 
```
app.py
```python
from foxcross.serving import compose_models

app = compose_models()
```
Assuming gunicorn has been installed, run:
`gunicorn -k uvicorn.workers.UvicornWorker app:app`
