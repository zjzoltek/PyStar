from collections.abc import Iterable
from logging import Logger
from typing import ClassVar

import pygame
from colorama import just_fix_windows_console

import a_star


class DisplayController:
    _is_initialized: ClassVar[bool] = False
    
    @staticmethod
    def initialize() -> None:
        if DisplayController._is_initialized:
            raise RuntimeError('Display controller is already initialized')
        
        just_fix_windows_console()
        pygame.init()
        DisplayController._is_initialized = True

    @staticmethod
    def _is_valid_dimension(t: Iterable[int]) -> Iterable[str]:
        validation_errors: list[str] = []
        
        if len(t) != 2:
            validation_errors.append(f'Expected two arguments, got: {t}')
            return validation_errors
        
        if t[0] <= 0:
            validation_errors.append(f'Expected width to be a positive integer, got {t[0]}')
        
        if t[1] <= 0:
            validation_errors.append(f'Expected height to be a positive integer, got {t[1]}')
        
        return validation_errors
    
    @staticmethod
    def _request_dimensions_from_user(prompt: str) -> tuple[int, int]:
        while True:
            try:
                dimensions = input(f'{prompt}? Seperate width and height by space eg. 1200 800 =>').split(' ')
                validation_errors = DisplayController._is_valid_dimension(dimensions)
                if validation_errors:
                    
                    print('Cell width and height must be two positive integers separated by a space')
                    continue
                    
                return dimensions
            except ValueError as e:
                print(f'Error: {e}')
                continue

    def __init__(self):
        self._win_w: int = 0
        self._win_h: int = 0
        self._cell_w: int = 0
        self._cell_h: int = 0
    
    def get_display_dimensions() -> tuple[int, int]:
        return DisplayController._request_dimensions_from_user(prompt='Window dimensions')
    
    def get_cell_dimensions() -> tuple[int, int]:
        return DisplayController._request_dimensions_from_user(prompt='Cell dimensions')\
            
    def display_user_manual() -> None:
        print('Controls:')
        print('m - Re-Generate Maze')
        print('f - Find path with current maze (start and end points will be generated if not done so already)')
        print('p - Generate random start and end points')
        print('c - Clear maze colors and reset start and end points')
        print('x - Clear path, but not start and end colors')
        print('z - Toggle drawboard')