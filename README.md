## Foxcross
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/laactech/foxcross/blob/master/LICENSE.md)
[![Build Status](https://travis-ci.org/laactech/foxcross.svg?branch=master)](https://travis-ci.org/laactech/foxcross)
[![Build status](https://ci.appveyor.com/api/projects/status/github/laactech/foxcross?branch=master&svg=true)](https://ci.appveyor.com/project/laactech/foxcross)
![PyPI](https://img.shields.io/pypi/v/foxcross.svg?color=blue)

AsyncIO serving for data science models built on [Starlette](https://www.starlette.io/)

**Documentation**: https://www.foxcross.dev/

**Requirements**: Python 3.6+

## Quick Start
Installation using `pip`:
```bash
pip install foxcross
```

Create some test data and a simple model in the same directory to be served:

`data.json`
```json
[1,2,3,4,5]
```

`models.py`
```python
from foxcross.serving import ModelServing, run_model_serving

class AddOneModel(ModelServing):
    test_data_path = "data.json"

    def predict(self, data):
        return [x + 1 for x in data]

if __name__ == "__main__":
    run_model_serving()
```

Run the model locally:
```bash
python models.py
```

Navigate to `localhost:8000/predict-test/`, and you should see the list incremented by 1.
You can visit `localhost:8000/` to see all the available routes for your model.
