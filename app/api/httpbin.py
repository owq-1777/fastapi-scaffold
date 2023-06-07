from typing import Any
from fastapi import APIRouter, Body, Request, Response

from app.exceptions import MethodNotAllowedError
from app.utils.routers import APIContextRoute


router = APIRouter(route_class=APIContextRoute)


@router.get("")
async def get(request: Request):
    item = {
        'ip': request.client.host,
        'method': request.method,
        "headers": request.headers,
        "url": str(request.url)
    }
    return item


@router.post("")
async def post(request: Request, data: dict[str, Any] = Body(...)):
    return {
        'ip': request.client.host,
        'method': request.method,
        'headers': request.headers,
        'url': str(request.url),
        'data': data
    }


@router.put("")
async def put(request: Request, data: dict[str, Any] = Body(...)):
    return {
        'ip': request.client.host,
        'method': request.method,
        'headers': request.headers,
        'url': str(request.url),
        'data': data
    }


@router.delete("")
async def delete(request: Request, data: dict[str, Any] = Body(...)):
    return {
        'ip': request.client.host,
        'method': request.method,
        'headers': request.headers,
        'url': str(request.url),
        'data': data
    }


@router.patch("")
async def patch(request: Request, data: dict[str, Any] = Body(...)):
    return {
        'ip': request.client.host,
        'method': request.method,
        'headers': request.headers,
        'url': str(request.url),
        'data': data
    }


@router.options("")
async def options():
    return MethodNotAllowedError


@router.head("/")
async def head(request: Request):
    response = Response()
    response.headers["X-Header"] = "Hello FastAPI"
    return response
