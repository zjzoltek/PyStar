from typing import override, Any
from errors import InvalidArgTypeError
from validation.condition import Condition

class MatchesType(Condition[Any, InvalidArgTypeError]):
    def __init__(self, obj: Any) -> None:
        self._expectedType = type(obj)
        
    @override
    def test(self, value: Any):
        if value is not self._expectedType:
            return InvalidArgTypeError(self._expectedType, value)