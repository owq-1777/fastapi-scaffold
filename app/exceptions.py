# -*- coding: utf-8 -*-
'''
@Desc   : Init: python -c 'from app.config.core import generate_error_class;generate_error_class()'
'''

from app.config import EXCEPTIONS_CONF
from app.logs import log


class APIBaseException(Exception):
    def __init__(
        self,
        status_code: int = 200,
        api_code: int | None = None,
        msg: str = "error",
        headers: dict[str, str] | None = None,
        *args, **keyword
    ):
        self.status_code = status_code
        self.code = api_code
        self.msg = msg
        self.result = False
        self.headers = headers

class APIError(APIBaseException):
    def __init__(self, open_log: bool = True, **keyword):
        self.open_log = open_log
        self._name = self.__class__.__name__
        self._info: dict = EXCEPTIONS_CONF.get(self._name, {})
        super().__init__(**self._info, **keyword)

        _ = self.open_log and self.record_log()

    def __str__(self):
        return f"{self._name}: {self._info}{' | headers: ' + str(self.headers) if self.headers else ''}"

    def record_log(self):
        log.bind(action='api-error').warning(f"code: {self._info.get('api_code')} | {self._info.get('msg')}")


# * Exception Start

class ParameterError(APIError): ...
class RateLimitError(APIError): ...
class UnauthorizedError(APIError): ...
class ForbiddenError(APIError): ...
class NotfoundError(APIError): ...
class MethodNotAllowedError(APIError): ...
class InternalError(APIError): ...
class RequestAuthError(APIError): ...
class TokenAuthError(APIError): ...
class TokenOverdueError(APIError): ...
class VerifyCodeError(APIError): ...
class RequestTimeoutError(APIError): ...
class FileTooLargeError(APIError): ...
class FileFomatError(APIError): ...

# * Exception End
