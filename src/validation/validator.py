from typing import Optional, Any, TypeVar, Generic
from validation.condition import Condition

T = TypeVar('T')

class Validator(Generic[T]):
    def __init__(self, *conditions: Condition[T, Exception]) -> None:
        self._conditions: tuple[Condition[T, Exception], ...] = tuple(conditions)

    def validate(self, value: T) -> Any:
        v: Any = value
        for c in self._conditions:
            optionalException: Optional[Exception] = c.test(v)
            if optionalException:
                raise optionalException
            else:
                v = c.transform(v)

        return v