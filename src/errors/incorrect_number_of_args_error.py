from typing import override, Any

class IncorrectNumberOfArgsError(Exception):
    @override
    def __init__(self, expected: int, received: int, *args: object) -> None:
        super().__init__(args)
        self._expected = expected
        self._received = received
        
    @override
    def __str__(self):
        return f'Expected ({self._expected}), got ({self._received})'
    
    @override
    def __repr__(self):
        return IncorrectNumberOfArgsError.__name__ \
            + f'({self._expected, self._received})'
