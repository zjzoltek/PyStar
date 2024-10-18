from typing import override, Any

class InvalidArgTypeError(Exception):
    @override
    def __init__(self, expected: type, received: Any, *args: object) -> None:
        super().__init__(args)
        self._expected = expected
        self._received = type(received)

    @override
    def __str__(self):
        received_type = self._received.__class__.__name__
        return f'Expected ({self._expected}), but received \
            ({received_type}) instead'
    
    @override
    def __repr__(self):
        return InvalidArgTypeError.__name__ \
            + f'({self._expected, self._received})'