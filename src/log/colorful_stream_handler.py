import logging
from typing import Final, override, Any, LiteralString
import colorama

logging.LoggerAdapter
class ColorfulStreamHandler(logging.StreamHandler):
    _logFormat: Final[LiteralString] = '[%(levelname)s] [%(asctime)s] (%(module)s:%(name)s:%(funcName)s) | %(message)s'
    
    @staticmethod
    def _styleRecord(logRecord: logging.LogRecord) -> logging.LogRecord:
        log_message = str(logRecord.msg)
        styleMods = ColorfulStreamHandler._getLogRecordStyle(logRecord)
        logRecord.msg = ''.join([*styleMods, log_message])
        return logRecord
    
    @staticmethod
    def _getLogRecordStyle(record: logging.LogRecord) -> list[str]:
        match (record.levelno):
            case logging.CRITICAL:
                return [colorama.Style.BRIGHT, colorama.Back.RED, colorama.Fore.WHITE]
            case logging.ERROR:
                return [colorama.Style.BRIGHT, colorama.Back.BLACK, colorama.Fore.RED]
            case logging.WARNING:
                return [colorama.Style.BRIGHT, colorama.Back.BLACK, colorama.Fore.YELLOW]
            case logging.INFO:
                return [colorama.Style.NORMAL, colorama.Back.BLACK, colorama.Fore.WHITE]
            case logging.DEBUG:
                return [colorama.Style.DIM, colorama.Back.BLACK, colorama.Fore.WHITE]
            case _:
                raise ValueError(f'No styling found for {record}')
            
    @override
    def __init__(self, stream: Any):
        super().__init__(stream)
        super().set_name(self.__qualname__)
        super().setFormatter(logging.Formatter(self._logFormat))
        colorama.just_fix_windows_console()
    
    @override
    def emit(self, record):
        super().emit(ColorfulStreamHandler._styleRecord(record))