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
    
    def __init__(self, x, y, dimensions):
        self.neighbors = []
        self.x = x
        self.y = y
        self.__state = Cell.State.WALL
        self.__needs_write = True
        self.dimensions = dimensions
        self.neighors = None

    def get_color(self):
        match self.__state:
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
        if len([cell for cell in self.neighbors if cell.__state == Cell.State.OPEN]) > 1:
            return True

    def is_terminator(self):
        return self.__state.is_terminator()
    
    def is_transversible(self):
        return self.__state.is_transversible()
    
    def is_openable(self):
        return self.__state.is_openable()
    
    def get_unvisited_neighbors(self):
        return [cell for cell in self.neighbors if cell.__state == Cell.State.WALL and not cell.has_visited_neighbors()]
    
    def mark_as_start(self):
        self.__set_state(Cell.State.START)
        
    def mark_as_end(self):
        self.__set_state(Cell.State.END)
        
    def mark_as_searched(self):
        self.__set_state(Cell.State.SEARCHED)
        
    def mark_as_route(self):
        self.__set_state(Cell.State.ROUTE)
    
    def mark_as_open(self):
        self.__set_state(Cell.State.OPEN)
    
    def mark_as_wall(self):
        self.__set_state(Cell.State.WALL)
    
    def is_dirty(self):
        return self.__needs_write
    
    def reset_dirty_bit(self):
        self.__needs_write = False
        
    def __set_state(self, state):
        if (state != self.__state):
            self.__needs_write = True
            
        self.__state = state
        
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


