import random
from typing import Optional, Callable, TYPE_CHECKING
import pygame

from models import Cell, Dimensions, ICellStateListener, PathEndpoints, Node
from display.incremental_renderer import RenderBatch, IncrementalRenderer

if TYPE_CHECKING:
    from maze.async_maze_generator import MazeGenerationUpdate

class Maze(ICellStateListener):
    def __init__(self, width: int, height: int) -> None:
        self._width: int = width
        self._height: int = height
        self._cells: list[list[Cell]] = []
        self._needs_write: bool = False
        self._renderer: Optional[IncrementalRenderer] = None
        self._changed_cells: set[Cell] = set()
        self._cell_width: int = 0
        self._cell_height: int = 0
    
    def generate_async(
        self,
        cell_size: Dimensions,
        diagonals: bool,
        on_complete: Optional[Callable[[bool], None]] = None,
        on_progress: Optional[Callable[['MazeGenerationUpdate'], None]] = None
    ) -> None:
        """Generate maze asynchronously with progress callbacks."""
        from maze.async_maze_generator import AsyncMazeGenerator

        if not hasattr(self, '_async_generator'):
            self._async_generator = AsyncMazeGenerator()

        self._async_generator.generate_maze_async(
            self, cell_size, diagonals, on_complete, on_progress
        )

    def get_generation_updates(self, batch_size: int = 10):
        """Get pending updates from async maze generation."""
        if hasattr(self, '_async_generator'):
            return self._async_generator.process_updates(batch_size)
        return []

    def is_generating(self) -> bool:
        """Check if maze is currently being generated asynchronously."""
        return hasattr(self, '_async_generator') and self._async_generator.is_running

    def cancel_generation(self) -> None:
        """Cancel ongoing maze generation."""
        if hasattr(self, '_async_generator'):
            self._async_generator.cancel()

    # ============= AsyncPathfinding Methods =============

    def find_path_async(
        self,
        endpoints: PathEndpoints,
        on_complete: Optional[Callable[[Optional[list[Node]]], None]] = None
    ) -> None:
        """
        Find path asynchronously with optional completion callback.

        Args:
            endpoints: Start and end points for pathfinding
            on_complete: Callback when pathfinding completes
        """
        from maze.async_pathfinder import AsyncPathfinder

        if not hasattr(self, '_async_pathfinder'):
            self._async_pathfinder = AsyncPathfinder()

        self._async_pathfinder.find_path_async(endpoints, on_complete)

    def get_pathfinding_updates(self, batch_size: int = 10):
        """
        Get pending updates from async pathfinding.

        Args:
            batch_size: Maximum number of updates to process

        Returns:
            List of pathfinding updates
        """
        if hasattr(self, '_async_pathfinder'):
            return self._async_pathfinder.process_updates(batch_size)
        return []

    def is_pathfinding(self) -> bool:
        """Check if pathfinding is currently running."""
        return hasattr(self, '_async_pathfinder') and self._async_pathfinder.is_running

    def has_pathfinding_updates(self) -> bool:
        """Check if there are pending pathfinding updates."""
        return hasattr(self, '_async_pathfinder') and self._async_pathfinder.has_updates

    def cancel_pathfinding(self) -> None:
        """Cancel ongoing pathfinding."""
        if hasattr(self, '_async_pathfinder'):
            self._async_pathfinder.cancel()

    # ============= Combined Async Status Methods =============

    def is_async_operation_running(self) -> bool:
        """Check if any async operation is currently running."""
        return self.is_generating() or self.is_pathfinding()

    def has_async_updates(self) -> bool:
        """Check if any async operation has pending updates."""
        generation_updates = hasattr(self, '_async_generator') and self._async_generator.has_updates
        pathfinding_updates = hasattr(self, '_async_pathfinder') and self._async_pathfinder.has_updates
        return generation_updates or pathfinding_updates

    def set_renderer(self, surface: pygame.Surface) -> None:
        """Set up the incremental renderer."""
        # fps parameter kept for backward compatibility but not used
        # since IncrementalRenderer doesn't control frame rate
        self._renderer = IncrementalRenderer(surface)

    def draw_surf(self, width: int, height: int) -> RenderBatch | None:
        """Draw the maze surface using incremental rendering."""
        if self._renderer:
            # Use incremental renderer for better performance
            if self._needs_write:
                # Add changed cells to render queue
                for cell in self._changed_cells:
                    self._renderer.add_to_render_queue(cell)
                self._changed_cells.clear()
                self._needs_write = False

            return self._renderer.render_maze(self, width, height)
        else:
            # Fallback to full redraw if no renderer set
            if not self._needs_write:
                return None

            surf = pygame.Surface((width, height)).convert()
            for column in self._cells:
                for cell in column:
                    pygame.draw.rect(surf, cell.get_color(),
                        (cell.x * cell.dimensions.width,
                        cell.y * cell.dimensions.height,
                        cell.dimensions.width, cell.dimensions.height))

            self._needs_write = False
            return RenderBatch(surf, [surf.get_rect()])

    def reopen_cells(self, openable_only: bool=True) -> None:
        for column in self._cells:
            for cell in column:
                if cell.is_openable() or not openable_only:
                    cell.mark_as_open()
         
    def get_random_transversible_point(self) -> Cell:
        all_cells = [row for row in self._cells for cell in row if cell.is_transversible()]
        random.shuffle(all_cells)
        return random.choice(random.choice(all_cells))
       
    def get_cell(self, x: int, y: int) -> Cell | None:
        """
        Get cell at pixel coordinates (x, y).
        Optimized to use direct array indexing instead of linear search.
        """
        if not self._cells or self._cell_width == 0 or self._cell_height == 0:
            return None

        if x < 0 or y < 0:
            return None

        grid_x = int(x / self._cell_width)
        grid_y = int(y / self._cell_height)

        # Check bounds
        if (grid_x >= len(self._cells) or
            grid_y >= len(self._cells[0])):
            return None

        return self._cells[grid_x][grid_y]
                
    def on_cell_state_change(self, cell: Optional[Cell] = None) -> None:
        """Called when a cell's state changes."""
        self._needs_write = True
        if cell:
            self._changed_cells.add(cell)
       
    def _generate_cells(self, cell_size: Dimensions, diagonals: bool) -> None:
        w = int(self._width / cell_size.width)
        h = int(self._height / cell_size.height)
        self._cell_width = cell_size.width
        self._cell_height = cell_size.height
        self._cells = [[Cell(row, column, cell_size, self)
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

                self._cells[row][column].neighbors = [self._cells[coords[0]][coords[1]] for coords in n if coords]
