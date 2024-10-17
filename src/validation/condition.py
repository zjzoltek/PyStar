from typing import Callable, Optional

class Condition[T, R: Exception]:
    def __init__(self, condition: Callable[[T], Optional[R]]):
        self._test: Callable[[T], Optional[R]] = condition
    
    @property
    def test(self):
        return self._test
        