from typing import override, Optional

class IncorrectNumberOfArgsError(Exception):
    @override
    def __init__(self, *args: object):
        super().__init__(args)
        self._expected: Optional[int] = None
        self._received: Optional[int] = None
        
    @classmethod
    def create(cls, expected: str, received: str, *args: object):
        e = cls(args)
        e._expected = expected
        e._received = received
        return e

    def __str__(self):
        return f'Expected ({self._expected}), got ({self._received})'
    
    def __repr__(self):
        return IncorrectNumberOfArgsError.__name__ \
            + f'({self._expected, self._received})'
