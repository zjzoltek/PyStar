from typing import Optional, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar('T')
R = TypeVar('R', bound=Exception, covariant=True)

class Condition(ABC, Generic[T, R]):
    @abstractmethod
    def test(self, value: T) -> Optional[R]:
        raise NotImplementedError()

    def transform(self, value: T) -> object:
        return value

