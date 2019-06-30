from enum import Enum


class MediaTypes(Enum):
    JSON = "application/json"
    HTML = "text/html"
    ANY_TEXT = "text/*"
    ANY_APP = "application/*"
    ANY = "*/*"
