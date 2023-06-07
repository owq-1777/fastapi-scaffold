import os
import re
import uuid
import random
import yaml
from pydantic import BaseSettings
from functools import lru_cache

from app.common.tools import random_str

ROOT = os.getcwd()

class Settings(BaseSettings):

    # ------------------------------------ APP ------------------------------------ #

    # Environment: DEV, TEST, PROD
    RUN_ENV: str = 'DEV'
    LOG_LEVEL: str = 'INFO'

    ROOT = os.getcwd()

    # Directory for storing log files
    LOG_DIR: str = f'{ROOT}/logs'
    LOG_COLORIZE: bool = True

    # Directory for static files
    STATIC_DIR: str = f'{ROOT}/app/static'

    EXCEPTIONS_FILE: str = f'{ROOT}/app/exceptions.py'
    EXCEPTIONS_CONF: str = f'{ROOT}/app/config/exceptions.yaml'

    # ------------------------------------ API ------------------------------------ #

    TITLE: str = 'FastAPI'
    DEBUG: bool = True
    VERSION: str = '0.1.0'

    OPENAPI_URL: str | None = f'/openapi-{random_str(16)}.json'

    API_HOST = '127.0.0.1'
    API_POST = 7000
    API_WORKERS = 6

    API_TRACE_ID = '-' + str(uuid.uuid4())[:6] + '-'

    API_DOCS = f'/docs-{random_str(16)}'

    SCOPES: dict = {"own": "Own account permission"}

    ORIGINS = [
        "http://localhost",
        "http://localhost:7000",
    ]

    API_URL = f'http://{API_HOST}:{API_POST}'

    # ------------------------------------ Safety ------------------------------------ #

    # APP secret Key | openssl rand -hex 32
    SECRET_KEY: str = '2adbf44be99ad863172212d8eed8d4b2a14c827ec435ce134c4bf1dc46005c29'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    # ------------------------------------ DB ------------------------------------ #

    # MYSQL_URL = 'mysql://[[username]:[password]]@[host]:[port]/[database]?charset=utf8mb4'
    MYSQL_URL: str = 'mysql://username:password@localhost:3306/fastapi?charset=utf8mb4'

    # redis://[[username]:[password]]@[host]:[port]/[database number]
    REDIS_URL: str = 'redis:/127.0.0.1:6379/1'

    # ------------------------------------  ------------------------------------ #

    @property
    def log_dir(cls):
        return cls.LOG_DIR.rstrip("/")

    @property
    def log_file(cls):
        return f'{cls.log_dir}/api.log'

    @property
    def error_log_file(cls):
        return f'{cls.log_dir}/error.log'

    @property
    def debug_log_file(cls):
        return f'{cls.log_dir}/debug.log'

    @property
    def log_lever(cls):
        return cls.LOG_LEVEL if not cls.DEBUG else 'DEBUG'


@lru_cache
def get_config():
    return Settings() # type: ignore


@lru_cache
def get_exceptions_conf() -> dict:
    with open(get_config().EXCEPTIONS_CONF, 'r') as f:
        return yaml.load(f, yaml.FullLoader)


def generate_error_class():
    """ Generate exception classes based on the configuration """

    exc_file = get_config().EXCEPTIONS_FILE
    exceptions_conf = get_exceptions_conf()

    class_code = ''
    for k in exceptions_conf.keys():
        class_code += f"class {k}(APIError): ...\n"
    class_code += "\n"

    with open(exc_file, 'r') as f:
        content = f.read()

    start_str = "# * Exception Start\n\n"
    end_str = "# * Exception End\n"
    pattern = r"(?<=# \* Exception Start\n)(.*?)(?=\n# \* Exception End\n)"
    if re.findall(pattern, content, re.DOTALL):
        start_index = content.index(start_str)
        end_index = content.index(end_str) + len(end_str)
        if content[start_index:end_index] == start_str + class_code + end_str:
            return
        new_content = content[:start_index] + start_str + class_code + end_str + content[end_index:]
    else:
        new_content = content.strip() + "\n\n\n" + start_str + class_code + end_str

    with open(exc_file, "w") as file:
        file.write(new_content)

    print(f'Generate exceptions class: {list(exceptions_conf.keys())}')
