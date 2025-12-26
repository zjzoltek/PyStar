"""
Asynchronous maze generation implementation that decouples algorithm execution from rendering.
"""

import random
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from models import Cell, Dimensions, State
from maze.async_operation_manager import AsyncOperationManager
from maze.fast_maze_generator import FastMazeGenerator
import array

if TYPE_CHECKING:
    from maze.depth_first import Maze


@dataclass
class MazeGenerationUpdate:
    """Represents a single update from the maze generation algorithm."""
    cell: Optional[Cell]
    progress: float  # 0.0 to 1.0
    total_cells: int
    visited_cells: int
    message: str
    is_complete: bool = False


class AsyncMazeGenerator(AsyncOperationManager[MazeGenerationUpdate]):
    """
    Runs maze generation in a separate thread and communicates updates via queue.
    This allows the algorithm to run at full speed while the main thread
    renders updates and shows progress at its own pace.

    Inherits thread management, queue handling, and cancellation from AsyncOperationManager.
    """

    def generate_maze_async(
        self,
        maze: 'Maze',
        cell_size: Dimensions,
        diagonals: bool
    ) -> None:
        """
        Start maze generation in a background thread.

        Args:
            maze: The maze object to populate
            cell_size: Dimensions for each cell
            diagonals: Whether to include diagonal connections
        """
        self.start_async(
            target_method=self._run_maze_generation,
            args=(maze, cell_size, diagonals),
            name="MazeGeneration"
        )

    def _run_maze_generation(
        self,
        maze: 'Maze',
        cell_size: Dimensions,
        diagonals: bool
    ) -> None:
        """Run maze generation algorithm in background thread."""
        try:
            # Generate cell grid first (Allocation)
            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.0,
                total_cells=0,
                visited_cells=0,
                message="Initializing maze structure...",
                is_complete=False
            ))

            maze._generate_cells(cell_size, diagonals)
            if maze._renderer:
                maze._renderer.mark_full_redraw()

            w = len(maze._cells)
            h = len(maze._cells[0]) if w > 0 else 0
            total_cells = w * h

            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.0,
                total_cells=total_cells,
                visited_cells=0,
                message=f"Starting generation of {total_cells} cells...",
                is_complete=False
            ))

            if not diagonals:
                self._run_fast_generation(maze, w, h)
            else:
                self._run_legacy_generation(maze, total_cells)

        except Exception as e:
            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.0,
                total_cells=0,
                visited_cells=0,
                message=f"Maze generation failed: {str(e)}",
                is_complete=True
            ))
        finally:
            self._running = False

    def _run_fast_generation(self, maze: 'Maze', width: int, height: int) -> None:
        """Uses FastMazeGenerator and updates the maze."""

        gen = FastMazeGenerator.generate(width, height, diagonals=False)

        final_grid = None
        last_visited = 0
        total_cells = width * height

        for item in gen:
            if not self._should_continue():
                return

            if isinstance(item, int):
                visited = item
                last_visited = visited
                progress = min(1.0, visited / total_cells)

                self._queue_update(MazeGenerationUpdate(
                    cell=None,
                    progress=progress,
                    total_cells=total_cells,
                    visited_cells=visited,
                    message=f"Generating maze... {visited} cells visited",
                    is_complete=False
                ))
            else:
                final_grid = item

        if final_grid and self._should_continue():
            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.9,
                total_cells=total_cells,
                visited_cells=last_visited,
                message="Finalizing maze structure...",
                is_complete=False
            ))

            cells = maze._cells
            OPEN_VAL = 1
            STATE_OPEN = State.OPEN

            # Efficiently update cells
            count = 0
            batch_size = 50000

            # We bypass the standard update mechanism for speed
            # and trigger a full redraw at the end.

            for x in range(width):
                # Optimization: Cache column list
                col = cells[x]
                for y in range(height):
                    # Direct grid access: grid is row-major (y * width + x)
                    if final_grid[y * width + x] == OPEN_VAL:
                        # Direct state assignment
                        col[y].state = STATE_OPEN

                count += height
                if count >= batch_size:
                    if not self._should_continue():
                        return
                    count = 0

            # Force full redraw update
            if maze._renderer:
                maze._renderer.mark_full_redraw()

            # Ensure maze knows it needs write if no renderer yet
            maze._needs_write = True

            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=1.0,
                total_cells=total_cells,
                visited_cells=total_cells,
                message="Maze generation complete!",
                is_complete=True
            ))

    def _run_legacy_generation(self, maze: 'Maze', total_cells: int) -> None:
        """Original object-based generation for diagonals support."""
        unvisited_cells = set(
            [cell for column in maze._cells for cell in column])
        stack: list[Cell] = []
        current = maze._cells[0][0]
        visited_count = 0
        update_frequency = max(1, total_cells // 100)

        while unvisited_cells and self._should_continue():
            current.mark_as_open()
            visited_count += 1

            neighbors = current.get_unvisited_neighbors()
            visited_count += len(neighbors) // 2

            if current in unvisited_cells:
                unvisited_cells.remove(current)
                visited_count += 1

                if visited_count % update_frequency == 0 or visited_count >= total_cells:
                    progress = min(1.0, visited_count / total_cells)
                    self._queue_update(MazeGenerationUpdate(
                        cell=current,
                        progress=progress,
                        total_cells=total_cells,
                        visited_cells=visited_count,
                        message=f"Generating maze... {visited_count}/{total_cells} cells",
                        is_complete=False
                    ))

            if len(neighbors) > 0:
                stack.append(current)
                current = random.choice(neighbors)
            elif len(stack) > 0:
                current = stack.pop()
            else:
                break

        self._queue_update(MazeGenerationUpdate(
            cell=None,
            progress=1.0,
            total_cells=total_cells,
            visited_cells=visited_count,
            message="Maze generation complete!" if not self.is_cancelled else "Maze generation cancelled",
            is_complete=True
        ))
