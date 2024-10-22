from enum import Enum

from enums.color import *


class State(Enum):
    START = 1
    END = 2
    SEARCHED = 3
    ROUTE = 4
    OPEN = 5
    WALL = 6
    HIGHLIGHTED = 7

    def is_openable(self) -> bool:
        return self in (State.SEARCHED, State.ROUTE)

    def is_transversible(self) -> bool:
        return self.is_terminator() or self == State.OPEN

    def is_terminator(self) -> bool:
        return self in (State.START, State.END)

    def color(self) -> RGB:
        match self:
            case State.START:
                return Color.START.value
            case State.END:
                return Color.END.value
            case State.SEARCHED:
                return Color.SEARCHED.value
            case State.ROUTE:
                return Color.ROUTE.value
            case State.OPEN:
                return Color.OPEN.value
            case State.WALL:
                return Color.WALL.value
            case _:
                raise ValueError('Invalid state')