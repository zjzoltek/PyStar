from validation.condition import Condition
from typing import Collection, override, Optional, Any
from errors import IncorrectNumberOfArgsError

class HasLength(Condition[Collection[Any], IncorrectNumberOfArgsError]):
    def __init__(self, requiredLength):
        self._requiredLength = requiredLength
        
    @override
    def test(self, value: Collection[Any]) -> Optional[IncorrectNumberOfArgsError]:
        actualLength = len(value)
        if actualLength != self._requiredLength:
            return IncorrectNumberOfArgsError(self._requiredLength, actualLength)
        
        return None