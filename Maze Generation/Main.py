from random import randint
import Pathfinder
import pygame
from time import time
from pygame.locals import *
import sys

from Mazers import Depth_First

FPSCLOCK = None
DISPLAYSURF = None

WINWIDTH = 200
WINHEIGHT = 100
BASIC_FONT = None

MAZE = Depth_First.Maze(WINWIDTH, WINHEIGHT)


def main(random=False):
    global FPSCLOCK, DISPLAYSURF, BASIC_FONT

    pygame.init()

    BASIC_FONT = pygame.font.Font(pygame.font.get_default_font(), 18)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    print "\n\n"

    print "Generating maze . . ."
    MAZE.generate(randint(0, 9999999999))

    print "Finding path . . ."
    p = Pathfinder.Pathfinder(MAZE.cells, DISPLAYSURF, WINWIDTH, WINHEIGHT, FPSCLOCK)

    if not random:
        start = p.get_point(0, 0)
        goal = p.get_point(150, 25)
    else:
        start = p.get_random_point()
        goal = p.get_random_point()

    print "START: (%d, %d)\nEND: (%d, %d)" % (start.x, start.y, goal.x, goal.y)
    b = time()
    p.a_star(start, goal)
    e = time()
    print "FOUND PATH IN %f SECONDS" % (e - b)
    while True:
        handle_events()
        pygame.display.update()
        FPSCLOCK.tick(120)


def handle_events():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == KEYUP:
            if event.key == K_r:
                main()
            elif event.key == K_p:
                main(True)

    pygame.event.pump()

if __name__ == '__main__':
    print "Controls:\n"
    print "r - Remake maze and reset path\n"
    print "p - Change start and end points to random and reset path\n"
    main()
