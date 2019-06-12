#!/usr/bin/env bash
set -e

pip install poetry
poetry install

poetry run python ./scripts/validate_version.py

if [[ $? -ne 0 ]]; then exit 1; fi

git config --global user.email "travis@travis-ci.org"
git config --global user.name "Travis CI"
git checkout master

git tag -a ${dunder_version} -m ${dunder_version}
git push --tags

poetry publish --build -u ${PYPI_USER} -p ${PYPI_PASS}

poetry run mkdocs gh-deploy