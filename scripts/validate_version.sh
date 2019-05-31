#!/usr/bin/env bash
set -e

pyproj_version=$( cat pyproject.toml | grep version | sed "s/version = //" | sed "s/'//g" )

dunder_version=$( cat foxcross/__version__.py | grep version | sed "s/__version__ = //" | sed "s/'//g" )

if [[ ${pyproj_version} -ne ${dunder_version} ]]; then exit 1; fi
