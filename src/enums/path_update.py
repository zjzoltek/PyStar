from enum import Enum

from enums.color import *


class PathUpdate(Enum):
    SEARCHED = 1
    COMPLETE = 2
    ROUTE = 3