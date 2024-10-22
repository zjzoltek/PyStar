from validation.condition import Condition
from typing import Any, override, Optional
from errors import ArgOutOfRangeError

class InRange(Condition[Any, ArgOutOfRangeError]):
    def __init__(self, minimum: Any = None, maximum: Any = None, \
        unboundedMin: bool = False, unboundedMax: bool = False,
        inclusiveMin: bool = False, inclusiveMax: bool = False) -> None:
        assert (minimum is not None) ^ (unboundedMin is True), 'A minimum or unbounded minimum must be specified, but not both'
        assert (maximum is not None) ^ (unboundedMax is True), 'A maximum or unbounded maximum must be specified, but not both'
        self._min = minimum
        self._max = maximum
        self._unboundedMin = unboundedMin
        self._unboundedMax = unboundedMax
        self._inclusiveMin = inclusiveMin
        self._inclusiveMax = inclusiveMax
        
    @override
    def test(self, value: Any) -> Optional[ArgOutOfRangeError]:
        too_small = self._min and (value < self._min or (value == self._min and not self._inclusiveMin))
        too_large = self._max and (value > self._max or (value == self._max and not self._inclusiveMax))
        
        if too_small or too_large:
            return ArgOutOfRangeError(minimum=self._min, maximum=self._max, \
            unboundedMin=self._unboundedMin, unboundedMax=self._unboundedMax, \
                inclusiveMin=self._inclusiveMin, inclusiveMax=self._inclusiveMax)

        return None