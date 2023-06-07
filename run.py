import uvicorn

from app.config import CONF
from app.logs import log, reset_uvicorn_logger


def start_api():

    log.bind(action='api-server', trace_id=CONF.API_TRACE_ID).info(
        f'Started {CONF.TITLE} ({CONF.VERSION}) server'
        f' | ENV: {CONF.RUN_ENV} | Debug: {CONF.DEBUG}'
        f' | Docs: {CONF.API_URL}{CONF.API_DOCS}'
    )

    config = uvicorn.Config(
        'app.main:app',
        host=CONF.API_HOST,
        port=CONF.API_POST,
        workers=CONF.API_WORKERS,
        debug=CONF.DEBUG,
        proxy_headers=True,
        server_header=False,
    )
    reset_uvicorn_logger()

    server = uvicorn.Server(config)
    server.run()


if __name__ == '__main__':
    start_api()
