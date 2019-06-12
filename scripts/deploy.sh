#!/usr/bin/env bash
set -e

pyproj_version=$( cat pyproject.toml | grep version | sed "s/version = //" | sed "s/'//g" )

dunder_version=$( cat foxcross/__version__.py | grep version | sed "s/__version__ = //" | sed "s/'//g" )

if [[ ${pyproj_version} -ne ${dunder_version} ]]; then exit 1; fi

pip install poetry
poetry install

poetry run python ./scripts/check_version_bumped.py

if [[ $? -ne 0 ]]; then exit 1; fi

git config --global user.email "travis@travis-ci.org"
git config --global user.name "Travis CI"
git checkout master

git tag -a ${dunder_version} -m ${dunder_version}
git push --tags

poetry publish --build -u ${PYPI_USER} -p ${PYPI_PASS}

poetry run mkdocs gh-deploy