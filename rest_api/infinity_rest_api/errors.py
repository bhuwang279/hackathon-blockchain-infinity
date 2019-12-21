import json

from aiohttp.web import HTTPError


class _ApiError(HTTPError):
    """A parent class for all REST API errors. Extends aiohttp's HTTPError,
    so instances will by caught automatically by the API, and turned into a
    response to send back to clients. Children should not define any methods,
    just four class variables which the parent __init__ will reference.
    Attributes:
        status_code (int): HTTP status to use. Referenced withinin HTTPError's
            __init__ method.
        message (str): The human-readable description of the error.
    Raises:
        AssertionError: If api_code, status_code, title, or message were
            not set.
    """

    status_code = None
    message = None

    def __init__(self):
        assert self.status_code is not None, 'Invalid ApiError, status not set'
        assert self.message is not None, 'Invalid ApiError, message not set'

        super().__init__(
            content_type='application/json',
            text=json.dumps(
                {'error': self.message},
                indent=2,
                separators=(',', ': '),
                sort_keys=True))


class ApiBadRequest(_ApiError):
    def __init__(self, message):
        self.status_code = 400
        self.message = 'Bad Request: ' + message
        super().__init__()


class ApiInternalError(_ApiError):
    def __init__(self, message):
        self.status_code = 500
        self.message = 'Internal Error: ' + message
        super().__init__()


class ApiNotFound(_ApiError):
    def __init__(self, message):
        self.status_code = 404
        self.message = 'Not Found: ' + message
        super().__init__()


class ApiUnauthorized(_ApiError):
    def __init__(self, message):
        self.status_code = 401
        self.message = 'Unauthorized: ' + message
        super().__init__()
