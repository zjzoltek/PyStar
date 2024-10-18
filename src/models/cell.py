from dataclasses import dataclass
from typing import Self

from enums import RGB, State
from maze import Maze
from models import Dimensions

type _Cell = Cell

@dataclass
class Cell:
    x: int
    y: int
    dimensions: Dimensions
    maze: Maze
    
    state: State = State.WALL
    neighbors: list[_Cell] = []
  
    def get_color(self) -> RGB:
        return self.state.color()
    
    def has_visited_neighbors(self) -> bool:
        return len([cell for cell in self.neighbors if cell.state == State.OPEN]) > 1

    def is_terminator(self) -> bool:
        return self.state.is_terminator()
    
    def is_transversible(self) -> bool:
        return self.state.is_transversible()
    
    def is_openable(self) -> bool:
        return self.state.is_openable()
    
    def get_unvisited_neighbors(self) -> list[_Cell]:
        return [cell for cell in self.neighbors \
                if cell.state == State.WALL and not cell.has_visited_neighbors()]
    
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
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return False
        
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.__repr__())