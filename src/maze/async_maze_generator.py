"""
Asynchronous maze generation implementation that decouples algorithm execution from rendering.
"""

import random
from typing import Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass
from models import Cell, Dimensions
from maze.async_operation_manager import AsyncOperationManager

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
        diagonals: bool,
        on_complete: Optional[Callable[[bool], None]] = None,
        on_progress: Optional[Callable[[MazeGenerationUpdate], None]] = None
    ) -> None:
        """
        Start maze generation in a background thread.

        Args:
            maze: The maze object to populate
            cell_size: Dimensions for each cell
            diagonals: Whether to include diagonal connections
            on_complete: Callback when generation completes (receives success bool)
            on_progress: Callback for progress updates
        """
        self.start_async(
            target_method=self._run_maze_generation,
            args=(maze, cell_size, diagonals, on_complete, on_progress),
            name="MazeGeneration"
        )

    def _run_maze_generation(
        self,
        maze: 'Maze',
        cell_size: Dimensions,
        diagonals: bool,
        on_complete: Optional[Callable[[bool], None]],
        on_progress: Optional[Callable[[MazeGenerationUpdate], None]]
    ) -> None:
        """Run maze generation algorithm in background thread."""
        try:
            # Generate cell grid first
            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.0,
                total_cells=0,
                visited_cells=0,
                message="Initializing maze structure...",
                is_complete=False
            ))

            # Call the maze's _generate_cells method
            maze._generate_cells(cell_size, diagonals)

            total_cells = sum(len(column) for column in maze._cells)

            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.05,
                total_cells=total_cells,
                visited_cells=0,
                message=f"Starting generation of {total_cells} cells...",
                is_complete=False
            ))

            # Now run the depth-first search algorithm incrementally
            unvisited_cells = set([cell for column in maze._cells for cell in column])
            stack: list[Cell] = []
            current = maze._cells[0][0]
            visited_count = 0
            update_frequency = max(1, total_cells // 100)  # Update at least 100 times

            while unvisited_cells and self._should_continue():
                current.mark_as_open()
                if current in unvisited_cells:
                    unvisited_cells.remove(current)
                    visited_count += 1

                    # Send progress update periodically
                    if visited_count % update_frequency == 0 or visited_count == total_cells:
                        progress = visited_count / total_cells
                        self._queue_update(MazeGenerationUpdate(
                            cell=current,
                            progress=progress,
                            total_cells=total_cells,
                            visited_cells=visited_count,
                            message=f"Generating maze... {visited_count}/{total_cells} cells",
                            is_complete=False
                        ))

                        # Call progress callback if provided
                        if on_progress:
                            on_progress(MazeGenerationUpdate(
                                cell=current,
                                progress=progress,
                                total_cells=total_cells,
                                visited_cells=visited_count,
                                message=f"Generating maze... {visited_count}/{total_cells} cells",
                                is_complete=False
                            ))

                neighbors = current.get_unvisited_neighbors()
                if len(neighbors) > 0:
                    stack.append(current)
                    current = random.choice(neighbors)
                elif len(stack) > 0:
                    current = stack.pop()
                else:
                    break

            # Signal completion
            success = not self.is_cancelled
            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=1.0,
                total_cells=total_cells,
                visited_cells=visited_count,
                message="Maze generation complete!" if success else "Maze generation cancelled",
                is_complete=True
            ))

            if on_complete:
                on_complete(success)

        except Exception as e:
            # Handle any errors during generation
            self._queue_update(MazeGenerationUpdate(
                cell=None,
                progress=0.0,
                total_cells=0,
                visited_cells=0,
                message=f"Maze generation failed: {str(e)}",
                is_complete=True
            ))
            if on_complete:
                on_complete(False)
        finally:
            self._running = False

    # All update processing, cancellation, and status checking methods
    # are inherited from AsyncOperationManager