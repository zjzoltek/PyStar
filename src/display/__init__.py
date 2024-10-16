from typing import Optional

import pygame

import log
from models import Dimensions


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
        valid_answers: set[str] = {'y', 'yes', 'n', 'no'}
        affirmative_answers: set[str] = {'y', 'yes'}
        
        while True:
            try:
                args = self._console.request('Would you like to give A* the ability to move diagonally (y/n)?')

                if len(args) != 1:
                    raise 'Incorrect number of arguments: expected either Y or N'
                
                answer = args[0].lower()
                
                if answer not in valid_answers:
                    raise 'Invalid: expected either Y or N'
                
                return answer in affirmative_answers
            except Exception as e:
                self._console.err(e)
                continue
            
    def _get_display_dimensions(self) -> Dimensions:
        while True:
            try:
                args = self._console.request('Window size? Input width followed by height (e.g. "500 500")')
        
                if len(args) != 2:
                    raise 'Incorrect number of arguments: expected two integers'
                
                w = int(args[0])
                h = int(args[1])
                
                if w <= 0:
                    raise 'Invalid: width must be a positive integer'
                if h <= 0:
                    raise 'Invalid: height must be a positive integer'
                
                return Dimensions(w, h)
            except Exception as e:
                self._console.err(e)
                continue

    def _get_cell_dimensions(self) -> Dimensions:
        while True:
            try:
                args = self._console.request('Cell size? (e.g. "10")')
        
                if len(args) > 1:
                    raise 'Incorrect number of arguments: expected one integer'
                
                cell_box_size = int(args[0])
                
                if cell_box_size <= 0:
                    raise 'Invalid: cell size must be a positive integer'
                
                return Dimensions(cell_box_size, cell_box_size)
            except Exception as e:
                self._console.err(e)
                continue

class Console:
    def __init__(self, prompt_end: str = '=>'):
        self._prompt_end = prompt_end
        self._logger = log.logging.getLogger(self.__qualname__)
    
    def request(self, prompt: str) -> list[str]:
        args = input(f'{prompt}{self._prompt_end}').split(' ')
        if not args:
            raise ValueError('No args provided')
        return args

    def out(self, content: str):
        self._logger.info(content)
        
    def err(self, content: str):
        self._logger.error(content)
