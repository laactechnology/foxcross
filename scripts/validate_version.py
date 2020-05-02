#!/usr/bin/env python
import os
from pathlib import Path

import requests
import tomlkit

from foxcross import __version__

PYPI_URL = "https://pypi.org/pypi/foxcross/json"


def main():
    pyproj_dir = os.path.abspath(os.path.join(__file__, "../.."))
    with Path(f"{pyproj_dir}/pyproject.toml").open() as f:
        pyproject = tomlkit.parse(f.read())

    pyproj_version = pyproject["tool"]["poetry"]["version"]

    if pyproj_version != __version__:
        print(
            f"pyproject version {pyproj_version} does not match dunder version"
            f" {__version__}"
        )
        return 1

    response = requests.get(PYPI_URL)

    pypi_version = response.json()["info"]["version"]

    if __version__ == pypi_version:
        print(f"dunder version: {__version__}, pypi version: {pypi_version}")
        print("Version is not incremented")
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit(main())
