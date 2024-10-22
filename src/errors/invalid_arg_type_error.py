from typing import override, Any

class InvalidArgTypeError(Exception):
    @override
    def __init__(self, expected: type, received: Any, *args: object) -> None:
        super().__init__(args)
        self._expected = expected
        self._received = type(received)
    @override
    def __str__(self):
        return f'Expected an argument of type ({self._expected}), but received ' + \
           f'({self._received}) instead'
    
    @override
    def __repr__(self):
        return InvalidArgTypeError.__name__ \
            + f'({self._expected, self._received})'