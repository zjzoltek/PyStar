import random
import time
from time import time

import pygame.sprite
from maze.cell import Cell


class Maze:
    def __init__(self, board_width, board_height):
        self.size = board_width * board_height
        self.width = board_width
        self.height = board_height
        self._cells = []
        self._needs_write = False
        
    def generate(self, box_size, diagonals):
        print("Generating maze . . .")

        start_time = time()
        self._generate_cells(box_size, diagonals)
        self._populate_cells()
        end_time = time()

        print("Maze generated in {}s".format(end_time - start_time))

    def draw_surf(self, width, height):
        if not self._needs_write:
            return

        surf = pygame.Surface((width, height))
        for column in self._cells:
            for cell in column:
                pygame.draw.rect(surf, cell.get_color(), (cell.x * cell.dimensions[0], cell.y*cell.dimensions[1], cell.dimensions[0], cell.dimensions[1]))
        
        self._needs_write = False
        
        return surf

    def reopen_cells(self, openable_only=True):
        for column in self._cells:
            for cell in column:
                if cell.is_openable() or not openable_only:
                    cell.mark_as_open()
         
    def get_random_transversible_point(self):
        all_cells = [row for column in self._cells for row in column if row.is_transversible()]
        random.shuffle(all_cells)
        return all_cells[random.randint(0, len(all_cells)-1)]
       
    def get_cell(self, x, y):
        for array in self._cells:
            for cell in array:
                if cell.x == int((x / self.width)) \
                        and cell.y == int((y / self.height)):
                    return cell
                
    def _populate_cells(self):
        unvisited_cells = set([cell for column in self._cells for cell in column])
        stack = []
        current = self._cells[0][0]

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

    def _generate_cells(self, box_size, diagonals):
        w = int(self.width / box_size[0])
        h = int(self.height / box_size[1])
        self._cells = [[Cell(x, y, box_size, self._on_cell_state_change)
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

                self._cells[i][j].neighbors = [self._cells[coords[0]][coords[1]] for coords in n if coords is not None]
    
    def _on_cell_state_change(self, _):
        self.needs_write = True