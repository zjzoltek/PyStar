from typing import Any, Collection, Optional, override, Iterable
from validation.condition import Condition
from errors import InvalidArgValueError

class IsIn(Condition[Any, InvalidArgValueError]):
    def __init__(self, values: Collection[Any]):
        self._values = values
        
    @override
    def test(self, value: Any) -> Optional[InvalidArgValueError]:
        if isinstance(value, Iterable):
            for v in value:
                if v not in self._values:
                    return InvalidArgValueError(self._values, v)
        else:
            if value not in self._values:
                return InvalidArgValueError(self._values, value)
            
        return None