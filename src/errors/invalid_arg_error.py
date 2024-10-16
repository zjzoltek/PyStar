from typing import override, Optional

class InvalidArgError[E, R](Exception):
    @override
    def __init__(self, *args: object):
        super().__init__(args)
        self._expected: Optional[E] = None
        self._received: Optional[R] = None
        
    @classmethod
    def create(cls, expected: E, received: R, *args: object):
        e = cls(*args)
        e._expected = expected
        e._received = received
        return e

    def __str__(self):
        expected_type = self._expected.__class__.__name__
        received_type = self._received.__class__.__name__
        return f'Expected ({expected_type}), but received \
            ({received_type}) instead: expected={self._expected} \
                actual={self._received}'
    
    def __repr__(self):
        return InvalidArgError.__name__ \
            + f'({self._expected, self._received})'