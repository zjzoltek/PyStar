import logging
import sys
from typing import ClassVar, Concatenate
from time import time
from collections.abc import Callable

class Logger:
    _initialized: ClassVar[bool] = False
    
    def init() -> None:
        if Logger._initialized:
            raise RuntimeError('Logger already initialized')
        
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter('[%(levelname)s] [%(name)s] [%(asctime)s] | %(message)s')
        handler.setFormatter(formatter)
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])
        Logger._initialized = True
        
def timed[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time()
        result = f(*args, **kwargs)
        stop = time()
        
        logging.debug(f'%s completed in {stop - start}', args=[f.__name__])
        return result

    return inner