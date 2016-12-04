from random import randint
import Pathfinder
import pygame
from time import time
from pygame.locals import *
import sys

from Mazers import Depth_First

FPSCLOCK = None
DISPLAYSURF = None

BASIC_FONT = None

BOX_MAZE = 0x01
REG_MAZE = 0x02


def main():
    global FPSCLOCK, DISPLAYSURF, BASIC_FONT

    print('\n')
    w = 0
    h = 0
    while True:
        dims = raw_input('Cell dimensions? Seperate width and height with space eg. 12 12 =>')
        fdims = dims.split()
        if len(fdims) != 2:
            print "Incorrect number of args. Try again"
            print '\n'
            continue
        else:
            try:
                w = int(fdims[0])
                h = int(fdims[1])
            except ValueError:
                print "Either width or height is not a number. No decimals or chars please"
                continue

            break

    diagonals = raw_input("Would you give AStar the ability to move diagonally? Y/N (Default No) =>")
    if diagonals.lower() in ("y", "yes"):
        diagonals = True
    else:
        diagonals = False

    win_w = 0
    win_h = 0
    while True:
        fullscreen = raw_input("Window size? Seperate width and height by space eg. 1200 800 =>")
        fullscreen = fullscreen.split()
        if len(fullscreen) != 2:
            print "Incorrect number of args. Try again"
            print()
            continue
        else:
            try:
                win_w = int(fullscreen[0])
                win_h = int(fullscreen[1])
            except ValueError:
                print "Either width or height is not a number. No decimals or chars please"
                continue

            break

    pygame.init()

    BASIC_FONT = pygame.font.Font(pygame.font.get_default_font(), 18)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((win_w, win_h))
    maze = Depth_First.Maze(win_w, win_h)
    if w == 1 and h == 1:
        maze_type = REG_MAZE
    else:
        maze_type = BOX_MAZE

    print "Generating maze . . ."
    if w == 1 and h == 1:
        maze.generate(randint(0, 9999999999), diagonals)
    else:
        maze.generate_box(randint(0, 9999999999), (w, h), diagonals)

    print "Finding path . . ."
    p = Pathfinder.Pathfinder(maze.cells, DISPLAYSURF, win_w, win_h, maze_type)

    start = p.get_random_point()
    goal = p.get_random_point()

    print "START: (%d, %d)\nEND: (%d, %d)" % (start.x, start.y, goal.x, goal.y)
    b = time()
    p.a_star(start, goal)
    e = time()
    print "FOUND PATH IN %d SECONDS" % (e - b)
    while True:
        handle_events()
        pygame.display.update()
        FPSCLOCK.tick(60)


def handle_events():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == KEYUP:
            if event.key == K_r:
                main()

    pygame.event.pump()

if __name__ == '__main__':
    print "Controls:\n"
    print "r - Remake maze, prompt for new cell dimensions and reset path\n"
    main()
