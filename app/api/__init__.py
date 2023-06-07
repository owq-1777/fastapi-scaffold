import asyncio
from random import randint
from fastapi import APIRouter, Request, Response

from app.logs import log
from . import httpbin
from app.exceptions import MethodNotAllowedError


router = APIRouter(prefix='')

router.include_router(httpbin.router, prefix='/httpbin', tags=['httpbin'])


# ------------------------------------  ------------------------------------ #


@router.api_route(
    '{url_path:path}',
    methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'HEAD'],
    include_in_schema=False
)
async def get_404(request: Request, url_path: str):
    method = request.method
    if method == 'HEAD':
        response = Response()
        return response

    if request.client.host not in ['127.0.0.1']:
        wait_time = randint(1, 10)
        log.debug(f'wail {wait_time}s response...')
        await asyncio.sleep(wait_time)
    raise MethodNotAllowedError
