import pygame
from a_star import PathFinder
import sys
import logging
from log import ColorfulStreamHandler
from display.screen import Screen

def main():
    logging.basicConfig(level=logging.DEBUG, handlers=[ColorfulStreamHandler(sys.stdout)])
    pygame.init()
    s = Screen().setup()
    PathFinder(s.surf, s.cell_dimensions, s.window_dimensions, s.diagonals)

if __name__ == '__main__':
    main()