from enum import Enum


class Cell:
    class State(Enum):
        START = 1
        END = 2
        SEARCHED = 3
        ROUTE = 4
        OPEN = 5
        WALL = 6
        
        def is_openable(self):
            return self in (Cell.State.SEARCHED, Cell.State.ROUTE)
        
        def is_transversible(self):
            return self.is_terminator() or self == Cell.State.OPEN

        def is_terminator(self):
            return self in (Cell.State.START, Cell.State.END)
        
    class Color(Enum):
        START = (0, 0, 255)
        END = (255, 20, 147)
        SEARCHED = (255, 0, 0)
        ROUTE = (0, 255, 0)
        OPEN = (255, 255, 255)
        WALL = (0, 0, 0)
    
    def __init__(self, x, y, dimensions, on_state_change=None):
        self.neighbors = []
        self.x = x
        self.y = y
        self.dimensions = dimensions
        self.neighors = None
        self._state = Cell.State.WALL
        self._on_state_change = on_state_change

    def get_color(self):
        match self._state:
            case Cell.State.START:
                return Cell.Color.START.value
            case Cell.State.END:
                return Cell.Color.END.value
            case Cell.State.SEARCHED:
                return Cell.Color.SEARCHED.value
            case Cell.State.ROUTE:
                return Cell.Color.ROUTE.value
            case Cell.State.OPEN:
                return Cell.Color.OPEN.value
            case Cell.State.WALL:
                return Cell.Color.WALL.value
            case _:
                raise ValueError('Invalid state')
    
    def has_visited_neighbors(self):
        if len([cell for cell in self.neighbors if cell._state == Cell.State.OPEN]) > 1:
            return True

    def is_terminator(self):
        return self._state.is_terminator()
    
    def is_transversible(self):
        return self._state.is_transversible()
    
    def is_openable(self):
        return self._state.is_openable()
    
    def get_unvisited_neighbors(self):
        return [cell for cell in self.neighbors if cell._state == Cell.State.WALL and not cell.has_visited_neighbors()]
    
    def mark_as_start(self):
        self._set_state(Cell.State.START)
        
    def mark_as_end(self):
        self._set_state(Cell.State.END)
        
    def mark_as_searched(self):
        self._set_state(Cell.State.SEARCHED)
        
    def mark_as_route(self):
        self._set_state(Cell.State.ROUTE)
    
    def mark_as_open(self):
        self._set_state(Cell.State.OPEN)
    
    def mark_as_wall(self):
        self._set_state(Cell.State.WALL)
    
    def _set_state(self, state):
        if self._state != state and self._on_state_change != None:
            self._on_state_change(state)
        self._state = state
        
    def __repr__(self):
        return "Cell(%s, %s)" % (self.x, self.y)
    
    def __eq__(self, other):
        if not isinstance(other, Cell):
            return False
        
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.__repr__())


