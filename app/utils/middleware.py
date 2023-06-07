import time
import uuid

from fastapi import Request, Response
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware

from app.logs import log


class ResponseHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['server'] = 'server'
        return response


class TracebackMiddleware(BaseHTTPMiddleware):
    """ 添加回溯信息, 中间件加载应放在最外层 """

    def generate_trace_id(self):
        return str(uuid.uuid4())[:8]

    def format_request_info(self, request: Request) -> str:
        return f'{request.client.host} - "{request.method} {request.url.path}"'

    async def dispatch(self, request: Request, call_next):

        try:
            getattr(request.state, 'trace_id')
        except AttributeError:
            trace_id = self.generate_trace_id()
            request.state.trace_id = trace_id

        with log.contextualize(trace_id=request.state.trace_id):
            req_info = self.format_request_info(request=request)
            log.bind(action='request').info(f'{req_info}')

            start_time = time.time()

            response = await call_next(request)

            process_time = str(int((time.time() - start_time) * 1000))

            if response.status_code != 200:
                response.headers['x-trace-id'] = request.state.trace_id

            response.headers['x-process-time'] = process_time
            log.bind(action='response').info(f'{req_info} | {response.status_code} | {process_time}ms')

            # 后台执行任务
            # response.background = BackgroundTask()

            return response
