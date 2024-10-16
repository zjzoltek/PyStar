from dataclasses import dataclass
from typing import Optional, Self

from enums import Color, State
from maze import Maze

type _Cell = Cell

@dataclass
class Cell:
    neighbors: list[_Cell]
    x: int
    y: int
    dimensions: tuple[int, int]
    state: State = State.WALL
    maze: Maze
  
    def get_color(self) -> Color:
        return self.state.color()
    
    def has_visited_neighbors(self) -> bool:
        return len([cell for cell in self.neighbors if cell._state == State.OPEN]) > 1

    def is_terminator(self) -> bool:
        return self.state.is_terminator()
    
    def is_transversible(self) -> bool:
        return self.state.is_transversible()
    
    def is_openable(self) -> bool:
        return self.state.is_openable()
    
    def get_unvisited_neighbors(self) -> list[_Cell]:
        return [cell for cell in self.neighbors \
                if cell._state == State.WALL and not cell.has_visited_neighbors()]
    
    def mark_as_start(self) -> Self:
        self._set_state(State.START)
        return self
        
    def mark_as_end(self) -> Self:
        self._set_state(State.END)
        return self
        
    def mark_as_searched(self) -> Self:
        self._set_state(State.SEARCHED)
        return self
        
    def mark_as_route(self) -> Self:
        self._set_state(State.ROUTE)
        return self
    
    def mark_as_open(self) -> Self:
        self._set_state(State.OPEN)
        return self
    
    def mark_as_wall(self) -> Self:
        self._set_state(State.WALL)
        return self
    
    def _set_state(self, state: State) -> None:
        if self.state != state:
            self.maze.on_cell_state_change()
        self.state = state
        
    def __repr__(self) -> str:
        return 'Cell(%s, %s)' % (self.x, self.y)
    
    def __eq__(self, other: _Cell) -> bool:
        if not isinstance(other, Cell):
            return False
        
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: _Cell) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.__repr__())

@dataclass(frozen=True)
class Point():
    x: int
    y: int
    
@dataclass
class Dimensions:
    width: int
    height: int

@dataclass
class StartEnd:
    start: Optional[Cell]
    end: Optional[Cell]
    
    def is_empty(self) -> bool:
        return self.start is None and self.end is None
    
    def reset(self) -> None:
        self.start.mark_as_open()
        self.end.mark_as_open()
        self.start = self.end = None
    
    def progress(self, p: Cell) -> None:
        if self.start is not None and self.end is not None:
            self.reset()
        
        if self.start is None:
            self.start = p
        elif self.end is None:
            self.end = p
    
@dataclass(frozen=True)
class Node:
    cell: Cell
    parent: Optional[Cell]
    gCost: float
    hCost: float
    
    @property
    def fCost(self) -> float:
        return self.gCost + self.hCost
    
    def __repr__(self):
        return repr(self.cell)
    
    def __lt__(self, other):
        return self.fCost < other.fCost
    
    def __gt__(self, other):
        return self.fCost > other.fCost
    
    def __le__(self, other):
        return self.fCost <= other.fCost
    
    def __ge__(self, other):
        return self.fCost >= other.fCost
    
    def __eq__(self, other):
        return self.fCost == other.fCost
    
    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return hash(self.__repr__())