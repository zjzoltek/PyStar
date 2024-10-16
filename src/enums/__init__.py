from enum import Enum


class Color(Enum):
    START = (0, 0, 255)
    END = (255, 20, 147)
    SEARCHED = (255, 0, 0)
    ROUTE = (0, 255, 0)
    OPEN = (255, 255, 255)
    WALL = (0, 0, 0)

class State(Enum):
    START = 1
    END = 2
    SEARCHED = 3
    ROUTE = 4
    OPEN = 5
    WALL = 6

    def is_openable(self) -> bool:
        return self in (State.SEARCHED, State.ROUTE)

    def is_transversible(self) -> bool:
        return self.is_terminator() or self == State.OPEN

    def is_terminator(self) -> bool:
        return self in (State.START, State.END)

    def color(self) -> tuple[int, int, int]:
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