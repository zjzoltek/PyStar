from validation.condition import Condition
from typing import Any, override, Optional
from errors import ArgOutOfRangeError

class InRange(Condition[Any, ArgOutOfRangeError]):
    def __init__(self, minimum: Any = None, maximum: Any = None, \
        unboundedMin: bool = False, unboundedMax: bool = False,
        inclusiveMin: bool = False, inclusiveMax: bool = False) -> None:
        assert((minimum is not None) ^ (unboundedMin is True))
        assert((maximum is not None) ^ (unboundedMax is True))
        self._min = minimum
        self._max = maximum
        self._unboundedMin = unboundedMin
        self._unboundedMax = unboundedMax
        self._inclusiveMin = inclusiveMin
        self._inclusiveMax = inclusiveMax
        
    @override
    def test(self, value: Any) -> Optional[ArgOutOfRangeError]:
        if self._min:
            if value < self._min or (value <= self._min and self._inclusiveMin):
                raise ArgOutOfRangeError(minimum=self._min, maximum=self._max, \
                    unboundedMin=self._unboundedMin, unboundedMax=self._unboundedMax, \
                        inclusiveMin=self._inclusiveMin, inclusiveMax=self._inclusiveMax)
        
        return None