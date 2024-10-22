import functools
import logging
from typing import Callable, Optional
from time import time

def timed[**P, R](timer_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(f)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time()
            result = f(*args, **kwargs)
            stop = time()

            logging.debug(f'[{timer_name}] Completed in {stop - start}s')
            return result

        return inner

    return decorator

