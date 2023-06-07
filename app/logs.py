import sys
import os
import logging
from datetime import datetime
import uuid

from loguru import logger

from app.common.colorizer import colorize
from app.common.time_tools import calculate_cutoff_time
from app.config import CONF

from pprint import pformat


LOGURU_ACTION = '{name}.{function}:{line}'
LOGURU_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> '
    '| <level>{level: <8}</level> '
    '| <light-black>{extra[trace_id]}</light-black> '
    '| <cyan>' + LOGURU_ACTION + '</cyan> '
    '| <level>{message}</level>'
)

# ------------------------------------ uvicorn conf ------------------------------------ #


class InterceptHandler(logging.Handler):
    """
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).bind(
            name='api', action='api-server', trace_id=CONF.API_TRACE_ID).log(level, record.getMessage())


def reset_uvicorn_logger():
    """ Change handler for default uvicorn logger """

    # uvicorn log default configuration: uvicorn.config.LOGGING_CONFIG
    # Clear uvicorn default log handler, which needs to be run after uvicorn is initialized
    uvicorn_loggers = (logging.getLogger(name) for name in logging.root.manager.loggerDict if name.startswith('uvicorn.'))
    for i in uvicorn_loggers:
        i.handlers = []

    # Set the logger of uvicorn to loguru
    logging.getLogger('uvicorn').handlers = [InterceptHandler()]
    # logging.getLogger('uvicorn.error').handlers = [InterceptHandler()]
    # logging.getLogger('uvicorn.access').handlers = [InterceptHandler()]


# ------------------------------------ Log tools ------------------------------------ #


def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    """

    loguru_format = LOGURU_FORMAT
    if action := record['extra'].get('action'):
        loguru_format = loguru_format.replace(LOGURU_ACTION, f'{action: <10}')

    if payload := record['extra'].get('payload'):
        record['extra']['payload'] = pformat(payload, indent=4, compact=True, width=88)
        loguru_format += "\n<level>{extra[payload]}</level>"

    loguru_format += "{exception}\n"
    return loguru_format


def make_filter(name):
    def _filter(record):
        return record["extra"].get("name") == name

    return _filter


def check_trace_id(log_record):
    if not log_record['extra'].get('trace_id'):
        trace_id = str(uuid.uuid4())[:8] if log_record['level'].name in ['WARNING', 'ERROR'] else '--------'
        log_record['extra']['trace_id'] = trace_id


# ------------------------------------ Find log fun ------------------------------------ #


def decode_logs_file(log_file: str = CONF.log_file):
    pattern = r"(?P<time>.*) \| (?P<level>.*) \| (?P<trace_id>.*) \| (?P<action>.*) \| (?P<message>.*)"
    items = []
    for groups in logger.parse(log_file, pattern):
        items.append(groups)
    return items


def find_logs(trace_id: str):
    items = decode_logs_file(CONF.log_file)
    log_format = '<green>{time}</green> | <level>{level: <8}</level> | <light-black>{trace_id}</light-black> | <cyan>{func}</cyan> | <level>{message}</level>'
    logs = ''
    for i in items:
        if i['trace_id'] == trace_id:
            logs += colorize(log_format.format(
                time=i['time'],
                level=i['level'],
                trace_id=i['trace_id'],
                func=i['func'],
                message=i['message'],
            )) + '\n'

    if not logs:
        print(f'No logs matching the `trace_id` of {trace_id} were found.')
    else:
        print(logs)

    return logs


def delete_expired_log_files(log_file_name: str, retention_period: str):

    # 日志文件的基础名称
    log_name = log_file_name.replace(f'{CONF.LOG_DIR}/', '')
    base_name, ext = os.path.splitext(log_name)

    cutoff_time = calculate_cutoff_time(retention_period)

    # 归档的时间戳格式
    timestamp_format = '%Y-%m-%d_%H-%M-%S_%f'

    # 遍历日志文件所在目录下的所有文件
    for file_name in os.listdir(CONF.LOG_DIR):
        # 如果文件名以日志文件的基础名称开头，且以时间戳格式结尾，说明是归档的日志文件
        if file_name.startswith(base_name) and file_name.endswith(ext):
            try:
                # 解析时间戳
                timestamp = datetime.strptime(file_name[len(base_name) + 1:-len(ext)], timestamp_format)

                # 如果时间戳早于保留日志的截止时间 删除该文件
                if timestamp < cutoff_time:
                    print(f'remove {file_name}')
                    os.remove(f'{CONF.LOG_DIR}/{file_name}')
            except ValueError:
                pass

# ------------------------------------ Init log fun ------------------------------------ #


def init_logger():

    global logger

    # Delete default recorder
    logger.remove()

    logger = logger.patch(check_trace_id)

    handlers = [
        dict(
            sink=sys.stderr,
            format=format_record,
            level='DEBUG',
            colorize=True,
        ),
        dict(
            sink=CONF.log_file,
            level=CONF.log_lever,
            format=format_record,
            rotation='100 MB',
            enqueue=True,
            colorize=False,
            filter=make_filter('api'),
        ),
        dict(
            sink=CONF.error_log_file,
            level='ERROR',
            format=format_record,
            rotation='50 MB',
            enqueue=True,
            colorize=False,
        ),
    ]

    if CONF.DEBUG:
        # Record the details of the error log
        handlers.append(dict(
            sink=CONF.debug_log_file,
            format=format_record,
            rotation='1 day',
            backtrace=True,
            diagnose=True,
            enqueue=True,
            colorize=False,
        ))

    logger.configure(handlers=handlers)

    print('init logs done.')



# ------------------------------------ Init log ------------------------------------ #


init_logger()
log = logger.bind(name='api')