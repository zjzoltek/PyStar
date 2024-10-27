import sys
from a_star import PathFinder
from typing import Final, Optional, Callable

import pygame
from pygame.locals import *
from display.screen import *
import maze
from log import logging
import models

class Director:
    FPS: Final[int] = 60
    LEFT_CLICK: Final[int] = 1
    RIGHT_CLICK: Final[int] = 3
        
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
            clampedPoint.append(min.y)
        else:
            clampedPoint.append(point.y)

        return models.Point(clampedPoint[0], clampedPoint[1])
    
    @staticmethod
    def _mouse_position() -> models.Point:
        pos = pygame.mouse.get_pos()
        return models.Point(pos[0], pos[1])
    
    def __init__(self) -> None:
        self._maze: maze.Maze
        
        self._fps = pygame.time.Clock()
        self._logger = logging.getLogger(Director.__name__)
        self._screen = Screen()
        self._startEnd: models.StartEnd = models.StartEnd(None, None)
        self._pressed_keys: dict[int, pygame.event.Event] = {}
        self._drawing: bool = False
        self._current_cursor_pos: models.Point = models.Point(0, 0)  
        self._last_cursor_pos: Optional[models.Point] = None
        
    def bootstrap(self) -> Self:
        self._screen.display_user_manual()
        self._screen.setup()
        self._maze = maze.Maze(self._screen.window_dimensions.width, self._screen.window_dimensions.height)

        self._generate_maze()
        
        return self
    
    def handle_events_indefinitely(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == MOUSEBUTTONDOWN:
                    self._pressed_keys[event.button] = event
                if event.type == KEYDOWN:
                    self._pressed_keys[event.key] = event

                self._compute_current_highlighted_cell()
                self._handle_mouse_events()
                self._handle_key_events()
                self._pressed_keys.clear()
                self._update_display()
                
    def _generate_random_start_end(self) -> None:
        self._startEnd.reset()
        self._startEnd.start, self._startEnd.end = \
            (self._maze.get_random_transversible_point().mark_as_start(), \
                self._maze.get_random_transversible_point().mark_as_end())
        self._logger.debug(self._startEnd)
    
    def _reset_maze_colors(self, *, include_start_end=False) -> None:
        self._maze.reopen_cells()
        
        if include_start_end:
            self._startEnd.reset()

    def _generate_maze(self) -> None:
        self._maze.generate(self._screen.cell_dimensions, self._screen.diagonals)

    def _handle_key_events(self) -> None:
        if K_z in self._pressed_keys:
            self._drawing = not self._drawing
            if self._drawing:
                self._maze.reopen_cells(openable_only=False)
            else:
                self._generate_maze()

        if K_f in self._pressed_keys:
            def tick():
                pygame.event.pump()
                self._update_display()
                
            self._reset_maze_colors()

            if not self._startEnd.is_populated():
                self._generate_random_start_end()
            
            self._logger.debug(f'PATH: {PathFinder.find_path(self._startEnd, tick)}')
        
        if K_p in self._pressed_keys:
            self._generate_random_start_end()

        if K_m in self._pressed_keys:
            self._generate_maze()

        if K_c in self._pressed_keys:
            self._reset_maze_colors(include_start_end=True)

        if K_x in self._pressed_keys:
            self._reset_maze_colors()

        if K_SPACE in self._pressed_keys:
            self._startEnd.progress(self._maze.get_cell(self._current_cursor_pos.x, self._current_cursor_pos.y))

    def _handle_mouse_events(self): 
        if self.LEFT_CLICK in self._pressed_keys:
            event = self._pressed_keys[self.LEFT_CLICK]
            self._startEnd.progress(self._maze.get_cell(event.pos[0], event.pos[1]))

    def _compute_current_highlighted_cell(self) -> None:
        if not self._drawing:
            return
        
        if K_d in self._pressed_keys or K_RIGHT in self._pressed_keys:
            self._current_cursor_pos.x += self._screen.cell_dimensions.width
        elif K_s in self._pressed_keys or K_DOWN in self._pressed_keys:
            self._current_cursor_pos.y += self._screen.cell_dimensions.height
        elif K_a in self._pressed_keys or K_LEFT in self._pressed_keys:
            self._current_cursor_pos.x -= self._screen.cell_dimensions.width
        elif K_w in self._pressed_keys or K_UP in self._pressed_keys:
            self._current_cursor_pos.y -= self._screen.cell_dimensions.height

        self._current_cursor_pos = self._clamp(self._current_cursor_pos, \
                                            models.Point(self._screen.window_dimensions.width - self._screen.cell_dimensions.width, \
                                                    self._screen.window_dimensions.height - self._screen.cell_dimensions.height),
                                             models.Point(0, 0))
        
        hcell: Optional[models.Cell] = self._maze.get_cell(self._current_cursor_pos.x, self._current_cursor_pos.y)
        assert(hcell is not None)
        
        if K_v in self._pressed_keys:
            hcell.mark_as_wall()

        if self.RIGHT_CLICK in self._pressed_keys:
            mouse_position = self._mouse_position()
            mcell: Optional[models.Cell] = self._maze.get_cell(mouse_position.x, mouse_position.y)
            assert(mcell is not None)
            mcell.mark_as_wall()

        if K_b in self._pressed_keys:
            hcell.mark_as_open()
    
    def _update_display(self) -> None:
        if self._drawing and self._last_cursor_pos != self._current_cursor_pos:
            cell_to_highlight = self._maze.get_cell(self._current_cursor_pos.x, self._current_cursor_pos.y)
            assert cell_to_highlight, 'Could not find cell to highlight'
            cell_to_highlight.highlight()
            
            if self._last_cursor_pos:
                cell_to_unhighlight = self._maze.get_cell(self._last_cursor_pos.x, self._last_cursor_pos.y)
                assert cell_to_unhighlight, 'Could not find cell to unhighlight'
                cell_to_unhighlight.unhighlight()
            
            self._last_cursor_pos = self._current_cursor_pos.copy()
            
        new_surf = self._maze.draw_surf(self._screen.window_dimensions.width, \
                                        self._screen.window_dimensions.height)
        if new_surf:
            self._screen.surf.blit(new_surf, (0, 0))
            
        pygame.display.flip()
        self._fps.tick(self.FPS)
