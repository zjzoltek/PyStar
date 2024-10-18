from typing import override, Any, Collection

class InvalidArgValueError(Exception):
    @override
    def __init__(self, expected: Collection[Any], received: Any, *args: object) -> None:
        super().__init__(args)
        self._expected = expected
        self._received = received

    @override
    def __str__(self):
        return f'Expected one of {self._expected}, got {self._received}'
    
    @override
    def __repr__(self):
        return InvalidArgValueError.__name__ \
            + f'({self._expected, self._received})'