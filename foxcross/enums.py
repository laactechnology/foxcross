from enum import Enum


class MediaTypes(Enum):
    JSON = "application/json"
    ANY_APP = "application/*"
    ANY = "*/*"
