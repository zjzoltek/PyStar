import Pathfinder
import pygame

DISPLAYSURF = None
BASIC_FONT = None

def main():
    global DISPLAYSURF, BASIC_FONT

    print('\n')

    win_w, win_h = get_windims()
    box_w, box_h = get_boxdims(win_w, win_h)
    diagonals = get_diagonals()

    pygame.init()
    BASIC_FONT = pygame.font.Font(pygame.font.get_default_font(), 18)
    DISPLAYSURF = pygame.display.set_mode((win_w, win_h))
    Pathfinder.Pathfinder({"win_dims": (win_w, win_h), "box_dims": (box_w, box_h), "diagonal": diagonals}, DISPLAYSURF, win_w, win_h)

def get_diagonals():
    diagonals = input("Would you like to give AStar the ability to move diagonally? Y/N (Default No) =>")
    return diagonals.lower() in ("y", "yes")

def get_windims():
    while True:
        fullscreen = input("Window size? Seperate width and height by space eg. 1200 800 =>")
        fullscreen = fullscreen.split()
        if len(fullscreen) != 2:
            print("Incorrect number of args. Try again")
            print('\n')
            continue
        else:
            try:
                return int(fullscreen[0]), int(fullscreen[1])
            except ValueError:
                print("Either width or height is not a number. No decimals or chars please")
                continue


def get_boxdims(win_w, win_h):
    while True:
        dims = input('Cell dimensions? Seperate width and height with space eg. 12 12 =>')
        fdims = dims.split()
        if len(fdims) != 2:
            print("Incorrect number of args. Try again")
            print('\n')
            continue
        else:
            try:
                w, h = int(fdims[0]), int(fdims[1])
                if w * h > win_h * win_w:
                    print("Cell dimensions cannot be greater than screen dimensions of {}x{}".format(win_w, win_h))
                    continue
                return w, h
            except ValueError:
                print("Either width or height is not a number. No decimals or chars please")
                continue

if __name__ == '__main__':
    print("Controls:")
    print("m - Re-Generate Maze")
    print("f - Find path with current maze (start and end points will be generated if not done so already)")
    print("p - Generate random start and end points")
    print("c - Clear maze colors and reset start and end points")
    print("x - Clear path, but not start and end colors")
    print("k (during path find) - Stop pathfinding")
    print("r - Re-prompt for dimensions and diagonal allowance")
    print("z - Toggle drawboard")
    main()
