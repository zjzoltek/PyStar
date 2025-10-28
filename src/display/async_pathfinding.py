"""
Asynchronous pathfinding implementation that decouples algorithm execution from rendering.
"""

import threading
import queue
from typing import Optional, Callable
from dataclasses import dataclass
import models
from enums import PathUpdate


@dataclass
class PathfindingUpdate:
    """Represents a single update from the pathfinding algorithm."""
    cell: Optional[models.Cell]
    update_type: PathUpdate
    path: Optional[list[models.Node]] = None


class AsyncPathfinder:
    """
    Runs pathfinding in a separate thread and communicates updates via queue.
    This allows the algorithm to run at full speed while the main thread
    renders updates at its own pace.
    """

    def __init__(self) -> None:
        self._update_queue: queue.Queue[PathfindingUpdate] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = False

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
        if self._thread and self._thread.is_alive():
            return  # Already running

        self._running = True
        self._thread = threading.Thread(
            target=self._run_pathfinding,
            args=(endpoints, on_complete),
            daemon=True
        )
        self._thread.start()

    def _run_pathfinding(
        self,
        endpoints: models.PathEndpoints,
        on_complete: Optional[Callable]
    ) -> list[models.Node]:
        """Run A* algorithm in background thread."""
        assert endpoints.start, endpoints.end
        
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

        while openlist and self._running:
            current = heappop(openlist)
            closedlist.add(current.cell)

            # Check if we reached the goal
            if current.cell == endpoints.end:
                path: list[models.Node] = []
                while current.parent is not None:
                    if not current.cell.is_terminator():
                        # Queue route update
                        self._update_queue.put(
                            PathfindingUpdate(current.cell, PathUpdate.ROUTE)
                        )
                    path.append(current)
                    current = current.parent

                # Signal completion
                self._update_queue.put(
                    PathfindingUpdate(None, PathUpdate.COMPLETE, path)
                )
                if on_complete:
                    on_complete(path)
                self._running = False
                return path

            # Mark cell as searched
            if not current.cell.is_terminator():
                self._update_queue.put(
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
        self._update_queue.put(
            PathfindingUpdate(None, PathUpdate.COMPLETE, None)
        )

        if on_complete:
            on_complete(None)
            
        self._running = False
        return []

    def process_updates(self, batch_size: int = 10) -> list[PathfindingUpdate]:
        """
        Process pending updates from the pathfinding thread.

        Args:
            batch_size: Maximum number of updates to process

        Returns:
            List of updates to apply
        """
        updates = []
        try:
            for _ in range(batch_size):
                update = self._update_queue.get_nowait()
                updates.append(update)

                # Apply the update to the cell
                if update.cell:
                    if update.update_type == PathUpdate.SEARCHED:
                        update.cell.mark_as_searched()
                    elif update.update_type == PathUpdate.ROUTE:
                        update.cell.mark_as_route()

        except queue.Empty:
            pass

        return updates

    def stop(self) -> None:
        """Stop the pathfinding thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    @property
    def is_running(self) -> bool:
        """Check if pathfinding is currently running."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def has_updates(self) -> bool:
        """Check if there are pending updates."""
        return not self._update_queue.empty()
