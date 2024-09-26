from enum import Enum

import colorama


class Logger:
    class Level(Enum):
        DEBUG = 0
        INFO = 1
        WARN = 2
        SEVERE = 3
        
    def __init__(self, emitter=print, default_log_level=None):
        self._log_emitter = emitter
        self._default_log_level = default_log_level if default_log_level is not None else Logger.Level.DEBUG
        