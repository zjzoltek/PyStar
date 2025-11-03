import pygame
import sys
import logging
from log import ColorfulStreamHandler
from display import Director
from models import Dimensions

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, handlers=[ColorfulStreamHandler(sys.stdout)])
    pygame.init()
    pygame.key.set_repeat(500, 100)

    print("\n" + "=" * 60)
    print("PyStar - Optimized Visualization Suite")
    print("=" * 60)

    director = Director().bootstrap_for_test(Dimensions(1000, 1000), Dimensions(1, 1), True)
    director.handle_events_indefinitely()
