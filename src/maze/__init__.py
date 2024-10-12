import random
from dataclasses import dataclass
from enum import Enum

import pygame.sprite

from log import timed

type _Cell = Cell

class Maze:
    def __init__(self, *, board_width: int, board_height: int) -> None:
        self.width: int = board_width
        self.height: int = board_height
        self._cells: list[list[Cell]] = []
        self._needs_write: bool = False
    
    @timed
    def generate(self, *, box_size: tuple[int, int], diagonals: bool) -> None:
        self._generate_cells(box_size, diagonals)
        self._populate_cells()

    def draw_surf(self, *, width: int, height: int) -> pygame.Surface | None:
        if not self._needs_write:
            return

        surf = pygame.Surface((width, height))
        for column in self._cells:
            for cell in column:
                pygame.draw.rect(surf, cell.get_color(), \
                    (cell.x * cell.dimensions[0], \
                    cell.y*cell.dimensions[1], \
                    cell.dimensions[0], cell.dimensions[1]))
        
        self._needs_write = False
        
        return surf

    def reopen_cells(self, *, openable_only: bool=True) -> None:
        for column in self._cells:
            for cell in column:
                if cell.is_openable() or not openable_only:
                    cell.mark_as_open()
         
    def get_random_transversible_point(self) -> _Cell:
        all_cells = [row for row in self._cells for cell in row if cell.is_transversible()]
        random.shuffle(all_cells)
        return random.choice(all_cells)
       
    def get_cell(self, *, x: int, y: int) -> _Cell | None:
        for row in self._cells:
            for cell in row:
                if cell.x == int((x / self.height)) \
                        and cell.y == int((y / self.width)):
                    return cell
                
    def on_cell_state_change(self) -> None:
        self._needs_write = True
       
    def _populate_cells(self) -> None:
        unvisited_cells = set([cell for column in self._cells for cell in column])
        stack: list[Cell] = []
        current = self._cells[0][0]

        while unvisited_cells:
            current.mark_as_open()
            if current in unvisited_cells:
                unvisited_cells.remove(current)

            neighbors = current.get_unvisited_neighbors()
            if len(neighbors) > 0:
                stack.append(current)
                current = random.choice(neighbors)
            elif len(stack) > 0:
                current = stack.pop()
            else:
                break

    def _generate_cells(self, box_size: tuple[int, int], diagonals: bool) -> None:
        w = int(self.width / box_size[0])
        h = int(self.height / box_size[1])
        self._cells = [[Cell(row, column, box_size, self)
                      for row in range(h)]
                      for column in range(w)]
        
        for row in range(h):
            for column in range(w):
                u = (row - 1, column) if 0 <= row - 1 < h else None
                d = (row + 1, column) if 0 <= row + 1 < h else None
                r = (row, column + 1) if 0 <= column + 1 < w else None
                l = (row, column - 1) if 0 <= column - 1 < w else None

                if diagonals:
                    u_r = (row - 1, column + 1) if 0 <= row - 1 < h and 0 <= column + 1 < w else None
                    d_r = (row + 1, column + 1) if 0 <= row + 1 < h and 0 <= column + 1 < w else None
                    u_l = (row - 1, column - 1) if 0 <= row - 1 < h and 0 <= column - 1 < w else None
                    d_l = (row + 1, column - 1) if 0 <= row + 1 < h and 0 <= column - 1 < w else None
                    n = [u, d, l, r, u_r, d_r, u_l, d_l]
                else:
                    n = [u, d, l, r]

                self._cells[row][column].neighbors = [self._cells[coords[0]][coords[1]] for coords in n if coords]

        
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
   
@dataclass
class Cell:
    neighbors: list[_Cell]
    x: int
    y: int
    dimensions: tuple[int, int]
    state: State = State.WALL
    maze: type[Maze]
  
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
    
    def mark_as_start(self) -> None:
        self._set_state(State.START)
        
    def mark_as_end(self) -> None:
        self._set_state(State.END)
        
    def mark_as_searched(self) -> None:
        self._set_state(State.SEARCHED)
        
    def mark_as_route(self) -> None:
        self._set_state(State.ROUTE)
    
    def mark_as_open(self) -> None:
        self._set_state(State.OPEN)
    
    def mark_as_wall(self) -> None:
        self._set_state(State.WALL)
    
    def _set_state(self, state: State) -> None:
        if self.state != state:
            self._maze.on_cell_state_change()
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