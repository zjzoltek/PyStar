from typing import Any, Optional, override

from errors import ArgOutOfRangeError
from models import INF, ValueRange, unpack
from validation.condition import Condition


class InRange(Condition[Any, ArgOutOfRangeError]):
    def __init__(self, r: ValueRange) -> None:
        self._minimum, self._maximum, self._inclusiveMin, self._inclusiveMax = unpack(r)
        self._r = r

    @override
    def test(self, value: Any) -> Optional[ArgOutOfRangeError]:
        too_small = self._minimum != INF and (value > self._minimum or (value == self._minimum and not self._inclusiveMin))
        too_large = self._maximum != INF and (value < self._maximum or (value == self._maximum and not self._inclusiveMax))
        if too_small or too_large:
            return ArgOutOfRangeError(**self._r)

        return None