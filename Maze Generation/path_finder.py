import heapq
import sys
from enum import Enum
from math import sqrt
from random import randint, seed
from time import time

import pygame
from maze.cell import Cell
from maze.depth_first import Maze
from pygame.locals import *


class Path_Finder:
    class Mode(Enum):
        MANUAL = 1
        AUTO = 2
        
    FPS = 60

    @staticmethod
    def get_distance(start, goal):
        dx = float(start.x - goal.x)
        dy = float(start.y - goal.y)
        dist = float(sqrt(dx * dx + dy * dy))

        return dist

    @staticmethod
    def clamp(x, y, maxx, maxy, minx, miny):
        pair = []
        if x > maxx:
            pair.append(maxx)
        elif x < minx:
            pair.append(minx)
        else:
            pair.append(x)

        if y > maxy:
            pair.append(maxy)
        elif y < miny:
            pair.append(miny)
        else:
            pair.append(y)

        return pair
    
    @staticmethod
    def _mouse_button_str(mouse_button):
        return 'button{}'.format(mouse_button)
    
    def __init__(self, surf, win_dims, box_dims, diagonals):
        self.fps = pygame.time.Clock()
        self.surf = surf
        (self.w, self.h) = win_dims
        (self.box_w, self.box_h) = box_dims
        self.maze = Maze(self.w, self.h)
        self.points = []
        self.pressed_keys = {}
        self.mode = self.Mode.AUTO
        self.diagonals = diagonals
        self.highlighted_cell = [0, 0]

        seed(randint(0, 1000))
        self._regenerate_maze()
        self._handle_events()
    
    def _find_path(self, start: Cell, goal: Cell) -> None:
        openlist = []
        closedlist = set()
        
        current = Node(start, None, 0, self.get_distance(start, goal))
        heapq.heappush(openlist, current)

        while openlist:
            current = heapq.heappop(openlist)
            closedlist.add(current.cell)
            
            if current.cell.x == goal.x and current.cell.y == goal.y:
                path = []
                while current.parent is not None:
                    if not current.cell.is_terminator():
                        current.cell.mark_as_route()

                    path.append(current)
                    current = current.parent
                return path

            if not current.cell.is_terminator():
                current.cell.mark_as_searched()

            for cell in current.cell.neighbors:
                if not cell.is_transversible() or cell in closedlist:
                    continue
                    
                gcost = current.gCost + self.get_distance(current.cell, cell)
                hcost = self.get_distance(cell, goal)
                n = Node(cell, current, gcost, hcost)
                heapq.heappush(openlist, n)

            pygame.event.pump()
        return None

    def _generate_random_start_end(self):
        self._reset_start_end()
        self.points = [self.maze.get_random_transversible_point(), self.maze.get_random_transversible_point()]
        self.points[0].mark_as_start()
        self.points[1].mark_as_end()
        print(f'New points generated: Start: {self.points[0].x}, {self.points[0].y} | End: {self.points[1].x}, {self.points[1].y}')

    def _reset_start_end(self):
        for p in self.points:
            p.mark_as_open()
        
        self.points.clear()
    
    def _reset_maze_colors(self, include_start_end=False):
        self.maze.reopen_cells()
        
        if include_start_end:
            self._reset_start_end()

    def _regenerate_maze(self):
        self.maze.generate((self.box_w, self.box_h), self.diagonals)
                
    def _handle_events(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == MOUSEBUTTONDOWN:
                    self.pressed_keys[self._mouse_button_str(event.button)] = event
                if event.type == KEYDOWN:
                    self.pressed_keys[event.key] = event

                self._compute_current_highlighted_cell()
                self._handle_mouse_events()
                self._handle_key_events()
                self.pressed_keys.clear()
                self._update_display()

    def _handle_key_events(self):
        if K_z in self.pressed_keys:
            self.mode = self.Mode.AUTO if self.mode == self.Mode.MANUAL else self.Mode.MANUAL
            if self.mode == self.Mode.AUTO:
                self._regenerate_maze()
            else:
                self.maze.reopen_cells(openable_only=False)

        if K_f in self.pressed_keys:
            self._reset_maze_colors()

            if len(self.points) != 2:
                self._generate_random_start_end()
            
            start_time = time()
            self._find_path(self.points[0], self.points[1])
            end_time = time()
            print('Done in {} seconds'.format(end_time - start_time))
        
        if K_p in self.pressed_keys:
            self._generate_random_start_end()

        if K_m in self.pressed_keys:
            self._regenerate_maze()

        if K_c in self.pressed_keys:
            self._reset_maze_colors(include_start_end=True)

        if K_x in self.pressed_keys:
            self._reset_maze_colors()

        if K_SPACE in self.pressed_keys:
            self._progress_points(self.maze.get_cell(self.highlighted_cell[0], self.highlighted_cell[1]))

    def _handle_mouse_events(self): 
        if self._mouse_button_str(1) in self.pressed_keys:
            event = self.pressed_keys[self._mouse_button_str(1)]
            self._progress_points(self.maze.get_cell(event.pos[0], event.pos[1]))

    def _progress_points(self, cell):
        if len(self.points) == 2:
            self._reset_start_end()
        elif cell.is_transversible() and not cell.is_terminator():
            if not self.points:
                cell.mark_as_start()
            else:
                cell.mark_as_end()
            self.points.append(cell)

    def _compute_current_highlighted_cell(self):
        if K_d in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell[0] += self.box_w
        elif K_s in self.pressed_keys or K_DOWN in self.pressed_keys:
            self.highlighted_cell[1] += self.box_h
        elif K_a in self.pressed_keys or K_LEFT in self.pressed_keys:
            self.highlighted_cell[0] -= self.box_w
        elif K_w in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell[1] -= self.box_h

        self.highlighted_cell = self.clamp(self.highlighted_cell[0],
                                            self.highlighted_cell[1], self.w - self.box_w,
                                            self.h - self.box_h, 0, 0)
        
        if K_v in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.maze.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.mark_as_wall()

        if self._mouse_button_str(3) in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.maze.get_cell(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            hcell.mark_as_wall()

        if K_b in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.maze.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.mark_as_open()

        pygame.draw.rect(self.surf, (0, 255, 0),
                            (self.highlighted_cell[0] *  self.box_w, \
                                self.highlighted_cell[1] *  self.box_h, \
                                    self.box_w, self.box_h))
    
    def _update_display(self):
        new_surf = self.maze.draw_surf(self.w, self.h)
        if new_surf is not None:
            self.surf.blit(new_surf, (0, 0))
            pygame.display.flip()
        self.fps.tick(self.FPS)

class Node:
    def __init__(self, cell, parent, gcost, hcost):
        self.cell = cell
        self.parent = parent

        self.gCost = gcost
        self.hCost = hcost
        self.fCost = gcost + hcost
    
    def __repr__(self):
        return repr(self.cell)
    
    def __lt__(self, other):
        return self.fCost < other.fCost
    
    def __gt__(self, other):
        return self.fCost > other.fCost
    
    def __le__(self, other):
        return self.fCost <= other.fCost
    
    def __ge__(self, other):
        return self.fCost >= other.fCost
    
    def __eq__(self, other):
        return self.fCost == other.fCost
    
    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return hash(self.__repr__())
