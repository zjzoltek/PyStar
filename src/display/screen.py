from typing import Optional, Self

import pygame

from display.console import *
from models.dimensions import Dimensions
from models.value_range import INF, ValueRange
from validation.has_length import HasLength
from validation.in_range import InRange
from validation.matches_type import MatchesType
from validation.validator import Validator


class Screen:
    def __init__(self) -> None:
        self._surf: pygame.Surface
        self._cell_dimensions: Optional[Dimensions] = None
        self._window_dimensions: Optional[Dimensions] = None
        self._diagonals: Optional[bool] = None
        self._console = Console(prompt_end=' ')
    
    @property
    def surf(self) -> pygame.Surface:
        assert self._surf is not None
        return self._surf
    
    @property
    def cell_dimensions(self) -> Dimensions:
        assert self._cell_dimensions is not None
        return self._cell_dimensions
    
    @property
    def window_dimensions(self) -> Dimensions:
        assert self._window_dimensions is not None
        return self._window_dimensions
    
    @property
    def diagonals(self) -> bool:
        assert self._diagonals is not None
        return self._diagonals
    
    def setup(self) -> None:
        pygame.init()
        
        self._window_dimensions = self._get_display_dimensions()
        self._cell_dimensions = self._get_cell_dimensions()
        self._diagonals = self._get_diagonals()
        self._surf = pygame.display.set_mode(\
            (self._window_dimensions.width, self._window_dimensions.height), \
                pygame.HWSURFACE|pygame.DOUBLEBUF)
    
    def setup_for_test(self, window_dimensions: Dimensions, cell_dimensions: Dimensions, diagonals: bool):
        self._window_dimensions = window_dimensions
        self._cell_dimensions = cell_dimensions
        self._diagonals = diagonals
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
        while True:
            try:
                return self._console.switch('Would you like to allow A* to move diagonally?')
            except Exception as e:
                self._console.err(str(e))
                continue
            
    def _get_display_dimensions(self) -> Dimensions:
        while True:
            try:
                item_validator = Validator((MatchesType(int())), InRange(ValueRange(minimum=1, maximum=INF, inclusiveMin=True)))
                set_validator = Validator(HasLength(2))
                args = self._console.request('Window size?', set_validator, item_validator)
                
                return Dimensions(int(args[0]), int(args[1]))
            except Exception as e:
                self._console.err(str(e))
                continue

    def _get_cell_dimensions(self) -> Dimensions:
        while True:
            try:
                item_validator = Validator(MatchesType(int()), \
                    InRange(ValueRange(minimum=1, maximum=INF, inclusiveMin=True)))
                set_validator = Validator(HasLength(1))
                args = self._console.request('Cell size?', set_validator, item_validator)
        
                size = int(args[0])
                return Dimensions(size, size)
            except Exception as e:
                self._console.err(str(e))
                continue