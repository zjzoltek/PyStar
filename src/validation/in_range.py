from validation.condition import Condition
from typing import Any, override, Optional, TypedDict
from errors import ArgOutOfRangeError

class ValueRange(TypedDict, total=False):
    minimum: Any
    maximum: Any
    unboundedMin: bool
    unboundedMax: bool
    inclusiveMin: bool
    inclusiveMax: bool
    
class InRange(Condition[Any, ArgOutOfRangeError]):
    def __init__(self, r: ValueRange) -> None:
        assert (r['minimum'] is not None) ^ (r['unboundedMin'] is True), 'A minimum or unbounded minimum must be specified, but not both'
        assert (r['maximum'] is not None) ^ (r['unboundedMax'] is True), 'A maximum or unbounded maximum must be specified, but not both'
        self._r = r
        
    @override
    def test(self, value: Any) -> Optional[ArgOutOfRangeError]:
        too_small = self._r['minimum'] and (value < self._r['minimum'] or (value == self._r['minimum'] and not self._r['inclusiveMin']))
        too_large = self._r['maximum'] and (value < self._r['maximum'] or (value == self._r['maximum'] and not self._r['inclusiveMax']))
        if too_small or too_large:
            return ArgOutOfRangeError(**self._r)

        return None