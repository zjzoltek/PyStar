from enum import Enum

import colorama


class Logger:
    class Level(Enum):
        DEBUG = 0
        INFO = 1
        WARN = 2
        ERROR = 3
        
        def get_term_colors(self):
            match self:
                case Logger.Level.DEBUG:
                    return (colorama.Back.BLACK, colorama.Fore.BLUE)
                case Logger.Level.INFO:
                    return (colorama.Back.BLACK, colorama.Fore.WHITE)
                case Logger.Level.WARN:
                    return (colorama.Back.BLACK, colorama.Fore.YELLOW)
                case Logger.Level.ERROR:
                    return (colorama.Back.BLACK, colorama.Fore.RED)
                case _:
                    raise ValueError(f'Unrecognized log level: {self}')

    @staticmethod
    def _reset():
        print(colorama.Style.RESET_ALL)

    @staticmethod
    def _level(content, level):
        (bg, fg) = level.get_term_colors()
        
        return bg + fg + content
    
    def __init__(self, emitter=print, default_log_level=None, sep=' | '):
        self._log_emitter = emitter
        self._default_log_level = default_log_level if default_log_level is not None else Logger.Level.DEBUG
        self._sep = sep
    
    def debug(self, content, **kwargs):
        self._log(content, Logger.Level.DEBUG, kwargs)
    
    def debug(self, content, **kwargs):
        self._log(content, Logger.Level.INFO, kwargs)
        
    def debug(self, content, **kwargs):
        self._log(content, Logger.Level.WARN, kwargs)
        
    def debug(self, content, **kwargs):
        self._log(content, Logger.Level.ERROR, kwargs)
        
    def _log(self, content, level, **kwargs):
        if isinstance(content, type([])):
            content = self._sep.join(content)
            
        if len(kwargs):
            content = content.format(kwargs)
            
        print(self._level(content, level))
        self._reset()
    

        