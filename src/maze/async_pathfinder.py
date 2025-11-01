"""
Asynchronous pathfinding implementation that decouples algorithm execution from rendering.
Moved from display module to maze module for better cohesion.
"""

from typing import Optional, Callable
from dataclasses import dataclass
import models
from enums import PathUpdate
from maze.async_operation_manager import AsyncOperationManager


@dataclass
class PathfindingUpdate:
    """Represents a single update from the pathfinding algorithm."""
    cell: Optional[models.Cell]
    update_type: PathUpdate
    path: Optional[list[models.Node]] = None


class AsyncPathfinder(AsyncOperationManager[PathfindingUpdate]):
    """
    Runs pathfinding in a separate thread and communicates updates via queue.
    This allows the algorithm to run at full speed while the main thread
    renders updates at its own pace.

    Inherits thread management, queue handling, and cancellation from AsyncOperationManager.
    """

    def find_path_async(
        self,
        endpoints: models.PathEndpoints,
        on_complete: Optional[Callable[[Optional[list[models.Node]]], None]] = None
    ) -> None:
        """
        Start pathfinding in a background thread.

        Args:
            endpoints: Start and end points for pathfinding
            on_complete: Callback when pathfinding completes
        """
        self.start_async(
            target_method=self._run_pathfinding,
            args=(endpoints, on_complete),
            name="Pathfinding"
        )

    def _run_pathfinding(
        self,
        endpoints: models.PathEndpoints,
        on_complete: Optional[Callable]
    ) -> list[models.Node]:
        """Run A* algorithm in background thread."""
        assert endpoints.start and endpoints.end

        from heapq import heappop, heappush
        from math import sqrt

        def get_distance(start, goal) -> float:
            dx = float(start.x - goal.x)
            dy = float(start.y - goal.y)
            return float(sqrt(dx * dx + dy * dy))

        openlist: list[models.Node] = []
        closedlist: set[models.Cell] = set()

        current = models.Node(
            cell=endpoints.start,
            parent=None,
            gCost=0,
            hCost=get_distance(endpoints.start, endpoints.end)
        )
        heappush(openlist, current)

        while openlist and self._should_continue():
            current = heappop(openlist)
            closedlist.add(current.cell)

            # Check if we reached the goal
            if current.cell == endpoints.end:
                path: list[models.Node] = []
                while current.parent is not None:
                    if not current.cell.is_terminator():
                        # Queue route update
                        self._queue_update(
                            PathfindingUpdate(current.cell, PathUpdate.ROUTE)
                        )
                    path.append(current)
                    current = current.parent

                # Signal completion
                self._queue_update(
                    PathfindingUpdate(None, PathUpdate.COMPLETE, path)
                )
                if on_complete:
                    on_complete(path)
                self._running = False
                return path

            # Mark cell as searched
            if not current.cell.is_terminator():
                self._queue_update(
                    PathfindingUpdate(current.cell, PathUpdate.SEARCHED)
                )

            # Explore neighbors
            for cell in current.cell.neighbors:
                if not cell.is_transversible() or cell in closedlist:
                    continue

                gcost = current.gCost + get_distance(current.cell, cell)
                hcost = get_distance(cell, endpoints.end)
                n = models.Node(cell, current, gcost, hcost)
                heappush(openlist, n)

        # No path found
        self._queue_update(
            PathfindingUpdate(None, PathUpdate.COMPLETE, None)
        )

        if on_complete:
            on_complete(None)

        self._running = False
        return []

    def process_updates(self, batch_size: int = 10) -> list[PathfindingUpdate]:
        """
        Process pending updates from the pathfinding thread.
        Overridden to apply updates directly to cells.

        Args:
            batch_size: Maximum number of updates to process

        Returns:
            List of updates to apply
        """
        updates = super().process_updates(batch_size)

        # Apply the updates to cells
        for update in updates:
            if update.cell:
                if update.update_type == PathUpdate.SEARCHED:
                    update.cell.mark_as_searched()
                elif update.update_type == PathUpdate.ROUTE:
                    update.cell.mark_as_route()

        return updates