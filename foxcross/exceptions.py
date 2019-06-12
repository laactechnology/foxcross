class NoModelServingFoundError(Exception):
    pass


class BadDataFormatError(Exception):
    http_status_code = 400


class TestDataPathUndefinedError(Exception):
    pass


class PreProcessingError(Exception):
    http_status_code = 400


class PostProcessingError(Exception):
    http_status_code = 500
