from typing import Optional
from abc import ABC, abstractmethod


class Condition[T, R: Exception](ABC):
    @abstractmethod
    def test(self, value: T) -> Optional[R]:
        raise NotImplementedError()
    
    def transform(self, value: T) -> object:
        return value

