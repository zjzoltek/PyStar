import sys
from a_star import PathFinder
from typing import Final, Self

import pygame # type: ignore
from pygame.locals import * # type: ignore
from display.screen import Screen
from display.input_handler import InputHandler
from display.async_pathfinding import AsyncPathfinder
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
        self._async_pathfinder = AsyncPathfinder()
        self._visualization_mode = 'async'
        self._updates_per_frame = 5

    def set_visualization_mode(self, mode: str) -> None:
        """Set the active visualization mode."""
        if mode not in {'synchronous', 'optimized', 'async'}:
            raise ValueError(f"Unsupported visualization mode: {mode}")
        self._visualization_mode = mode
        
    def bootstrap(self) -> Self:
        self._screen.display_user_manual()
        self._screen.setup()
        self._maze = maze.Maze(self._screen.window_dimensions.width, self._screen.window_dimensions.height)

        # Set up the incremental renderer for smooth visualization
        self._maze.set_renderer(self._screen.surf, self.FPS)

        self._generate_maze()

        return self
    
    def bootstrap_for_test(self, window_dimensions: models.Dimensions, cell_dimensions: models.Dimensions, diagonals: bool) -> Self:
        self._screen.setup_for_test(window_dimensions, cell_dimensions, diagonals)
        self._maze = maze.Maze(self._screen.window_dimensions.width, self._screen.window_dimensions.height)

        # Set up the incremental renderer for smooth visualization
        self._maze.set_renderer(self._screen.surf, self.FPS)

        self._generate_maze()
        
        return self
        
    def handle_events_indefinitely(self) -> None:
        print("\nVisualization Modes:")
        print("  Press 1: Synchronous mode (original, capped at 60 FPS)")
        print("  Press 2: Optimized mode (fast synchronous, no FPS cap while solving)")
        print("  Press 3: Async mode (background solver, no FPS cap while active)")
        print(f"\nCurrent mode: {self._visualization_mode}\n")

        while True:
            for event in pygame.event.get():
                if event.type == QUIT: # type: ignore
                    self._async_pathfinder.stop()
                    pygame.quit()
                    sys.exit(0)

                self._input_handler.process_event(event)

            skip_tick = False
            if self._visualization_mode == 'async':
                updates = self._async_pathfinder.process_updates(self._updates_per_frame)
                if updates:
                    self._maze.on_cell_state_change()
                skip_tick = self._async_pathfinder.is_running or self._async_pathfinder.has_updates

            self._update_cursor_for_drawing_mode()
            self._handle_mouse_events()
            self._handle_key_events()
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
        self._maze.generate(self._screen.cell_dimensions, self._screen.diagonals)
        # Force immediate render after maze generation
        if self._maze._renderer:
            self._maze._renderer.mark_full_redraw()

    def _handle_key_events(self) -> None:
        if self._input_handler.is_key_pressed(K_1):
            self._visualization_mode = 'synchronous'
            print("Switched to SYNCHRONOUS mode (original, slow)")

        if self._input_handler.is_key_pressed(K_2):
            self._visualization_mode = 'optimized'
            print("Switched to OPTIMIZED mode (fast synchronous)")

        if self._input_handler.is_key_pressed(K_3):
            self._visualization_mode = 'async'
            print("Switched to ASYNC mode (background thread, no fps limit while active)")

        if self._input_handler.is_key_pressed(K_z): # type: ignore
            self._input_handler.drawing_mode = not self._input_handler.drawing_mode
            if self._input_handler.drawing_mode:
                self._maze.reopen_cells(openable_only=False)
            else:
                self._generate_maze()

        if self._input_handler.is_key_pressed(K_f): # type: ignore
            self._run_pathfinding()
        
        if self._input_handler.is_key_pressed(K_p): # type: ignore
            self._generate_random_start_end()

        if self._input_handler.is_key_pressed(K_m): # type: ignore
            self._generate_maze()

        if self._input_handler.is_key_pressed(K_c): # type: ignore
            self._reset_maze_colors(include_start_end=True)

        if self._input_handler.is_key_pressed(K_x): # type: ignore
            self._reset_maze_colors()

        if self._input_handler.is_key_pressed(K_SPACE): # type: ignore
            pos = self._input_handler.cursor_position
            self._path_endpoints.select_cell(self._maze.get_cell(pos.x, pos.y))

    def _handle_mouse_events(self) -> None:
        event = self._input_handler.get_mouse_event(InputHandler.LEFT_CLICK)
        if event:
            self._path_endpoints.select_cell(self._maze.get_cell(event.pos[0], event.pos[1]))

    def _run_pathfinding(self) -> None:
        """Run pathfinding using the active visualization mode."""
        # Ensure async pathfinding is not already running
        if self._async_pathfinder.is_running:
            self._async_pathfinder.stop()

        self._reset_maze_colors()

        if not self._path_endpoints.is_complete():
            self._generate_random_start_end()

        if self._visualization_mode == 'synchronous':
            def tick():
                pygame.event.pump()
                self._update_display()

            self._logger.debug(f'PATH: {PathFinder.find_path(self._path_endpoints, tick)}')

        elif self._visualization_mode == 'optimized':
            def tick_optimized():
                pygame.event.pump()
                self._update_display(skip_tick=True)

            self._logger.debug(f'PATH: {PathFinder.find_path(self._path_endpoints, tick_optimized)}')

        elif self._visualization_mode == 'async':
            def on_complete(path):
                self._logger.debug(f'PATH (async): {path}')

            self._async_pathfinder.find_path_async(self._path_endpoints, on_complete)

        else:
            self._logger.warning("Unknown visualization mode '%s'", self._visualization_mode)

    def _update_cursor_for_drawing_mode(self) -> None:
        """Update cursor position and handle drawing mode actions."""
        if not self._input_handler.drawing_mode:
            return

        # Calculate cursor movement
        delta_x = delta_y = 0
        cell_width = self._screen.cell_dimensions.width
        cell_height = self._screen.cell_dimensions.height

        if self._input_handler.is_key_pressed(K_d) or self._input_handler.is_key_pressed(K_RIGHT): # type: ignore
            delta_x = cell_width
        elif self._input_handler.is_key_pressed(K_a) or self._input_handler.is_key_pressed(K_LEFT): # type: ignore
            delta_x = -cell_width
        elif self._input_handler.is_key_pressed(K_s) or self._input_handler.is_key_pressed(K_DOWN): # type: ignore
            delta_y = cell_height
        elif self._input_handler.is_key_pressed(K_w) or self._input_handler.is_key_pressed(K_UP): # type: ignore
            delta_y = -cell_height

        # Update cursor position with bounds
        max_point = models.Point(
            self._screen.window_dimensions.width - cell_width,
            self._screen.window_dimensions.height - cell_height
        )
        min_point = models.Point(0, 0)
        self._input_handler.update_cursor_position(delta_x, delta_y, max_point, min_point)

        # Handle cell modifications
        pos = self._input_handler.cursor_position
        cell = self._maze.get_cell(pos.x, pos.y)
        if cell:
            if self._input_handler.is_key_pressed(K_v): # type: ignore
                cell.mark_as_wall()
            elif self._input_handler.is_key_pressed(K_b): # type: ignore
                cell.mark_as_open()

        # Handle right-click wall drawing
        right_click = self._input_handler.get_mouse_event(InputHandler.RIGHT_CLICK)
        if right_click:
            mouse_cell = self._maze.get_cell(right_click.pos[0], right_click.pos[1])
            if mouse_cell:
                mouse_cell.mark_as_wall()
    
    def _update_display(self, *, skip_tick: bool = False) -> None:
        """Update the display with current maze state.

        Args:
            skip_tick: When True, do not call fps.tick(); allows unthrottled refresh
                while still executing the full render pipeline.
        """
        # Handle cursor highlighting in drawing mode
        if self._input_handler.drawing_mode:
            current_pos = self._input_handler.cursor_position
            last_pos = self._input_handler.last_cursor_position

            if last_pos != current_pos:
                # Highlight new cell
                cell_to_highlight = self._maze.get_cell(current_pos.x, current_pos.y)
                if cell_to_highlight:
                    cell_to_highlight.highlight()

                # Unhighlight previous cell
                if last_pos:
                    cell_to_unhighlight = self._maze.get_cell(last_pos.x, last_pos.y)
                    if cell_to_unhighlight:
                        cell_to_unhighlight.unhighlight()

                self._input_handler.last_cursor_position = current_pos.copy()

        # Render maze surface
        render_batch = self._maze.draw_surf(
            self._screen.window_dimensions.width,
            self._screen.window_dimensions.height
        )
        if render_batch:
            for rect in render_batch.rects:
                self._screen.surf.blit(render_batch.surface, rect, rect)
            if render_batch.rects:
                pygame.display.update(render_batch.rects)

        if not skip_tick:
            self._fps.tick(self.FPS)
