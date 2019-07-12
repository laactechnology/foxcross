from enum import Enum


class MediaTypes(Enum):
    JSON = "application/json"
    HTML = "text/html"
    ANY_TEXT = "text/*"
    ANY_APP = "application/*"
    ANY = "*/*"

    @classmethod
    def html_media_types(cls):
        return cls.ANY.value, cls.ANY_TEXT.value, cls.HTML.value

    @classmethod
    def json_media_types(cls):
        return cls.ANY.value, cls.ANY_APP.value, cls.JSON.value
