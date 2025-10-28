"""
Basic pygame type stubs for pylance compatibility.
This is a minimal stub file to prevent import resolution warnings.
"""

from typing import Any, Tuple, Union, Optional, Sequence

# Basic pygame types
Color = Union[Tuple[int, int, int], Tuple[int, int, int, int], str, int]
ColorValue = Color
Coordinate = Union[Tuple[float, float], Sequence[float]]

class Surface:
    def __init__(self, size: Tuple[int, int], flags: int = 0, depth: int = 0) -> None: ...
    def get_rect(self) -> 'Rect': ...
    def blit(self, source: 'Surface', dest: Union[Coordinate, 'Rect'], area: Optional['Rect'] = None) -> 'Rect': ...
    def convert(self) -> 'Surface': ...
    def convert_alpha(self) -> 'Surface': ...

class Rect:
    x: int
    y: int
    width: int
    height: int

    def __init__(self, left: int, top: int, width: int, height: int) -> None: ...

class Clock:
    def tick(self, framerate: int = 0) -> int: ...

# pygame.event module
class event:
    class Event:
        type: int
        button: int
        pos: Tuple[int, int]
        key: int

    @staticmethod
    def get() -> list[Event]: ...
    @staticmethod
    def pump() -> None: ...

# pygame.display module
class display:
    @staticmethod
    def set_mode(size: Tuple[int, int], flags: int = 0, depth: int = 0) -> Surface: ...
    @staticmethod
    def update(rectangle: Union['Rect', list['Rect'], None] = None) -> None: ...
    @staticmethod
    def set_caption(title: str) -> None: ...

# pygame.draw module
class draw:
    @staticmethod
    def rect(surface: Surface, color: ColorValue, rect: Union['Rect', Tuple[int, int, int, int]], width: int = 0) -> 'Rect': ...

# pygame.key module
class key:
    @staticmethod
    def set_repeat(delay: int = 0, interval: int = 0) -> None: ...

# pygame.time module
class time:
    @staticmethod
    def Clock() -> Clock: ...

# pygame.font module
class Font:
    def __init__(self, filename: Optional[str], size: int) -> None: ...
    def render(self, text: str, antialias: bool, color: ColorValue) -> Surface: ...

class font:
    @staticmethod
    def Font(filename: Optional[str], size: int) -> Font: ...
    @staticmethod
    def get_init() -> bool: ...

# pygame.locals module - expose as submodule
from . import locals

# pygame.locals constants also available at module level
QUIT: int
KEYDOWN: int
MOUSEBUTTONDOWN: int
HWSURFACE: int
DOUBLEBUF: int
K_1: int
K_2: int
K_3: int
K_z: int
K_f: int
K_p: int
K_m: int
K_c: int
K_x: int
K_SPACE: int
K_d: int
K_a: int
K_s: int
K_w: int
K_RIGHT: int
K_LEFT: int
K_DOWN: int
K_UP: int
K_v: int
K_b: int
K_q: int
K_ESCAPE: int

def init() -> None: ...
def quit() -> None: ...