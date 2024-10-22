from typing import override

from models import ValueRange, INF, unpack


class ArgOutOfRangeError(Exception):
    _MESSAGE_FMT = 'Expected argument to be in range: {range}'
    _INF = '∞'
    
    def __init__(self, r: ValueRange, *args: object) -> None:
        super().__init__(args)
        self._minimum, self._maximum, self._inclusiveMin, self._inclusiveMax = unpack(r)
    
    @override
    def __str__(self):
        return self._MESSAGE_FMT.format(range=self._represent_range())
    
    @override
    def __repr__(self):
        return ArgOutOfRangeError.__name__ \
            + f'({self._represent_range()})'
            
    def _represent_range(self) -> str:
        left_bracket: str = '['
        right_bracket: str = ']'
        
        if self._minimum == INF or not self._inclusiveMin:
            left_bracket = '('
            
        if self._maximum == INF or not self._inclusiveMax:
            right_bracket = ')'
        
        return '{left_bracket}{min},{max}{right_bracket}' \
                .format(left_bracket=left_bracket, \
                    min=self._min or self._INF, \
                    max=self._max or self._INF, \
                    right_bracket=right_bracket)
        