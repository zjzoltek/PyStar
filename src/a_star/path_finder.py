import sys
from heapq import heappop, heappush
from math import sqrt
from typing import Final, Optional

import pygame
from pygame.locals import *

import maze
from log import logging, timed
import models

class PathFinder:
    FPS: Final[int] = 60
    HIGHLIGHTED_CELL_COLOR: Final[tuple[int, int, int]] = (0, 255, 0)
    LEFT_CLICK: Final[int] = 1
    RIGHT_CLICK: Final[int] = 3
    
    @staticmethod
    def _get_distance(start, goal) -> float:
        dx = float(start.x - goal.x)
        dy = float(start.y - goal.y)
        dist = float(sqrt(dx * dx + dy * dy))

        return dist

    @staticmethod
    def _clamp(point: models.Point, max: models.Point, min: models.Point) -> models.Point:
        clampedPoint: list[int] = []
        if point.x > max.x:
            clampedPoint.append(max.x)
        elif point.x < min.x:
            clampedPoint.append(min.x)
        else:
            clampedPoint.append(point.x)

        if point.y > max.y:
            clampedPoint.append(max.y)
        elif point.y < min.y:
            clampedPoint.append(max.y)
        else:
            clampedPoint.append(max.y)

        return models.Point(clampedPoint[0], clampedPoint[1])
    
    @staticmethod
    def _mouse_position() -> models.Point:
        pos = pygame.mouse.get_pos()
        return models.Point(pos[0], pos[1])
    
    def __init__(self, surf: pygame.Surface, cell_dimensions: models.Dimensions, window_dimensions: models.Dimensions, diagonals: bool):
        self._fps = pygame.time.Clock()
        self._surf = surf
        self._logger = logging.getLogger(PathFinder.__name__)

        self.cell_dimensions = cell_dimensions
        self.maze = maze.Maze(window_dimensions.width, window_dimensions.height)
        self.startEnd: models.StartEnd = models.StartEnd(None, None)
        self.pressed_keys: dict[int, pygame.event.Event] = {}
        self.is_drawing: bool = False
        self.diagonals: bool = diagonals
        self.highlighted_cell: models.Point = models.Point(0, 0)  
        self.window_dimensions = window_dimensions
        
        self._generate_maze()
        self._handle_events()
    
    @timed
    def _find_path(self, startEnd: models.StartEnd) -> Optional[list[models.Node]]:
        assert(startEnd.start is not None)
        assert(startEnd.end is not None)
        
        openlist: list[models.Node] = []
        closedlist: set[models.Cell] = set()
        
        current = models.Node(cell=startEnd.start, parent=None, gCost=0, hCost=self._get_distance(startEnd.start, startEnd.end))
        heappush(openlist, current)

        while openlist:
            current = heappop(openlist)
            closedlist.add(current.cell)
            
            if current.cell.x == startEnd.end.x and current.cell.y == startEnd.end.y:
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
                hcost = self._get_distance(cell, startEnd.end)
                n = models.Node(cell, current, gcost, hcost)
                heappush(openlist, n)

            pygame.event.pump()
        return None

    def _generate_random_start_end(self) -> None:
        self.startEnd.reset()
        self.startEnd.start, self.startEnd.end = \
            (self.maze.get_random_transversible_point().mark_as_start(), \
                self.maze.get_random_transversible_point().mark_as_end())
        self._logger.debug(self.startEnd)
    
    def _reset_maze_colors(self, *, include_start_end=False) -> None:
        self.maze.reopen_cells()
        
        if include_start_end:
            self.startEnd.reset()

    def _generate_maze(self) -> None:
        self.maze.generate(self.cell_dimensions, self.diagonals)
                
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

    def _handle_key_events(self) -> None:
        if K_z in self.pressed_keys:
            self.is_drawing = not self.is_drawing
            if self.is_drawing:
                self.maze.reopen_cells(openable_only=False)
            else:
                self._generate_maze()

        if K_f in self.pressed_keys:
            self._reset_maze_colors()

            if self.startEnd.is_empty():
                self._generate_random_start_end()
            
            self._find_path(self.startEnd)
        
        if K_p in self.pressed_keys:
            self._generate_random_start_end()

        if K_m in self.pressed_keys:
            self._generate_maze()

        if K_c in self.pressed_keys:
            self._reset_maze_colors(include_start_end=True)

        if K_x in self.pressed_keys:
            self._reset_maze_colors()

        if K_SPACE in self.pressed_keys:
            self.startEnd.progress(self.maze.get_cell(self.highlighted_cell.x, self.highlighted_cell.y))

    def _handle_mouse_events(self): 
        if self.LEFT_CLICK in self.pressed_keys:
            event = self.pressed_keys[self.LEFT_CLICK]
            self.startEnd.progress(self.maze.get_cell(event.pos[0], event.pos[1]))

    def _compute_current_highlighted_cell(self) -> None:
        if K_d in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell.x += self.cell_dimensions.width
        elif K_s in self.pressed_keys or K_DOWN in self.pressed_keys:
            self.highlighted_cell.y += self.cell_dimensions.height
        elif K_a in self.pressed_keys or K_LEFT in self.pressed_keys:
            self.highlighted_cell.x -= self.cell_dimensions.width
        elif K_w in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell.y -= self.cell_dimensions.height

        self.highlighted_cell = self._clamp(self.highlighted_cell, \
                                            models.Point(self.window_dimensions.width - self.cell_dimensions.width, \
                                                    self.window_dimensions.height - self.cell_dimensions.height),
                                             models.Point(0, 0))
        
        hcell: Optional[models.Cell] = self.maze.get_cell(self.highlighted_cell.x, self.highlighted_cell.y)
        assert(hcell is not None)
        
        if K_v in self.pressed_keys and self.is_drawing:
            hcell.mark_as_wall()

        if self.RIGHT_CLICK in self.pressed_keys and self.is_drawing:
            mouse_position = self._mouse_position()
            mcell: Optional[models.Cell] = self.maze.get_cell(mouse_position.x, mouse_position.y)
            assert(mcell is not None)
            mcell.mark_as_wall()

        if K_b in self.pressed_keys and self.is_drawing:
            hcell.mark_as_open()

        pygame.draw.rect(self._surf, self.HIGHLIGHTED_CELL_COLOR,
                            (self.highlighted_cell.x *  self.cell_dimensions.width, \
                                self.highlighted_cell.y *  self.cell_dimensions.height, \
                                    self.cell_dimensions.width, self.cell_dimensions.height))
    
    def _update_display(self) -> None:
        new_surf = self.maze.draw_surf(self.window_dimensions.width, \
                                        self.window_dimensions.height)
        if new_surf is not None:
            self._surf.blit(new_surf, (0, 0))
            pygame.display.flip()
        self._fps.tick(self.FPS)
