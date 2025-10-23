import random
from typing import Optional
import pygame

from log import timed
from models import Cell, Dimensions, ICellStateListener
from display.incremental_renderer import RenderBatch, VisualizationRenderer

class Maze(ICellStateListener):
    def __init__(self, width: int, height: int) -> None:
        self._width: int = width
        self._height: int = height
        self._cells: list[list[Cell]] = []
        self._needs_write: bool = False
        self._renderer: Optional[VisualizationRenderer] = None
        self._changed_cells: set[Cell] = set()
    
    @timed('Maze.generate')
    def generate(self, cell_size: Dimensions, diagonals: bool) -> None:
        self._generate_cells(cell_size, diagonals)
        self._populate_cells()

    def set_renderer(self, surface: pygame.Surface, fps: int = 60) -> None:
        """Set up the visualization renderer."""
        self._renderer = VisualizationRenderer(surface, fps)

    def draw_surf(self, width: int, height: int) -> RenderBatch | None:
        """Draw the maze surface using incremental rendering."""
        if self._renderer:
            # Use incremental renderer for better performance
            if self._needs_write:
                # Add changed cells to render queue
                for cell in self._changed_cells:
                    self._renderer.visualize_cell_change(cell)
                self._changed_cells.clear()
                self._needs_write = False

            return self._renderer.render_frame(self, width, height)
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
        for row in self._cells:
            for cell in row:
                if cell.x == int((x / cell.dimensions.height)) \
                        and cell.y == int((y / cell.dimensions.height)):
                    return cell
        
        return None
                
    def on_cell_state_change(self, cell: Optional[Cell] = None) -> None:
        """Called when a cell's state changes."""
        self._needs_write = True
        if cell:
            self._changed_cells.add(cell)
       
    def _populate_cells(self) -> None:
        """Generate maze using depth-first search."""
        unvisited_cells = set([cell for column in self._cells for cell in column])
        stack: list[Cell] = []
        current = self._cells[0][0]

        while unvisited_cells:
            current.mark_as_open()
            if current in unvisited_cells:
                unvisited_cells.remove(current)

            neighbors = current.get_unvisited_neighbors()
            if len(neighbors) > 0:
                stack.append(current)
                current = random.choice(neighbors)
            elif len(stack) > 0:
                current = stack.pop()
            else:
                break

        # Mark full redraw needed after maze generation
        if self._renderer:
            self._renderer.mark_full_redraw()

    def _generate_cells(self, cell_size: Dimensions, diagonals: bool) -> None:
        w = int(self._width / cell_size.width)
        h = int(self._height / cell_size.height)
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
