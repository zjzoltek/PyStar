import sys
from heapq import heappop, heappush
from math import sqrt
from time import time
from typing import Final, Optional

import pygame
from pygame.locals import *

import maze
from models import *
from log import timed

class PathFinder:
    FPS: Final[int] = 60

    @staticmethod
    def _get_distance(start, goal) -> float:
        dx = float(start.x - goal.x)
        dy = float(start.y - goal.y)
        dist = float(sqrt(dx * dx + dy * dy))

        return dist

    @staticmethod
    def _clamp(*, point: Point, max: Point, min: Point) -> Point:
        clampedPoint: Point = Point()
        if point.x > max.x:
            clampedPoint.x = max.x
        elif point.x < min.x:
            clampedPoint.x = min.x
        else:
            clampedPoint.x = point.x

        if point.y > max.y:
            clampedPoint.y = max.y
        elif point.y < min.y:
            clampedPoint.y = min.y
        else:
            clampedPoint.y = point.y

        return clampedPoint
    
    def __init__(self, surf: pygame.Surface, cell_dimensions: Dimensions, diagonals: bool):
        self._fps = pygame.time.Clock()
        self._surf = surf
        self.cell_dimensions = cell_dimensions
        self.maze = maze.Maze(board_width=self.w, board_height=self.h)
        self.startEnd: StartEnd = StartEnd()
        self.pressed_keys: dict[int, pygame.event.Event] = {}
        self.is_drawing: bool = False
        self.diagonals: bool = diagonals
        self.highlighted_cell: Point = Point(0, 0)  

        self._regenerate_maze()
        self._handle_events()
    
    @timed
    def _find_path(self, start: Cell, goal: Cell) -> Optional[list[Node]]:
        openlist: list[Node] = []
        closedlist: set[Cell] = {}
        
        current = Node(cell=start, parent=None, gCost=0, hCost=self._get_distance(start, goal))
        heappush(openlist, current)

        while openlist:
            current = heappop(openlist)
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
                    
                gcost = current.gCost + self._get_distance(current.cell, cell)
                hcost = self._get_distance(cell, goal)
                n = Node(cell=cell, parent=current, gCost=gcost, hCost=hcost)
                heappush(openlist, n)

            pygame.event.pump()
        return None

    def _generate_random_start_end(self) -> None:
        self.startEnd.reset()
        self.startEnd.start, self.startEnd.end = \
            (self.maze.get_random_transversible_point().mark_as_start(), \
                self.maze.get_random_transversible_point().mark_as_end())
        print(f'New points generated: {self.startEnd}')
    
    def _reset_maze_colors(self, *, include_start_end=False) -> None:
        self.maze.reopen_cells()
        
        if include_start_end:
            self.startEnd.reset()

    def _regenerate_maze(self) -> None:
        self.maze.generate((self.cell_dimensions.width, self.cell_dimensions.height), self.diagonals)
                
    def _handle_events(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == MOUSEBUTTONDOWN:
                    self.pressed_keys[event.button] = event
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

            if not self.startEnd.has_start() or not self.startEnd.has_end():
                self._generate_random_start_end()
            
            self._find_path(self.points[0], self.points[1])
        
        if K_p in self.pressed_keys:
            self._generate_random_start_end()

        if K_m in self.pressed_keys:
            self._regenerate_maze()

        if K_c in self.pressed_keys:
            self._reset_maze_colors(include_start_end=True)

        if K_x in self.pressed_keys:
            self._reset_maze_colors()

        if K_SPACE in self.pressed_keys:
            self.startEnd.progress(self.maze.get_cell(self.highlighted_cell[0], self.highlighted_cell[1]))

    def _handle_mouse_events(self): 
        if 1 in self.pressed_keys:
            event = self.pressed_keys[1]
            self.startEnd.progress(self.maze.get_cell(event.pos[0], event.pos[1]))

    def _compute_current_highlighted_cell(self):
        if K_d in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell[0] += self.cell_dimensions.width
        elif K_s in self.pressed_keys or K_DOWN in self.pressed_keys:
            self.highlighted_cell[1] += self.cell_dimensions.height
        elif K_a in self.pressed_keys or K_LEFT in self.pressed_keys:
            self.highlighted_cell[0] -= self.cell_dimensions.width
        elif K_w in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell[1] -= self.cell_dimensions.height

        self.highlighted_cell = self._clamp(self.highlighted_cell[0],
                                            self.highlighted_cell[1], self.w - self.cell_dimensions.width,
                                            self.h - self.cell_dimensions.height, 0, 0)
        
        if K_v in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.maze.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.mark_as_wall()

        if self._mouse_button_str(3) in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.maze.get_cell(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            hcell.mark_as_wall()

        if K_b in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.maze.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.mark_as_open()

        pygame.draw.rect(self._surf, (0, 255, 0),
                            (self.highlighted_cell[0] *  self.cell_dimensions.width, \
                                self.highlighted_cell[1] *  self.cell_dimensions.height, \
                                    self.cell_dimensions.width, self.cell_dimensions.height))
    
    def _update_display(self):
        new_surf = self.maze.draw_surf(self.w, self.h)
        if new_surf is not None:
            self._surf.blit(new_surf, (0, 0))
            pygame.display.flip()
        self._fps.tick(self.FPS)
