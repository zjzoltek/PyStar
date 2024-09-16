import random
import pygame.sprite
from time import time

class Maze:
    @staticmethod
    def gen_surf_box(cells, width, height):
        surf = pygame.Surface((width, height))

        for y in cells:
            for x in y:
                pygame.draw.rect(surf, x.color, (x.x * x.box[0], x.y*x.box[1], x.box[0], x.box[1]))

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

    def __populate_cells__(self):
        stack = []
        current = self.cells[0][0]

        while not self.__all_cells_visited__():
            current.visited = True
            current.color = (255, 255, 255)
            stack.append(current)

            neighbors = current.get_unvisited_neighbors(self.cells)
            if len(neighbors) > 0:
                current = neighbors[random.randint(0, len(neighbors) - 1)]
            elif len(stack) > 0:
                current = stack.pop()
            else:
                break

    def __generate_cells__(self, box_size, diagonals):
        w = int(self.width / box_size[0])
        h = int(self.height / box_size[1])
        self.cells = [[Cell(x, y)
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
                if not j.visited:
                    return False

        return True

class Cell:
    def __init__(self, x, y):
        self.visited = False
        self.neighbors = []
        self.x = x
        self.y = y
        self.color = (0, 0, 0)

    def get_neighbors(self, cells):
        n = []
        for i in self.neighbors:
            n.append(cells[i[0]][i[1]])

        return n

    def has_visited_neighbors(self, cells):
        if len([x for x in self.get_neighbors(cells) if x.visited]) > 1:
            return True

    def get_unvisited_neighbors(self, cells):
        return [x for x in self.get_neighbors(cells) if not x.visited and not x.has_visited_neighbors(cells)]


def random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
