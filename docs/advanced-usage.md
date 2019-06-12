# Advanced Usage

## Debugging Mode
**WARNING: this should not be enabled in production**

```python
from foxcross.serving import run_model_serving

run_model_serving(debug=True)
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

run_model_serving(redirect_https=True)
```
or
```python
from foxcross.serving import compose_models

app = compose_models(redirect_https=True)
```
