# Foxcross
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/laactech/foxcross/blob/master/LICENSE.md)
[![Build Status](https://travis-ci.org/laactech/foxcross.svg?branch=master)](https://travis-ci.org/laactech/foxcross)
[![Build status](https://ci.appveyor.com/api/projects/status/github/laactech/foxcross?branch=master&svg=true)](https://ci.appveyor.com/project/laactech/foxcross)
[![PyPI](https://img.shields.io/pypi/v/foxcross.svg?color=blue)](https://pypi.org/project/foxcross/)
[![codecov](https://codecov.io/gh/laactech/foxcross/branch/master/graph/badge.svg)](https://codecov.io/gh/laactech/foxcross)

AsyncIO serving for data science models built on [Starlette](https://www.starlette.io/)

**Requirements**: Python 3.6+

## Quick Start
Installation using `pip`:
```bash
pip install foxcross
```

Create some test data and a simple model in the same directory to be served:

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

if __name__ == "__main__":
    run_model_serving()
```

Run the model locally
```bash
python models.py
```

Navigate to `localhost:8000/predict-test/` in your web browser, and you should see the
list incremented by 1. You can visit `localhost:8000/` to see all the available
endpoints for your model.

## Why does this package exist?
Currently, some of the most popular data science model building frameworks such as PyTorch
and Scikit-Learn do not come with a built in serving library similar to TensorFlow Serving.

To fill this gap, people create Flask applications to serve their model. This can be error
prone, and the implementation can differ between each model. Additionally, Flask is a
[WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
web framework whereas Foxcross is built on [Starlette](https://www.starlette.io/), a
more performant [ASGI](https://asgi.readthedocs.io/en/latest/) web framework.

Foxcross aims to be the serving library for data science models built with frameworks
that do not come with their own serving library. Using Foxcross enables consistent
and testable serving of data science models.

## Security

If you believe you've found a bug with security implications, please do not disclose this
issue in a public forum.

Email us at [support@laac.dev](mailto:support@laac.dev)
