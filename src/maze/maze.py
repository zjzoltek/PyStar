import random
import time

import pygame.sprite
from cell import *


class Maze:
    def __init__(self, board_width, board_height):
        self.size = board_width * board_height
        self.width = board_width
        self.height = board_height
        self._cells = []
        self._needs_write = False
        
    def generate(self, box_size, diagonals):
        print('Generating maze . . .')

        start_time = time.time()
        self._generate_cells(box_size, diagonals)
        self._populate_cells()
        end_time = time.time()

        print('Maze generated in {}s'.format(end_time - start_time))

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
        all_cells = [row for row in self._cells for cell in row if cell.is_transversible()]
        random.shuffle(all_cells)
        return random.choice(all_cells)
       
    def get_cell(self, x, y):
        for row in self._cells:
            for cell in row:
                if cell.x == int((x / self.height)) \
                        and cell.y == int((y / self.width)):
                    return cell
                
    def on_cell_state_change(self):
        self._needs_write = True
       
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
                current = random.choice(neighbors)
            elif len(stack) > 0:
                current = stack.pop()
            else:
                break

    def _generate_cells(self, box_size, diagonals):
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

                self._cells[row][column].neighbors = [self._cells[coords[0]][coords[1]] for coords in n if coords is not None]

        
        