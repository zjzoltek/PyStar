import time
import sys
from typing import Final, Self

import pygame
from pygame.locals import *
from display.screen import Screen
from display.input_handler import InputHandler
import maze
from log import logging
import models


class Director:
    FPS: Final[int] = 60

    def __init__(self) -> None:
        self._maze: maze.Maze
        self._fps = pygame.time.Clock()
        self._logger = logging.getLogger(Director.__name__)
        self._screen = Screen()
        self._path_endpoints: models.PathEndpoints = models.PathEndpoints()
        self._input_handler = InputHandler()
        self._visualization_mode = 'async'
        self._updates_per_frame = 5
        self._maze_generation_progress = 0.0
        self._maze_generation_message = ""
        self._last_pathfinding_time = 0.0

    def set_visualization_mode(self, mode: str) -> None:
        """Set the active visualization mode."""
        if mode not in {'synchronous', 'optimized', 'async'}:
            raise ValueError(f"Unsupported visualization mode: {mode}")
        self._visualization_mode = mode

    def bootstrap(self) -> Self:
        self._screen.display_user_manual()
        self._screen.setup()
        self._maze = maze.Maze(
            self._screen.window_dimensions.width, self._screen.window_dimensions.height)
        self._maze.set_renderer(self._screen.surf)
        self._generate_maze()

        return self

    def bootstrap_for_test(self, window_dimensions: models.Dimensions, cell_dimensions: models.Dimensions, diagonals: bool) -> Self:
        self._screen.setup_for_test(
            window_dimensions, cell_dimensions, diagonals)
        self._maze = maze.Maze(
            self._screen.window_dimensions.width, self._screen.window_dimensions.height)
        self._maze.set_renderer(self._screen.surf)
        self._generate_maze()

        return self

    def handle_events_indefinitely(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self._maze.cancel_pathfinding()
                    self._maze.cancel_generation()
                    pygame.quit()
                    sys.exit(0)

                self._input_handler.process_event(event)  # type: ignore

            path_updates = self._maze.get_pathfinding_updates(
                self._updates_per_frame)
            for update in path_updates:
                self._maze.on_cell_state_change(update.cell)

            maze_updates = self._maze.get_generation_updates(
                self._updates_per_frame)
            if maze_updates:
                update = maze_updates.pop()
                self._maze_generation_message = update.message
                self._maze_generation_progress = update.progress

                if self._maze._renderer and update.is_complete:
                    self._maze._renderer.mark_full_redraw()
                else:
                    self._maze.on_cell_state_change(update.cell)

            skip_tick = self._maze.has_async_updates()

            # Handle input only if not generating maze (to prevent interference)
            if not self._maze.is_generating():
                self._update_cursor_for_drawing_mode()
                self._handle_mouse_events()
                self._handle_key_events()
            else:
                # Only check for cancel keys if they were pressed during generation
                # (not if they were already pressed before generation started)
                if (self._input_handler.is_key_pressed_once(K_q) or
                        self._input_handler.is_key_pressed_once(K_ESCAPE)):
                    self._maze.cancel_generation()

            self._input_handler.clear_pressed_keys()
            self._update_display(skip_tick=skip_tick)

    def _generate_random_start_end(self) -> None:
        start = self._maze.get_random_transversible_point()
        end = self._maze.get_random_transversible_point()
        self._path_endpoints.set_random_endpoints(start, end)
        self._logger.debug(f'Endpoints: start={start}, end={end}')

    def _reset_maze_colors(self, *, include_start_end=False) -> None:
        self._maze.reopen_cells()

        if include_start_end:
            self._path_endpoints.clear()

    def _generate_maze(self) -> None:
        """Generate maze using async method for better UI responsiveness."""
        if self._maze.is_generating():
            self._maze.cancel_generation()
            return

        self._maze_generation_message = "Starting maze generation..."
        self._logger.info("Starting async maze generation")
        self._input_handler.clear_pressed_keys()

        self._maze.generate_async(
            self._screen.cell_dimensions,
            self._screen.diagonals
        )

    def _handle_key_events(self) -> None:
        # Use is_key_pressed_once for one-shot actions to prevent key repeat issues
        if self._input_handler.is_key_pressed_once(K_z):
            if not self._maze.is_pathfinding():
                self._input_handler.drawing_mode = not self._input_handler.drawing_mode
                if self._input_handler.drawing_mode:
                    self._maze.reopen_cells(openable_only=False)
                else:
                    self._generate_maze()

        if self._input_handler.is_key_pressed_once(K_f):
            # Prevent double activation if pathfinding is running or just finished
            if self._maze.is_pathfinding():
                return

            # 0.5s debounce to prevent accidental double-clicks or ghost inputs
            if time.time() - self._last_pathfinding_time < 0.5:
                return

            self._path_endpoints.clear()
            self._run_pathfinding()

        if self._input_handler.is_key_pressed_once(K_p):
            if not self._maze.is_pathfinding():
                self._generate_random_start_end()

        if self._input_handler.is_key_pressed_once(K_m):
            if not self._maze.is_pathfinding():
                self._generate_maze()

        if self._input_handler.is_key_pressed_once(K_c):
            if not self._maze.is_pathfinding():
                self._reset_maze_colors(include_start_end=True)

        if self._input_handler.is_key_pressed_once(K_x):
            if not self._maze.is_pathfinding():
                self._reset_maze_colors()

        if self._input_handler.is_key_pressed_once(K_SPACE):
            pos = self._input_handler.cursor_position
            self._path_endpoints.select_cell(self._maze.get_cell(pos.x, pos.y))

    def _handle_mouse_events(self) -> None:
        event = self._input_handler.get_mouse_event(InputHandler.LEFT_CLICK)
        if event:
            self._path_endpoints.select_cell(
                self._maze.get_cell(event.pos[0], event.pos[1]))

    def _run_pathfinding(self) -> None:
        if self._maze.is_pathfinding():
            self._logger.warning("Pathfinding already running")
            return

        self._reset_maze_colors()

        if not self._path_endpoints.is_complete():
            self._generate_random_start_end()

        self._maze.find_path_async(self._path_endpoints,
                                   on_complete=self._on_pathfinding_complete)

    def _on_pathfinding_complete(self, path: list[models.Node] | None) -> None:
        self._logger.debug('Pathfinding complete')
        self._last_pathfinding_time = time.time()

    def _update_cursor_for_drawing_mode(self) -> None:
        if not self._input_handler.drawing_mode:
            return

        delta_x = delta_y = 0
        cell_width = self._screen.cell_dimensions.width
        cell_height = self._screen.cell_dimensions.height

        if self._input_handler.is_key_pressed(K_d) or self._input_handler.is_key_pressed(K_RIGHT):
            delta_x = cell_width
        elif self._input_handler.is_key_pressed(K_a) or self._input_handler.is_key_pressed(K_LEFT):
            delta_x = -cell_width
        elif self._input_handler.is_key_pressed(K_s) or self._input_handler.is_key_pressed(K_DOWN):
            delta_y = cell_height
        elif self._input_handler.is_key_pressed(K_w) or self._input_handler.is_key_pressed(K_UP):
            delta_y = -cell_height

        max_point = models.Point(
            self._screen.window_dimensions.width - cell_width,
            self._screen.window_dimensions.height - cell_height
        )
        min_point = models.Point(0, 0)
        self._input_handler.update_cursor_position(
            delta_x, delta_y, max_point, min_point)

        pos = self._input_handler.cursor_position
        cell = self._maze.get_cell(pos.x, pos.y)
        if cell:
            # Use is_key_pressed_once for placement to avoid rapid-fire placement
            if self._input_handler.is_key_pressed_once(K_v):
                cell.mark_as_wall()
            elif self._input_handler.is_key_pressed_once(K_b):
                cell.mark_as_open()

        right_click = self._input_handler.get_mouse_event(
            InputHandler.RIGHT_CLICK)
        if right_click:
            mouse_cell = self._maze.get_cell(
                right_click.pos[0], right_click.pos[1])
            if mouse_cell:
                mouse_cell.mark_as_wall()

    def _update_display(self, *, skip_tick: bool = False) -> None:
        if self._input_handler.drawing_mode:
            current_pos = self._input_handler.cursor_position
            last_pos = self._input_handler.last_cursor_position

            if last_pos != current_pos:
                cell_to_highlight = self._maze.get_cell(
                    current_pos.x, current_pos.y)
                if cell_to_highlight:
                    cell_to_highlight.highlight()

                # Unhighlight previous cell
                if last_pos:
                    cell_to_unhighlight = self._maze.get_cell(
                        last_pos.x, last_pos.y)
                    if cell_to_unhighlight:
                        cell_to_unhighlight.unhighlight()

                self._input_handler.last_cursor_position = current_pos.copy()

        render_batch = self._maze.draw_surf(
            self._screen.window_dimensions.width,
            self._screen.window_dimensions.height
        )
        if render_batch:
            for rect in render_batch.rects:
                self._screen.surf.blit(render_batch.surface, rect, rect)
            if render_batch.rects:
                pygame.display.update(render_batch.rects)

        if self._maze.is_generating():
            self._draw_progress_overlay()

        if not skip_tick:
            self._fps.tick(self.FPS)

    def _draw_progress_overlay(self) -> None:
        """Draw a progress bar overlay for maze generation."""
        # Progress bar dimensions
        bar_width = 400
        bar_height = 30
        bar_x = (self._screen.window_dimensions.width - bar_width) // 2
        bar_y = self._screen.window_dimensions.height - 80

        # Background rectangle
        bg_rect = pygame.Rect(bar_x - 10, bar_y - 10,
                              bar_width + 20, bar_height + 40)
        pygame.draw.rect(self._screen.surf, (0, 0, 0), bg_rect)
        pygame.draw.rect(self._screen.surf, (255, 255, 255), bg_rect, 2)

        # Progress bar background
        progress_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self._screen.surf, (64, 64, 64), progress_bg_rect)

        # Progress bar fill
        if self._maze_generation_progress > 0:
            fill_width = int(bar_width * self._maze_generation_progress)
            progress_fill_rect = pygame.Rect(
                bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self._screen.surf, (0, 255, 0),
                             progress_fill_rect)

        # Progress text
        if hasattr(pygame, 'font') and pygame.font.get_init():
            try:
                font = pygame.font.Font(None, 24)
                progress_text = f"{self._maze_generation_progress:.1%}"
                text_surface = font.render(
                    progress_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
                self._screen.surf.blit(text_surface, text_rect)

                # Status message
                if self._maze_generation_message:
                    status_surface = font.render(
                        self._maze_generation_message, True, (255, 255, 255))
                    status_rect = status_surface.get_rect(
                        center=(bar_x + bar_width // 2, bar_y + bar_height + 15))
                    self._screen.surf.blit(status_surface, status_rect)
            except:
                pass

        pygame.display.update(bg_rect)
