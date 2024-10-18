from typing import override, Optional, Any

class ArgOutOfRangeError(Exception):
    _MESSAGE_FMT = 'Out of range: {range}'
    
    def __init__(self, minimum: Optional[Any] = None, maximum: Optional[Any] = None, \
        unboundedMin: bool = False, unboundedMax: bool = False,
        inclusiveMin: bool = False, inclusiveMax: bool = False, *args: object) -> None:
        super().__init__(args)
        assert((minimum is not None) ^ (unboundedMin is not None))
        assert((maximum is not None) ^ (unboundedMax is not None))
        self._min = minimum
        self._max = maximum
        self._unboundedMin = unboundedMin
        self._unboundedMax = unboundedMax
        self._inclusiveMin = inclusiveMin
        self._inclusiveMax = inclusiveMax
    
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
        
        if self._unboundedMin or not self._inclusiveMin:
            left_bracket = '('
            
        if self._unboundedMax or not self._inclusiveMax:
            right_bracket = ')'
        
        return '{left_bracket}{min},{max}{right_bracket}' \
                .format(left_bracket=left_bracket, min=self._min, \
                    max=self._max, right_bracket=right_bracket)
        