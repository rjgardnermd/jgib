from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"


class Color(Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    PURPLE = "\033[1m\033[34m"
    PINK = "\033[35m"
    CYAN = "\033[1m\033[96m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ENDC = "\033[0m"


MAX_VALUE_LENGTH_IN_TABLES = 50
