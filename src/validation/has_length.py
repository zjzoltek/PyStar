from validation.condition import Condition
from typing import Sequence, override, Optional, Any
from errors import IncorrectNumberOfArgsError

class HasLength(Condition[Sequence[Any], IncorrectNumberOfArgsError]):
    def __init__(self, requiredLength):
        self._requiredLength = requiredLength
        
    @override
    def test(self, value: Sequence[Any]) -> Optional[IncorrectNumberOfArgsError]:
        actualLength = len(value)
        if actualLength != self._requiredLength:
            return IncorrectNumberOfArgsError(self._requiredLength, actualLength)
        
        return None
    
    @override
    def transform(self, value: Sequence[Any]) -> object:
        if self._requiredLength == 1:
            return value[0]
        
        return value