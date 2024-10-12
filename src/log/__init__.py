import logging
import sys
from collections.abc import Callable
from time import time
from typing import ClassVar

import colorama


class Logger:
    _initialized: ClassVar[bool] = False
    
    @classmethod
    def init(cls) -> None:
        if cls._initialized:
            raise RuntimeError('Logger already initialized')
        
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] (%(module)s:%(name)s:%(funcName)s) | %(message)s')
        handler.setFormatter(formatter)
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])
        cls._initialized = True
    
def timed[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time()
        result = f(*args, **kwargs)
        stop = time()

        logging.debug(f'Completed in {stop - start}s')
        return result

    return inner