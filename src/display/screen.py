from typing import Optional, Self

import pygame

from models.dimensions import Dimensions
from display.console import *
from validation.validator import Validator
from validation.in_range import InRange
from validation.matches_type import MatchesType
from validation.has_length import HasLength

class Screen:
    def __init__(self) -> None:
        self._surf: Optional[pygame.Surface] = None
        self._cell_dimensions: Optional[Dimensions] = None
        self._window_dimensions: Optional[Dimensions] = None
        self._diagonals: Optional[bool] = None
        self._console = Console()
    
    @property
    def surf(self) -> Optional[pygame.Surface]:
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
    
    def setup(self) -> Self:
        pygame.init()
        
        self._window_dimensions = self._get_display_dimensions()
        self._cell_dimensions = self._get_cell_dimensions()
        self._diagonals = self._get_diagonals()
        self._surf = pygame.display.set_mode(\
            (self._window_dimensions.width, self._window_dimensions.height), \
                pygame.HWSURFACE|pygame.DOUBLEBUF)
        
        return self
    
                
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
                itemValidator = Validator(MatchesType(int()), InRange(minimum=1, unboundedMax=True, inclusiveMin=True))
                argsValidator = Validator(HasLength(2))
                
                args = self._console.request('Window size? Input width followed by height (e.g. "500 500")', argsValidator)
            
                w = int(args[0])
                h = int(args[1])
                
                for item in args:
                    itemValidator.validate(item)
                
                return Dimensions(w, h)
            except Exception as e:
                self._console.err(str(e))
                continue

    def _get_cell_dimensions(self) -> Dimensions:
        while True:
            try:
                itemValidator = Validator(MatchesType(int()), InRange(minimum=1, unboundedMax=True, inclusiveMin=True))
                argsValidator = Validator(HasLength(1))
                
                args = self._console.request('Cell size? (e.g. "10")', argsValidator)
        
                cell_box_size = int(args[0])
                itemValidator.validate(cell_box_size)
                
                return Dimensions(cell_box_size, cell_box_size)
            except Exception as e:
                self._console.err(str(e))
                continue