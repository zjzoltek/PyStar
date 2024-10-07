import pygame
from colorama import just_fix_windows_console

import a_star
from logging import Logger
from typing import ClassVar
from collections.abc import Iterable

class DisplayController:
    _is_initialized: ClassVar[bool] = False
    
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
    
    def initialize(self):
        if self._is_initialized:
            raise RuntimeError('Display controller is already initialized')
        
        just_fix_windows_console()
        pygame.init()
        self._is_initialized = True

    def get_display_dimensions():
        return DisplayController._request_dimensions_from_user(prompt='Window dimensions')
    
    def get_cell_dimensions():
        return DisplayController._request_dimensions_from_user(prompt='Cell dimensions')\
            
    def display_user_manual():
        print('Controls:')
        print('m - Re-Generate Maze')
        print('f - Find path with current maze (start and end points will be generated if not done so already)')
        print('p - Generate random start and end points')
        print('c - Clear maze colors and reset start and end points')
        print('x - Clear path, but not start and end colors')
        print('z - Toggle drawboard')


    
def main():
    just_fix_windows_console()
    
    print('\n')

    win_w, win_h = get_windims()
    box_w, box_h = get_boxdims(win_w, win_h)
    diagonals = get_diagonals()

    pygame.init()
    a_star.PathFinder(pygame.display.set_mode((win_w, win_h), pygame.HWSURFACE|pygame.DOUBLEBUF), (win_w, win_h), (box_w, box_h), diagonals)

def get_diagonals():
    diagonals = input('Would you like to give AStar the ability to move diagonally? Y/N (Default No) =>')
    return diagonals.lower() in ('y', 'yes')

def get_windims():
    while True:
        dims = input('Window size? Seperate width and height by space eg. 1200 800 =>')
        dims = dims.split()
        if len(dims) != 2:
            print('Incorrect number of args. Try again')
            print('\n')
            continue
        else:
            try:
                w, h = int(dims[0]), int(dims[1])
                if w * h == 0:
                    print('Cell width and height must be non-zero')
            except ValueError:
                print('Either width or height is not a number. No decimals or chars please')
                continue


def get_boxdims(win_w, win_h):
    while True:
        dims = input('Cell dimensions? Seperate width and height with space eg. 12 12 =>')
        dims = dims.split()
        if len(dims) != 2:
            print('Incorrect number of args. Try again')
            print('\n')
            continue
        else:
            try:
                w, h = int(dims[0]), int(dims[1])
                if w * h > win_h * win_w:
                    print('Cell dimensions cannot be greater than screen dimensions of {}x{}'.format(win_w, win_h))
                    continue
                if w * h == 0:
                    print('Cell width and height must be non-zero')
                    continue
                return w, h
            except ValueError:
                print('Either width or height is not a number. No decimals or chars please')
                continue

if __name__ == '__main__':
    print('Controls:')
    print('m - Re-Generate Maze')
    print('f - Find path with current maze (start and end points will be generated if not done so already)')
    print('p - Generate random start and end points')
    print('c - Clear maze colors and reset start and end points')
    print('x - Clear path, but not start and end colors')
    print('k (during path find) - Stop pathfinding')
    print('r - Re-prompt for dimensions and diagonal allowance')
    print('z - Toggle drawboard')
    main()
