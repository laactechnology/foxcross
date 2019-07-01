# Advanced Usage

## Debugging Mode
**WARNING: this should not be enabled in production**

```python
from foxcross.serving import run_model_serving

run_model_serving(starlette_kwargs={"debug": True})
```
or
```python
from foxcross.serving import compose_models

app = compose_models(debug=True)
```

## Changing the serving module name
If you don't want to serve your models from `models.py`, pass a different module name when
running the serving.

directory structure
```
.
+-- data.json
+-- my_awesome_module.py
```
```python
from foxcross.serving import run_model_serving

run_model_serving(module_name="my_awesome_module")
```
or
```python
from foxcross.serving import compose_models

app = compose_models(module_name="my_awesome_module")
```

## Requiring HTTPS connections
To more securely serve your models, you can require all connections to your model be
encrypted via HTTPS

```python
from foxcross.serving import run_model_serving

run_model_serving(starlette_kwargs={"redirect_https": True})
```
or
```python
from foxcross.serving import compose_models

app = compose_models(redirect_https=True)
```

## Improving performance

To help improve performance, Foxcross supports using extra packages.

#### UJSON

[UJSON](https://github.com/esnme/ultrajson) is supported to speed up JSON serialization and
deserialization.

To install `ujson` with Foxcross, use:
```bash
pip install foxcross[ujson]
```

#### Modin
[Modin](https://github.com/modin-project/modin) is supported to speed up `pandas` operations.

To install `modin` with Foxcross, use:
```bash
pip install foxcross[modin]
```

## Overriding the HTTP status code in custom exceptions

The custom exceptions, `PredictionError`, `PreProcessingError`, and `PostProcessingError`
come with default HTTP status codes returned to the user. These default status codes can be
overridden using the `http_status_code` class attribute

```python
from foxcross.serving import ModelServing
from foxcross.exceptions import PredictionError

class AddOneModel(ModelServing):
    test_data_path = "data.json"

    def predict(self, data):
        try:
            return [x + 1 for x in data]
        except ValueError as exc:
            new_exc = PredictionError(f"Failed to do prediction: {exc}")
            new_exc.http_status_code = 500
            raise new_exc
```
