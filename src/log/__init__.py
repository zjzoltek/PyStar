import logging
from collections.abc import Callable
from time import time
from colorful_stream_handler import *

def timed[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time()
        result = f(*args, **kwargs)
        stop = time()

        logging.debug(f'Completed in {stop - start}s')
        return result

    return inner

