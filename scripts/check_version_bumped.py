import requests

from foxcross.__version__ import __version__

PYPI_URL = "https://pypi.org/pypi/foxcross/json"


def main():
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
