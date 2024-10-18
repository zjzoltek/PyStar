from typing import Optional
from validation.condition import *

class Validator[T]:
    def __init__(self, *conditions: Condition[T, Exception]) -> None:
        self._conditions: tuple[Condition[T, Exception], ...]  = tuple(conditions)
        
    def validate(self, value: T) -> None:
        exceptions: list[Exception] = []
        for c in self._conditions:
            optionalException: Optional[Exception] = c.test(value)
            if optionalException:
                exceptions.append(optionalException)
        
        if exceptions:
            raise ExceptionGroup('Validation Error', exceptions)
        
        return None
        
        