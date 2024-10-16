from enum import Enum

class Color(Enum):
    START = (0, 0, 255)
    END = (255, 20, 147)
    SEARCHED = (255, 0, 0)
    ROUTE = (0, 255, 0)
    OPEN = (255, 255, 255)
    WALL = (0, 0, 0)
