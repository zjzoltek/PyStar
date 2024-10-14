from collections.abc import Iterable
from typing import Self, Optional
from models import Dimensions
import logging
import pygame

class Display:
    @staticmethod
    def _ensure_valid_dimensions(t: Iterable[int]) -> None:
        validation_errors: list[str] = []
        
        if len(t) != 2:
            validation_errors.append(f'Expected two arguments, got: {t}')
            raise validation_errors
        
        if t[0] <= 0:
            validation_errors.append(f'Expected width to be a positive integer, got {t[0]}')
        
        if t[1] <= 0:
            validation_errors.append(f'Expected height to be a positive integer, got {t[1]}')
        
        raise validation_errors
        
    def __init__(self):
        self._surf: Optional[pygame.Surface] = None
        self.cell_dimensions: Optional[Dimensions] = None
        self.window_dimensions: Optional[Dimensions] = None
        self._logger = logging.getLogger(self.__qualname__)
        self._console = Console()
     
    def init(self) -> None:
        pygame.init()
        
        self.window_dimensions = self.get_display_dimensions()
        self.cell_dimensions = self.get_cell_dimensions()
        self._surf = pygame.display.set_mode(\
            (self.window_dimensions.width, self.window_dimensions.height), \
                pygame.HWSURFACE|pygame.DOUBLEBUF)
        
    def get_display_dimensions(self) -> Dimensions:
        return Display._request_dimensions_from_user(prompt='Window dimensions')
    
    def get_cell_dimensions(self) -> Dimensions:
        args = self._console.request('Cell size? (min. 1)')
        
        if not args:
            
        return Dimensions(cell_box_size, cell_box_size)
            
    @property
    def surf(self) -> pygame.Surface:
        return self._surf
    
    def display_user_manual() -> None:
        print('Controls:')
        print('m - Re-Generate Maze')
        print('f - Find path with current maze (start and end points will be generated if not done so already)')
        print('p - Generate random start and end points')
        print('c - Clear maze colors and reset start and end points')
        print('x - Clear path, but not start and end colors')
        print('z - Toggle drawboard')
        
class Console:
    def __init__(self, newline_length: int = 1, prompt_end='=>'):
        self._newline_length = newline_length
        self._prompt_end = prompt_end
        self._logger = logging.getLogger(self.__qualname__)
        
    def request(self, prompt: str) -> Dimensions:
        while True:
            try:
                return input(f'{prompt}{self._prompt_end}').split(' ')
            except Exception as e:
                self._err(f'{e}')
                continue

    def out(self, content: str):
        self._logger.info(content)
        
    def err(self, content: str):
        self._logger.error(content)