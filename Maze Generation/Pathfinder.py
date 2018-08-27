from math import sqrt
from random import shuffle, randint, seed
from Mazers import Depth_First
from pygame.locals import *
from time import time
import sys
import pygame
import Main


class Pathfinder:
    START_COLOR = (0, 0, 255)
    END_COLOR = (255, 20, 147)
    SEARCHED_COLOR = (255, 0, 0)
    PATH_COLOR = (0, 255, 0)
    FPS = 60

    DRAWING = 0x01
    AUTO = 0x02

    def __init__(self, main_args, displaysurf, width, height):
        self.surf = displaysurf
        self.fps = pygame.time.Clock()
        self.w = width
        self.h = height
        self.main_args = main_args
        self.maze = Depth_First.Maze(width, height, False)
        self.points = []
        self.keys = {}
        self.mode = self.AUTO
        self.seed = randint(0, 1000)
        if main_args['type'] == Main.REG_MAZE:
            self.maze.generate(self.seed)
            self.blitMethod = Depth_First.Maze.gen_surf_s

        elif main_args['type'] == Main.BOX_MAZE:
            self.maze.generate_box(self.seed, main_args['box_dims'], main_args['diagonal'])
            self.blitMethod = Depth_First.Maze.gen_surf_box_s

        self.cells = self.maze.cells
        self.highlighted_cell = [0, 0]
        self.update()
        pygame.display.update()
        self.handle_events()

    
    def a_star(self, start, goal):
        openlist = set()
        closedlist = set()

        current = Node(start, None, 0, self.get_distance(start, goal))

        openlist.add(current)

        while openlist:
            openlist = set(sorted(openlist, key=lambda _node: _node.fCost))
            current = openlist.pop()

            if current.cell.x == goal.x and current.cell.y == goal.y:
                path = []
                while current.parent is not None:
                    path.append(current)
                    if current.cell.color != self.END_COLOR:
                        current.cell.color = self.PATH_COLOR
                    current = current.parent
                self.surf.blit(self.blitMethod(self.cells, self.w, self.h), (0, 0))
                pygame.display.update()
                return path

            closedlist.add(current)
            if current.cell.color != self.START_COLOR:
                current.cell.color = self.SEARCHED_COLOR

            self.special_events()
            self.surf.blit(self.blitMethod(self.cells, self.w, self.h), (0, 0))
            pygame.display.update()

            n = [x for x in current.cell.get_neighbors(self.cells) if x.visited]

            nodes = []
            for cell in n:
                gcost = current.gCost + self.get_distance(current.cell, cell)
                hcost = self.get_distance(cell, goal)
                node = Node(cell, current, gcost, hcost)
                nodes.append(node)

            for cell in n:
                if self.cell_in_list(cell, closedlist):
                    continue

                gcost = current.gCost + self.get_distance(current.cell, cell)
                hcost = self.get_distance(cell, goal)

                node = Node(cell, current, gcost, hcost)

                if not self.cell_in_list(cell, openlist):
                    openlist.add(node)

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
    def clamp(x, y, maxx, maxy, minx, miny):
        pair = []
        if x > maxx:
            pair.append(maxx)
        elif x < minx:
            pair.append(minx)
        else:
            pair.append(x)

        if y > maxy:
            pair.append(maxy)
        elif y < miny:
            pair.append(miny)
        else:
            pair.append(y)

        return pair

    def generate_random_start_end(self):
        self.reset_cell_colors()
        seed()
        self.points = [self.get_random_point(), self.get_random_point()]
        self.points[0].color = self.START_COLOR
        self.points[1].color = self.END_COLOR
        print("New points generated: Start: {}, {} | End: {}, {}".format(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))
        self.update()

    def set_all_cells_to_color(self, col):
        for array in self.cells:
            for cell in array:
                cell.color = col

    def reset_cell_colors(self, leave_start_end=False):
        for array in self.cells:
            for cell in array:
                if cell.visited:
                    if leave_start_end and cell.color in (self.START_COLOR, self.END_COLOR):
                        continue
                    else:
                        cell.color = (255, 255, 255)
                else:
                    cell.color = (0, 0, 0)
        self.update()

    def reset_maze(self, new_seed):
        if new_seed:
            self.seed = randint(0, 1000)
        if self.main_args['type'] == Main.BOX_MAZE:
            self.maze.generate_box(self.seed, self.main_args['box_dims'], self.main_args['diagonal'])
        elif self.main_args['type'] == Main.REG_MAZE:
            self.maze.generate(self.seed, self.main_args['diagonal'])

        self.cells = self.maze.cells
        self.update()

    def get_cell(self, x, y):
        for array in self.cells:
            for cell in array:
                if self.main_args['type'] == Main.BOX_MAZE:
                    if cell.x == int((x / self.main_args['box_dims'][0])) \
                            and cell.y == int((y / self.main_args['box_dims'][1])):
                        return cell
                else:
                    if cell.x == x and cell.y == y:
                        return cell

    def handle_events(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if len(self.points) == 2:
                            self.points = []
                            self.reset_cell_colors()
                        elif len(self.points) == 1:
                            cell = self.get_cell(event.pos[0], event.pos[1])
                            if cell.visited:
                                self.points.append(cell)
                                cell.color = self.END_COLOR
                        elif not self.points:
                            cell = self.get_cell(event.pos[0], event.pos[1])
                            if cell.visited:
                                self.points.append(cell)
                                cell.color = self.START_COLOR
                    if event.button == 3:
                        self.keys['button3'] = event.pos

                if event.type == MOUSEBUTTONUP:
                    if 'button'+str(event.button) in self.keys:
                        del self.keys['button'+str(event.button)]
                if event.type == KEYDOWN:
                    self.keys[event.key] = True
                    if event.key == K_d:
                        self.highlighted_cell[0] += self.main_args['box_dims'][0]
                    elif event.key == K_s:
                        self.highlighted_cell[1] += self.main_args['box_dims'][1]
                    elif event.key == K_a:
                        self.highlighted_cell[0] -= self.main_args['box_dims'][0]
                    elif event.key == K_w:
                        self.highlighted_cell[1] -= self.main_args['box_dims'][1]
                if event.type == KEYUP:
                    if event.key in self.keys:
                        del self.keys[event.key]

                    if event.key == K_z:
                        if self.mode == self.AUTO:
                            self.mode = self.DRAWING
                            self.set_all_cells_to_color((255, 255, 255))
                            for r in self.cells:
                                for c in r:
                                    c.visited = True
                        else:
                            self.reset_maze(False)
                            self.cells = self.maze.cells
                            self.mode = self.AUTO
                            self.points = []

                    if event.key == K_r:
                        Main.main()
                    elif event.key == K_f:
                        self.reset_cell_colors(True)
                        if not self.points or len(self.points) < 2:
                            self.generate_random_start_end()
                        print("Finding path . . .")
                        print("Start: ({}, {})\nEnd: ({}, {})".format(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))
                        b = time()
                        self.a_star(self.points[0], self.points[1])
                        e = time()
                        print("Done in {} seconds".format(e - b))
                    elif event.key == K_p:
                        self.generate_random_start_end()
                    elif event.key == K_m:
                        self.reset_maze(True)
                    elif event.key == K_c:
                        if self.mode == self.AUTO:
                            self.reset_cell_colors()
                            self.points = []
                        else:
                            self.set_all_cells_to_color((255, 255, 255))
                            for r in self.cells:
                                for c in r:
                                    c.visited = True
                            self.points = []
                    elif event.key == K_x:
                        if self.mode == self.DRAWING:
                            for r in self.cells:
                                for c in r:
                                    if not c.visited:
                                        c.color = (255, 255, 255)
                                        c.visited = True
                            self.reset_cell_colors(True)
                        else:
                            self.reset_cell_colors(True)

                    elif event.key == K_SPACE:
                        if len(self.points) == 2:
                            self.points = []
                            self.reset_cell_colors()
                        elif len(self.points) == 1:
                            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
                            if hcell:
                                self.points.append(hcell)
                                hcell.color = self.END_COLOR
                        elif not self.points:
                            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
                            if hcell:
                                self.points.append(hcell)
                                hcell.color = self.START_COLOR
            self.update()
            pygame.event.pump()

            if K_RIGHT in self.keys:
                self.highlighted_cell[0] += self.main_args['box_dims'][0]
            elif K_DOWN in self.keys:
                self.highlighted_cell[1] += self.main_args['box_dims'][1]
            elif K_LEFT in self.keys:
                self.highlighted_cell[0] -= self.main_args['box_dims'][0]
            elif K_UP in self.keys:
                self.highlighted_cell[1] -= self.main_args['box_dims'][1]

            self.highlighted_cell = self.clamp(self.highlighted_cell[0],
                                               self.highlighted_cell[1], self.w - self.main_args['box_dims'][0],
                                               self.h - self.main_args['box_dims'][1], 0, 0)
            if K_v in self.keys and self.mode == self.DRAWING:
                hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
                hcell.visited = False
                hcell.color = (0, 0, 0)

            if 'button3' in self.keys and self.mode == self.DRAWING:
                hcell = self.get_cell(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                hcell.visited = False
                hcell.color = (0, 0, 0)

            if K_b in self.keys and self.mode == self.DRAWING:
                hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
                hcell.visited = True
                hcell.color = (255, 255, 255)

            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            pygame.draw.rect(self.surf, (0, 255, 0),
                             (self.highlighted_cell[0], self.highlighted_cell[1], hcell.box[0], hcell.box[1]))
            pygame.display.update()
            self.fps.tick(self.FPS)

    def special_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == KEYUP:
                if event.key == K_r:
                    Main.main()
                elif event.key == K_k:
                    print("A-Star Halted")
                    self.handle_events()
                elif event.key == K_f:
                    self.reset_cell_colors(True)
                    self.points = []
                    self.generate_random_start_end()
                    print("Finding path . . .")
                    print("START: ({}, {})\nEND: ({}, {})".format(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))
                    b = time()
                    self.a_star(self.points[0], self.points[1])
                    e = time()
                    print("FOUND PATH IN {} SECONDS".format(e - b))
                    self.handle_events()

    def update(self):
        self.surf.blit(self.blitMethod(self.cells, self.w, self.h), (0, 0))


class Node:
    def __init__(self, cell, parent, gcost, hcost):
        self.cell = cell
        self.parent = parent

        self.gCost = gcost
        self.hCost = hcost
        self.fCost = gcost + hcost
