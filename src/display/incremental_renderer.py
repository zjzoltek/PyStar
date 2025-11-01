from __future__ import annotations

from dataclasses import dataclass
from queue import Queue
from time import perf_counter
from typing import Optional, Set, TYPE_CHECKING

import pygame

import models

if TYPE_CHECKING:
    from maze.depth_first import Maze

@dataclass(slots=True)
class RenderBatch:
    """Result of an incremental render pass."""

    surface: pygame.Surface
    rects: list[pygame.Rect]

    def __bool__(self) -> bool:  # pragma: no cover - convenience for callers
        return bool(self.rects)


class IncrementalRenderer:
    """
    Implements incremental rendering with dirty rectangle optimization.
    Only redraws cells that have changed, dramatically improving performance.
    """

    def __init__(self, surface: pygame.Surface) -> None:
        self._surface = surface
        self._dirty_cells: Set[models.Cell] = set()
        self._render_queue: Queue[models.Cell] = Queue()
        self._batch_size = 10  # Number of cells to batch before rendering
        self._last_render_time = 0.0
        self._render_interval = 1/120  # 120 FPS for smooth animation
        self._full_redraw_needed = True
        self._cached_surface: pygame.Surface

    def mark_cell_dirty(self, cell: models.Cell) -> None:
        """Mark a cell as needing redraw."""
        self._dirty_cells.add(cell)

    def mark_full_redraw(self) -> None:
        """Mark that a full redraw is needed (e.g., after maze generation)."""
        self._full_redraw_needed = True
        self._dirty_cells.clear()

    def add_to_render_queue(self, cell: models.Cell) -> None:
        """Add a cell to the render queue for batched updates."""
        self._render_queue.put(cell)

    def render_maze(
        self,
        maze: Maze,
        width: int,
        height: int,
        force_immediate: bool = False
    ) -> Optional[RenderBatch]:
        """
        Render the maze with incremental updates.

        Args:
            maze: The maze to render
            width: Surface width
            height: Surface height
            force_immediate: Force immediate rendering without batching

        Returns:
            Updated surface if changes were made, None otherwise
        """
        current_time = perf_counter()

        # Check if we need a full redraw
        if self._full_redraw_needed:
            return self._render_full_maze(maze, width, height)

        # Process queued cells if we have enough or time has passed
        should_render = (
            force_immediate or
            self._render_queue.qsize() >= self._batch_size or
            (current_time - self._last_render_time) > self._render_interval
        )

        if should_render and not self._render_queue.empty():
            while not self._render_queue.empty():
                cell = self._render_queue.get()
                self._dirty_cells.add(cell)

        # If no dirty cells, return cached surface if available
        if not self._dirty_cells:
            return None

        # Create surface if needed
        if self._cached_surface is None:
            self._cached_surface = pygame.Surface((width, height)).convert()

        dirty_rects: list[pygame.Rect] = []
        seen_rects: set[tuple[int, int, int, int]] = set()

        for cell in self._dirty_cells:
            rect = self._render_cell(cell, self._cached_surface)
            key = (rect.x, rect.y, rect.width, rect.height)
            if key not in seen_rects:
                seen_rects.add(key)
                dirty_rects.append(rect)

        self._dirty_cells.clear()
        self._last_render_time = current_time

        return RenderBatch(self._cached_surface, dirty_rects)

    def _render_full_maze(self, maze: Maze, width: int, height: int) -> RenderBatch:
        """Render the entire maze from scratch."""
        self._cached_surface = pygame.Surface((width, height)).convert()

        # Render all cells
        for column in maze._cells:
            for cell in column:
                self._render_cell(cell, self._cached_surface)

        self._full_redraw_needed = False
        self._last_render_time = perf_counter()
        full_rect = self._cached_surface.get_rect()
        return RenderBatch(self._cached_surface, [full_rect])

    def _render_cell(self, cell: models.Cell, surface: pygame.Surface) -> pygame.Rect:
        """Render a single cell to the surface and return the affected rect."""
        rect = pygame.Rect(
            cell.x * cell.dimensions.width,
            cell.y * cell.dimensions.height,
            cell.dimensions.width,
            cell.dimensions.height
        )
        pygame.draw.rect(
            surface,
            cell.get_color(),
            rect
        )
        return rect


