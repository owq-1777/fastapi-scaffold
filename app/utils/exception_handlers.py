import traceback
from functools import wraps
from pprint import pformat
from typing import Callable

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.utils.response_class import ExceptionResponse
from app.exceptions import APIBaseException
from app.logs import log

from app.exceptions import ParameterError, InternalError

# ------------------------------------ Decorator ------------------------------------ #


def add_exception_handler(exc, raise_exc=None, error_callback: Callable | None = None) -> Callable:
    ''' 错误捕获处理 '''

    def wrapper(func):
        @wraps(func)
        async def wrap(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exc as e:  # type: ignore
                if error_callback:
                    await error_callback(*args, **kwargs)
                else:
                    if raise_exc:
                        raise raise_exc
                    raise e

        return wrap

    return wrapper


# ------------------------------------ Error handler ------------------------------------ #


async def api_error_handler(request: Request, exc: APIBaseException):
    return ExceptionResponse(trace_id=request.state.trace_id, status_code=exc.status_code, code=exc.code, msg=exc.msg)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    content = {'detail': exc.errors(), 'body': exc.body}
    msg = 'Request field validation error'
    log.warning(f'{msg}\n{pformat(content)}')
    error = ParameterError()
    return ExceptionResponse(trace_id=request.state.trace_id, status_code=error.status_code, msg=error.msg, details=exc.errors())


async def http_error_handler(request: Request, exc: HTTPException):
    log.error(f'HTTP exception:\n{exc.detail}')
    return ExceptionResponse(trace_id=request.state.trace_id, status_code=exc.status_code, msg=exc.detail)


async def server_exception_handler(request: Request, exc: Exception):
    log.error(f'Server exception: {exc.args}\n{traceback.format_exc()}')
    error = InternalError()
    return ExceptionResponse(trace_id=request.state.trace_id, status_code=error.status_code, msg=error.msg)
