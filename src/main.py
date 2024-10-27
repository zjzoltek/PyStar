import pygame
import sys
import logging
from log import ColorfulStreamHandler
from display import Director

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, handlers=[ColorfulStreamHandler(sys.stdout)])
    pygame.init()
    pygame.key.set_repeat(500, 100)
    Director().bootstrap().handle_events_indefinitely()
