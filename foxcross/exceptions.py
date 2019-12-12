class FoxcrossException(Exception):
    pass


class NoModelServingFoundError(FoxcrossException):
    pass


class PredictionError(FoxcrossException):
    http_status_code = 400


class TestDataPathUndefinedError(FoxcrossException):
    pass


class PreProcessingError(FoxcrossException):
    http_status_code = 400


class PostProcessingError(FoxcrossException):
    http_status_code = 500
