import random
import time
from time import time

import pygame.sprite
from maze.cell import Cell


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

    def clear(self):
        for column in self.cells:
            for cell in column:
                cell.mark_as_open()

    def __populate_cells__(self):
        unvisited_cells = set([cell for column in self.cells for cell in column])
        stack = []
        current = self.cells[0][0]

        while unvisited_cells:
            current.mark_as_open()
            if current in unvisited_cells:
                unvisited_cells.remove(current)

            neighbors = current.get_unvisited_neighbors()
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

                self.cells[i][j].neighbors = [self.cells[coords[0]][coords[1]] for coords in n if coords is not None]

    def __all_cells_visited__(self):
        for i in self.cells:
            for j in i:
                if j.state == Cell.State.WALL:
                    return False

        return True