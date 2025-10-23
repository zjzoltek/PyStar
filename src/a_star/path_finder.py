from heapq import heappop, heappush
from math import sqrt
from typing import final, Optional, Callable

from pygame.locals import *

from log import timed
import models

@final
class PathFinder:
    def __init__(self):
        raise TypeError(f'{PathFinder.__name__} is a static class and cannot be instantiated')

    @staticmethod
    def _get_distance(start, goal) -> float:
        dx = float(start.x - goal.x)
        dy = float(start.y - goal.y)
        dist = float(sqrt(dx * dx + dy * dy))

        return dist
    
    @staticmethod
    @timed('PathFinder.find_path')
    def find_path(endpoints: models.PathEndpoints, tickFn: Optional[Callable] = None) -> Optional[list[models.Node]]:
        assert(endpoints.start is not None)
        assert(endpoints.end is not None)

        openlist: list[models.Node] = []
        closedlist: set[models.Cell] = set()

        current = models.Node(cell=endpoints.start, parent=None, gCost=0, hCost=PathFinder._get_distance(endpoints.start, endpoints.end))
        heappush(openlist, current)

        while openlist:
            current = heappop(openlist)
            closedlist.add(current.cell)

            if current.cell.x == endpoints.end.x and current.cell.y == endpoints.end.y:
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
                    
                gcost = current.gCost + PathFinder._get_distance(current.cell, cell)
                hcost = PathFinder._get_distance(cell, endpoints.end)
                n = models.Node(cell, current, gcost, hcost)
                heappush(openlist, n)

            if tickFn:
                tickFn()

        return None
