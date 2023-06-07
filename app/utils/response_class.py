# -*- coding: utf-8 -*-
'''
@Desc   : 接口响应类
'''

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class UnifiedModel(BaseModel):
    code: int = 0
    result: bool = True
    data: dict | None = None
    msg: str = 'succeed'


class BaseErrorResModel(BaseModel):
    code: int
    result: bool = False
    msg: str = 'failure'
    details: list | None = None
    trace_id: str | None


class UnifiedResponse(JSONResponse):
    def __init__(
        self,
        content: dict | None = None,
        status_code: int = 200,
        code: int = 0,
        result: bool = True,
        msg: str = 'succeed',
        **keyword,
    ):
        _content = UnifiedModel(code=code, result=result, data=content, msg=msg)
        super().__init__(_content.dict(), status_code, **keyword)


class ExceptionResponse(JSONResponse):
    def __init__(
        self,
        trace_id: str | None = None,
        status_code: int = 200,
        code: int | None = None,
        msg: str = 'failure',
        headers: dict[str, str] | None = None,
        details: list | None = None,
        **keyword,
    ):
        code = status_code + 20000 if code is None else code
        _content = BaseErrorResModel(code=code, msg=msg, trace_id=trace_id, details=details)
        super().__init__(_content.dict(), status_code, headers=headers, **keyword)
