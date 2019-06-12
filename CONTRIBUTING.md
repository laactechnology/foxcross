# Contributing to Foxcross
To submit new code to the project you'll need to:

1. Fork the repo
2. Clone your fork on your local computer: `git clone https://github.com/<username>/foxcross.git`
3. Install [poetry](https://github.com/sdispater/poetry#installation) for managing
dependencies
4. Install Foxcross locally: `poetry install`
5. Run the basic test suite: `pytest tests/test_serving.py tests/test_failed_serving.py tests/test_no_extra.py`
6. Install the linters: `pre-commit install`
7. Create a branch for your work: `git checkout -b <branch-name>`
8. Make your changes
9. Add any tests or documentation necessary
10. Push to your remote: `git push origin <branch-name>`
11. [Open a pull request](https://github.com/laactech/foxcross/compare)