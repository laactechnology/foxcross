from enum import Enum


class MediaTypes(Enum):
    JSON = "application/json"
    HTML = "text/html"
    ANY_APP = "application/*"
    ANY = "*/*"
