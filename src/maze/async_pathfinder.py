from typing import Optional, Callable
from dataclasses import dataclass
import models
from enums import PathUpdate
from maze.async_operation_manager import AsyncOperationManager


@dataclass
class PathfindingUpdate:
    cell: Optional[models.Cell]
    update_type: PathUpdate
    path: Optional[list[models.Node]] = None


class AsyncPathfinder(AsyncOperationManager[PathfindingUpdate]):
    def find_path_async(
        self,
        endpoints: models.PathEndpoints,
        on_complete: Optional[Callable[[Optional[list[models.Node]]], None]] = None
    ) -> None:
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

            if current.cell == endpoints.end:
                path: list[models.Node] = []
                while current.parent is not None:
                    if not current.cell.is_terminator():
                        self._queue_update(
                            PathfindingUpdate(current.cell, PathUpdate.ROUTE)
                        )
                    path.append(current)
                    current = current.parent

                self._queue_update(
                    PathfindingUpdate(None, PathUpdate.COMPLETE, path)
                )
                if on_complete:
                    on_complete(path)
                self._running = False
                return path

            if not current.cell.is_terminator():
                self._queue_update(
                    PathfindingUpdate(current.cell, PathUpdate.SEARCHED)
                )

            for cell in current.cell.neighbors:
                if not cell.is_transversible() or cell in closedlist:
                    continue

                gcost = current.gCost + get_distance(current.cell, cell)
                hcost = get_distance(cell, endpoints.end)
                n = models.Node(cell, current, gcost, hcost)
                heappush(openlist, n)

        self._queue_update(
            PathfindingUpdate(None, PathUpdate.COMPLETE, None)
        )

        if on_complete:
            on_complete(None)

        self._running = False
        return []

    def process_updates(self, batch_size: int = 10) -> list[PathfindingUpdate]:
        updates = super().process_updates(batch_size)

        for update in updates:
            if update.cell:
                if update.update_type == PathUpdate.SEARCHED:
                    update.cell.mark_as_searched()
                elif update.update_type == PathUpdate.ROUTE:
                    update.cell.mark_as_route()

        return updates