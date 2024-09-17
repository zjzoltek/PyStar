import random
from enum import Enum
from time import time

import pygame.sprite


class Maze:
    @staticmethod
    def gen_surf_box(cells, width, height):
        surf = pygame.Surface((width, height))

        for column in cells:
            for row in column:
                pygame.draw.rect(surf, row.get_color(), (row.x * row.dimensions[0], row.y*row.dimensions[1], row.dimensions[0], row.dimensions[1]))

        return surf

    def __init__(self, board_width, board_height):
        self.size = board_width * board_height
        self.width = board_width
        self.height = board_height
        self.cells = None

    def generate(self, box_size, diagonals):
        print("Generating maze . . .")

        start_time = time()
        self.__generate_cells__(box_size, diagonals)
        self.__populate_cells__()
        end_time = time()

        print("Maze generated in {}s".format(end_time - start_time))

    def visit_all_cells(self):
        for column in self.cells:
            for row in column:
                row.state = Cell.State.VISITED

    def __populate_cells__(self):
        unvisited_cells = set([cell for column in self.cells for cell in column])
        stack = []
        current = self.cells[0][0]

        while unvisited_cells:
            current.state = Cell.State.VISITED
            if current in unvisited_cells:
                unvisited_cells.remove(current)

            neighbors = current.get_unvisited_neighbors(self.cells)
            if len(neighbors) > 0:
                stack.append(current)
                current = neighbors[random.randint(0, len(neighbors) - 1)]
            elif len(stack) > 0:
                current = stack.pop()
            else:
                break

    def __generate_cells__(self, box_size, diagonals):
        w = int(self.width / box_size[0])
        h = int(self.height / box_size[1])
        self.cells = [[Cell(x, y, box_size)
                      for x in range(w)]
                      for y in range(h)]
        for i in range(h):
            for j in range(w):
                u = (i - 1, j) if 0 < i - 1 < h else None
                d = (i + 1, j) if 0 < i + 1 < h else None
                r = (i, j + 1) if 0 < j + 1 < w else None
                l = (i, j - 1) if 0 < j - 1 < w else None

                if diagonals:
                    u_r = (i - 1, j + 1) if 0 < i - 1 < h and 0 < j + 1 < w else None
                    d_r = (i + 1, j + 1) if 0 < i + 1 < h and 0 < j + 1 < w else None
                    u_l = (i - 1, j - 1) if 0 < i - 1 < h and 0 < j - 1 < w else None
                    d_l = (i + 1, j - 1) if 0 < i + 1 < h and 0 < j - 1 < w else None
                    n = [u, d, l, r, u_r, d_r, u_l, d_l]
                else:
                    n = [u, d, l, r]

                self.cells[i][j].neighbors = [x for x in n if x is not None]

    def __all_cells_visited__(self):
        for i in self.cells:
            for j in i:
                if j.state == Cell.State.NOT_VISITED:
                    return False

        return True

class Cell:
    class State(Enum):
        START = 1
        END = 2
        SEARCHED = 3
        PATH = 4
        VISITED = 5
        NOT_VISITED = 6

    class Color(Enum):
        START = (0, 0, 255)
        END = (255, 20, 147)
        SEARCHED = (255, 0, 0)
        PATH = (0, 255, 0)
        VISITED = (255, 255, 255)
        NOT_VISITED = (0, 0, 0)
    
    def __init__(self, x, y, dimensions):
        self.neighbors = []
        self.x = x
        self.y = y
        self.state = Cell.State.NOT_VISITED
        self.dimensions = dimensions

    def get_color(self):
        match self.state:
            case Cell.State.START:
                return Cell.Color.START.value
            case Cell.State.END:
                return Cell.Color.END.value
            case Cell.State.SEARCHED:
                return Cell.Color.SEARCHED.value
            case Cell.State.PATH:
                return Cell.Color.PATH.value
            case Cell.State.VISITED:
                return Cell.Color.VISITED.value
            case Cell.State.NOT_VISITED:
                return Cell.Color.NOT_VISITED.value
            case _:
                raise ValueError('Invalid state')
    
    def get_neighbors(self, cells):
        n = []
        for i in self.neighbors:
            n.append(cells[i[0]][i[1]])

        return n

    def has_visited_neighbors(self, cells):
        if len([x for x in self.get_neighbors(cells) if x.state == Cell.State.VISITED]) > 1:
            return True

    def get_unvisited_neighbors(self, cells):
        return [x for x in self.get_neighbors(cells) if x.state == Cell.State.NOT_VISITED and not x.has_visited_neighbors(cells)]
    
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


