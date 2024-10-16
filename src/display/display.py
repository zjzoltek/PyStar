from typing import Optional

import pygame

from models import Dimensions
from console import *

class Display:
    def __init__(self):
        self._surf: Optional[pygame.Surface] = None
        self._cell_dimensions: Optional[Dimensions] = None
        self._window_dimensions: Optional[Dimensions] = None
        self._diagonals: Optional[bool] = None
        self._console = Console()
     
    @property
    def surf(self) -> pygame.Surface:
        return self._surf
    
    @property
    def cell_dimensions(self) -> Optional[Dimensions]:
        return self._cell_dimensions
    
    @property
    def window_dimensions(self) -> Optional[Dimensions]:
        return self._window_dimensions
    
    @property
    def diagonals(self) -> Optional[bool]:
        return self._diagonals
    
    def setup(self) -> None:
        pygame.init()
        
        self._window_dimensions = self._get_display_dimensions()
        self._cell_dimensions = self._get_cell_dimensions()
        self._diagonals = self._get_diagonals()
        self._surf = pygame.display.set_mode(\
            (self._window_dimensions.width, self._window_dimensions.height), \
                pygame.HWSURFACE|pygame.DOUBLEBUF)
    
                
    def display_user_manual(self) -> None:
        self._console.out('Controls:')
        self._console.out('m - Re-Generate Maze')
        self._console.out('f - Find path with current maze (start and end points will be generated if not done so already)')
        self._console.out('p - Generate random start and end points')
        self._console.out('c - Clear maze colors and reset start and end points')
        self._console.out('x - Clear path, but not start and end colors')
        self._console.out('z - Toggle drawboard')
        
    def _get_diagonals(self) -> bool:
        return self._console.switch('Would you like to allow A* to move diagonally?')
            
    def _get_display_dimensions(self) -> Dimensions:
        while True:
            try:
                args = self._console.request('Window size? Input width followed by height (e.g. "500 500")')
        
                if len(args) != 2:
                    raise 'Expected (2) arguments'
                
                w = int(args[0])
                h = int(args[1])
                
                if w <= 0:
                    raise 'First arg (width) must be a positive integer'
                if h <= 0:
                    raise 'Second arg (height) must be a positive integer'
                
                return Dimensions(w, h)
            except Exception as e:
                self._console.err(e)
                continue

    def _get_cell_dimensions(self) -> Dimensions:
        while True:
            try:
                args = self._console.request('Cell size? (e.g. "10")')
        
                if len(args) > 1:
                    raise 'Expected (1) argument'
                
                cell_box_size = int(args[0])
                
                if cell_box_size <= 0:
                    raise 'Cell size must be a positive integer'
                
                return Dimensions(cell_box_size, cell_box_size)
            except Exception as e:
                self._console.err(e)
                continue