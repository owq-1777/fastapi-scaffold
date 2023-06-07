from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException

from app.utils.exception_handlers import api_error_handler, validation_error_handler, http_error_handler, server_exception_handler
from app.utils.middleware import TracebackMiddleware
from app.api import router

from app.exceptions import APIBaseException

from app.config import CONF
from app.logs import reset_uvicorn_logger,log


def add_exception_handler(app: FastAPI):

    app.add_exception_handler(Exception, server_exception_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(APIBaseException, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


def add_middleware(app: FastAPI):

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CONF.ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_middleware(TracebackMiddleware)


def add_router(app: FastAPI):

    app.include_router(router)


def init_app():

    app = FastAPI(
        title=CONF.TITLE,
        debug=CONF.DEBUG,
        version=CONF.VERSION,
        openapi_url=CONF.OPENAPI_URL,
        docs_url=CONF.API_DOCS,
    )

    add_router(app)
    add_middleware(app)
    add_exception_handler(app)

    return app


log.bind(action='api-server', trace_id=CONF.API_TRACE_ID).info(
    f'Started {CONF.TITLE} ({CONF.VERSION}) server'
    f' | ENV: {CONF.RUN_ENV} | Debug: {CONF.DEBUG}'
    f' | Docs: {CONF.API_URL}{CONF.API_DOCS}'
)
reset_uvicorn_logger()

app = init_app()
