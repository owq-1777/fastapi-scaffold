import re
from enum import IntEnum


class Style(IntEnum):
    RESET_ALL = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    STRIKE = 8
    HIDE = 9
    NORMAL = 22


class Fore(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    LIGHT_BLACK = 90
    LIGHT_RED = 91
    LIGHT_GREEN = 92
    LIGHT_YELLOW = 93
    LIGHT_BLUE = 94
    LIGHT_MAGENTA = 95
    LIGHT_CYAN = 96
    LIGHT_WHITE = 97


class Back(IntEnum):
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 49

    LIGHT_BLACK = 100
    LIGHT_RED = 101
    LIGHT_GREEN = 102
    LIGHT_YELLOW = 103
    LIGHT_BLUE = 104
    LIGHT_MAGENTA = 105
    LIGHT_CYAN = 106
    LIGHT_WHITE = 107


def ansi_escape(codes):
    return {i.name.lower().replace('_', '-'): "\033[%dm" % i.value for i in codes}


def colorize(text: str) -> str:
    """ Converts text with a color label to a colored string """

    if match := re.search(r'<level>(.*?)</level>', text):
        level = match.group(1).strip()
        text = text.replace('<level>', f'<level:{level}>').replace('</level>', f'</level:{level}>')

    if match := re.search(r'<model>(.*?)</model>', text):
        model = match.group(1).strip()
        text = text.replace('<model>', f'<model:{model}>').replace('</model>', f'</model:{model}>')

    color_map = {
        **ansi_escape(Fore),
        "reset": "\033[0m",
        "level": {
            "DEBUG": f"\033[{Fore.LIGHT_BLUE}m",
            "INFO": f"\033[{Fore.LIGHT_WHITE}m",
            "WARNING": f"\033[{Fore.LIGHT_YELLOW}m",
            "ERROR": f"\033[{Fore.LIGHT_RED}m",
        },
        "model": {
            "GET": f"\033[;{Fore.WHITE};{Back.BLUE}m",
            "POST": f"\033[;{Fore.WHITE};{Back.GREEN}m",
            "PUT": f"\033[;{Fore.WHITE};{Back.YELLOW}m",
            "DELETE": f"\033[;{Fore.WHITE};{Back.RED}m",
            "HEAD": f"\033[;{Fore.WHITE};{Back.LIGHT_MAGENTA}m",
            "PATCH": f"\033[;{Fore.WHITE};{Back.LIGHT_GREEN}m",
            "OPTIONS": f"\033[;{Fore.WHITE};{Back.LIGHT_BLUE}m",
        }
    }

    for color in color_map:
        if isinstance(color_map[color], dict):
            for level in color_map[color]:
                text = text.replace(f"<{color}:{level}>", color_map[color][level])
                text = text.replace(f"</{color}:{level}>", color_map["reset"])
        else:
            text = text.replace(f"<{color}>", color_map[color])
            text = text.replace(f"</{color}>", color_map["reset"])

    return text
