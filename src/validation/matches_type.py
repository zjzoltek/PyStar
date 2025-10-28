from typing import override, Any, Optional
from errors import InvalidArgTypeError
from validation.condition import Condition

class MatchesType(Condition[Any, InvalidArgTypeError]):
    def __init__(self, obj: Any) -> None:
        self._expectedType = type(obj)

    @override
    def test(self, value: Any) -> Optional[InvalidArgTypeError]:
        try:
            self._expectedType(value)
        except Exception:
            return InvalidArgTypeError(self._expectedType, value)

        return None

    @override
    def transform(self, value: Any) -> object:
        return self._expectedType(value)
        