import random
import pygame.sprite
from time import time
from threading import Thread


class Maze:
    def __init__(self, board_width, board_height, random_colors=False):
        self.t = Thread()
        self.size = board_width * board_height
        self.width = board_width
        self.height = board_height
        self.cells = None
        self.random_colors = random_colors

    def is_gen_t_alive(self):
        return self.t.isAlive()

    def generate_t(self, seed):
        t = Thread(target=self.generate(seed))
        t.start()
        t.join()

    def generate_box(self, seed, box_size, diagonals):
        b = time()
        stack = []
        random.seed(seed)
        w = self.width / box_size[0]
        h = self.height / box_size[1]
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

        self.cells[0][0].visited = True
        curr_cell = self.cells[0][0]
        while not self.__all_cells_visited__():
            if len(curr_cell.get_unvisited_neighbors(self.cells)) != 0:
                u_n = curr_cell.get_unvisited_neighbors(self.cells)

                cn = u_n[random.randint(0, len(u_n) - 1)]

                stack.append(curr_cell)
                # Implement random colors here
                curr_cell.color = (255, 255, 255)
                cn.color = (255, 255, 255)
                # End
                cn.visited = True
                curr_cell = cn
            elif len(stack) != 0:
                popped = stack.pop()
                curr_cell = popped
            else:
                break

        e = time()
        print("Maze generated in %ds" % (e - b))

    def generate(self, seed, diagonals=False):
        b = time()
        stack = []
        random.seed(seed)
        self.cells = [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]

        for i in range(self.height):
            for j in range(self.width):
                u = (i - 1, j) if 0 < i - 1 < self.height else None
                d = (i + 1, j) if 0 < i + 1 < self.height else None
                r = (i, j + 1) if 0 < j + 1 < self.width else None
                l = (i, j - 1) if 0 < j - 1 < self.width else None

                if diagonals:
                    u_r = (i - 1, j + 1) if 0 < i - 1 < self.height and 0 < j + 1 < self.width else None
                    d_r = (i + 1, j + 1) if 0 < i + 1 < self.height and 0 < j + 1 < self.width else None
                    u_l = (i - 1, j - 1) if 0 < i - 1 < self.height and 0 < j - 1 < self.width else None
                    d_l = (i + 1, j - 1) if 0 < i + 1 < self.height and 0 < j - 1 < self.width else None
                    n = [u, d, l, r, u_r, d_r, u_l, d_l]
                else:
                    n = [u, d, l, r]

                self.cells[i][j].neighbors = [x for x in n if x is not None]

        self.cells[0][0].visited = True
        curr_cell = self.cells[0][0]
        while not self.__all_cells_visited__():
            if len(curr_cell.get_unvisited_neighbors(self.cells)) != 0:
                u_n = curr_cell.get_unvisited_neighbors(self.cells)

                cn = u_n[random.randint(0, len(u_n) - 1)]

                stack.append(curr_cell)
                # Implement random colors here
                curr_cell.color = (255, 255, 255)
                cn.color = (255, 255, 255)
                # End
                cn.visited = True
                curr_cell = cn
            elif len(stack) != 0:
                popped = stack.pop()
                curr_cell = popped
            else:
                break

        e = time()
        print "Maze generated in %ds" % (e - b)

    def __all_cells_visited__(self):
        for i in self.cells:
            for j in i:
                if not j.visited:
                    return False

        return True

    def gen_surf(self):
        surf = pygame.Surface((self.width, self.height))
        pix_arr = pygame.PixelArray(surf)

        for i in range(self.height):
            for j in range(self.width):
                pix_arr[j][i] = self.cells[i][j].color

        del pix_arr
        return surf

    def gen_surf_box(self):
        surf = pygame.Surface((self.width, self.height))

        for y in self.cells:
            for x in y:
                pygame.draw.rect(surf, x.color, (x.x, x.y, x.box[0], x.box[1]))

        return surf

    @staticmethod
    def gen_surf_box_s(cells, width, height):
        surf = pygame.Surface((width, height))

        for y in cells:
            for x in y:
                pygame.draw.rect(surf, x.color, (x.x * x.box[0], x.y*x.box[1], x.box[0], x.box[1]))

        return surf

    @staticmethod
    def gen_surf_s(cells, width, height):
        surf = pygame.Surface((width, height))
        pix_arr = pygame.PixelArray(surf)

        for i in range(height):
            for j in range(width):
                pix_arr[j][i] = cells[i][j].color

        del pix_arr
        return surf


class Cell:
    def __init__(self, x, y, box=None):
        self.visited = False
        self.neighbors = []
        self.x = x
        self.y = y
        self.color = (0, 0, 0)
        self.box = box

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
