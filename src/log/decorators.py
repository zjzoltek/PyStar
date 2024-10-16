import functools
import logging
from collections.abc import Callable
from time import time

def timed[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(f)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time()
        result = f(*args, **kwargs)
        stop = time()

        logging.debug(f'Completed in {stop - start}s')
        return result

    return inner

