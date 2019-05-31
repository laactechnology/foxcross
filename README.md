## Foxcross
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/laactech/foxcross/blob/master/LICENSE.md)
[![Build Status](https://travis-ci.org/laactech/foxcross.svg?branch=master)](https://travis-ci.org/laactech/foxcross)
[![Build status](https://ci.appveyor.com/api/projects/status/ufbm8hrkp4whol5a?svg=true)](https://ci.appveyor.com/project/laactech/foxcross)

AsyncIO serving for data science models built on [Starlette](https://www.starlette.io/)

**Documentation**: https://www.foxcross.dev/

**Requirements**: Python 3.6+

## Quick Start
Installation using `pip`:
```bash
pip install foxcross
```

Create some test data and a simple model to be served:

`data.json`
```json
[1,2,3,4,5]
```

`models.py`
```python
import foxcross

class AddOneModel(foxcross.ModelServing):
    test_data_path = "data.json"
    
    def predict(self, data):
        return [x + 1 for x in data]

if __name__ == "__main__":
    foxcross.run_model_serving()
```

Run the model locally:
```bash
python models.py
```

Navigate to `localhost:8000/predict-test/` and you should see the list incremented by 1.
You can visit `localhost:8000/` to see all the available routes for your model.
