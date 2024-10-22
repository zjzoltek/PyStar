from typing import Any, TypedDict, Final, NotRequired

INF: Final[Any] = '∞'

class ValueRange(TypedDict):
    minimum: Any
    maximum: Any
    inclusiveMin: NotRequired[bool]
    inclusiveMax: NotRequired[bool]
    
def unpack(r: ValueRange):
    return (r['minimum'], r['maximum'], r.get('inclusiveMin', False), r.get('inclusiveMax', True))