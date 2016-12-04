from math import sqrt
from random import shuffle, randint
from Mazers import Depth_First
from pygame.locals import *
import sys
import pygame
import Main


class Pathfinder:
    def __init__(self, cells, displaysurf, width, height, maze_type):
        self.cells = cells
        self.surf = displaysurf
        self.w = width
        self.h = height

        if maze_type == Main.REG_MAZE:
            self.blitMethod = Depth_First.Maze.gen_surf_s

        elif maze_type == Main.BOX_MAZE:
            self.blitMethod = Depth_First.Maze.gen_surf_box_s

    def a_star(self, start, goal):
        start.color = (0, 0, 255)
        goal.color = (100, 255, 162)
        openlist = []
        closedlist = []

        current = Node(start, None, 0, self.get_distance(start, goal))

        openlist.append(current)

        while openlist:
            openlist.sort(key=lambda _node: _node.fCost)
            current = openlist[0]

            if current.cell.x == goal.x and current.cell.y == goal.y:
                path = []
                while current.parent is not None:
                    path.append(current)
                    current.cell.color = (0, 255, 0)
                    current = current.parent
                self.surf.blit(self.blitMethod(self.cells, self.w, self.h), (0, 0))
                pygame.display.update()
                return path

            openlist.remove(current)
            closedlist.append(current)
            current.cell.color = (255, 0, 0)

            self.handle_events()
            self.surf.blit(self.blitMethod(self.cells, self.w, self.h), (0, 0))
            pygame.display.update()

            n = [x for x in current.cell.get_neighbors(self.cells) if x.visited]

            for cell in n:
                if self.cell_in_list(cell, closedlist):
                    continue

                gcost = current.gCost + self.get_distance(current.cell, cell)
                hcost = self.get_distance(cell, goal)

                node = Node(cell, current, gcost, hcost)

                if not self.cell_in_list(cell, openlist):
                    openlist.append(node)

        return None

    @staticmethod
    def cell_in_list(cell, nodelist):
        for i in nodelist:
            if i.cell.x == cell.x and i.cell.y == cell.y:
                return True

        return False

    @staticmethod
    def better_sibling(node, openlist):
        for i in openlist:
            if i.cell == node.cell and i.fCost <= node.fCost:
                return True

        return False

    def get_random_point(self):
        l = [i for x in self.cells for i in x if i.visited]
        shuffle(l)
        return l[randint(0, len(l)-1)]

    @staticmethod
    def node_sorter(a, b):
        if b.fCost < a.fCost:
            return 1
        if b.fCost > a.fCost:
            return -1
        return 0

    @staticmethod
    def get_distance(start, goal):
        dx = float(start.x - goal.x)
        dy = float(start.y - goal.y)
        dist = float(sqrt(dx * dx + dy * dy))

        return dist

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == KEYUP:
                if event.key == K_r:
                    Main.main()
                elif event.key == K_p:
                    Main.main()
        pygame.event.pump()


class Node:
    def __init__(self, cell, parent, gcost, hcost):
        self.cell = cell
        self.parent = parent

        self.gCost = gcost
        self.hCost = hcost
        self.fCost = gcost + hcost
