from typing import Any, Collection, Optional, override
from validation.condition import Condition
from errors import InvalidArgValueError

class IsIn(Condition[Any, InvalidArgValueError]):
    def __init__(self, values: Collection[Any]):
        self._values = values
        
    @override
    def test(self, value: Any) -> Optional[InvalidArgValueError]:
        if value not in self._values:
           raise InvalidArgValueError(self._values, value)
        
        return None