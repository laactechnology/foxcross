#!/usr/bin/env bash
set -e

# Install dependency management tool
pip install poetry
poetry install

# Validate version has been bumped and matches
poetry run python ./scripts/validate_version.py
if [[ $? -ne 0 ]]; then exit 1; fi

# Publish to pypi
poetry publish --build -u ${PYPI_USER} -p ${PYPI_PASS}

# Publish new docs
poetry run mkdocs gh-deploy