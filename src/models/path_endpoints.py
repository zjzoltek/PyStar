from dataclasses import dataclass
from typing import Optional
from models.cell import Cell


@dataclass
class PathEndpoints:
    """Manages the start and end points for pathfinding operations."""

    start: Optional[Cell] = None
    end: Optional[Cell] = None

    def is_complete(self) -> bool:
        """Check if both endpoints are selected."""
        return self.start is not None and self.end is not None

    def is_empty(self) -> bool:
        """Check if no endpoints are selected."""
        return self.start is None and self.end is None

    def clear(self) -> None:
        """Clear both endpoints and reset their cell states."""
        if self.start:
            self.start.mark_as_open()
            self.start = None

        if self.end:
            self.end.mark_as_open()
            self.end = None

    def select_cell(self, cell: Optional[Cell]) -> None:
        """
        Select a cell as an endpoint.
        First click sets start, second sets end.
        Third click clears both and starts over.
        """
        if cell is None:
            return

        # If both are set, clear and start over
        if self.is_complete():
            self.clear()

        # Set start or end based on current state
        if self.start is None:
            self.start = cell
            cell.mark_as_start()
        elif self.end is None:
            self.end = cell
            cell.mark_as_end()

    def set_random_endpoints(self, start_cell: Cell, end_cell: Cell) -> None:
        """Set specific cells as endpoints (used for random generation)."""
        self.clear()
        self.start = start_cell
        self.end = end_cell
        start_cell.mark_as_start()
        end_cell.mark_as_end()
