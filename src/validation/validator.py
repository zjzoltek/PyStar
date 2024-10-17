from typing import Optional
from condition import *
from collections.abc import Collection

class Validator[T]:
    def __init__(self, conditions: Collection[Condition[T]]):
        self._conditions: tuple[Condition[T]]  = tuple(conditions)
        
    def validate(value: T) -> Optional[ExceptionGroup]:
        group = ExceptionGroup() 
        