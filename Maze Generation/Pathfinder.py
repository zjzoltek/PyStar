import sys
from enum import Enum
from math import sqrt
from random import randint, seed, shuffle
from time import time

import Main
import pygame
from Mazers.Depth_First import Cell, Maze
from pygame.locals import *


class Pathfinder:
    class AStarState(Enum):
        CONTINUE = 1
        NO_PATH = 2
        
    class Mode(Enum):
        MANUAL = 1
        AUTO = 2
        
    FPS = 60

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
    
    @staticmethod
    def __mouse_button_string__(mouse_button):
        return 'button{}'.format(mouse_button)
    
    def __init__(self, main_args, displaysurf, width, height):
        self.surf = displaysurf
        self.fps = pygame.time.Clock()
        self.w = width
        self.h = height
        self.main_args = main_args
        self.maze = Maze(width, height)
        self.points = []
        self.pressed_keys = {}
        self.mode = Pathfinder.Mode.AUTO
        self.blitMethod = Maze.gen_surf_box
        self.highlighted_cell = [0, 0]

        seed(randint(0, 1000))
        self.regenerate_maze()
        self.handle_events()
    
    def a_star(self, start, goal):
        openlist = set()
        closedlist = set()

        current = Node(start, None, 0, self.get_distance(start, goal))
        openlist.add(current)

        while openlist:
            openlist = sorted(openlist, key=lambda node: node.fCost, reverse=True)
            current = openlist.pop()
            closedlist.add(current)

            if current.cell.x == goal.x and current.cell.y == goal.y:
                path = []
                while current.parent is not None:
                    if current.cell.state not in (Cell.State.START, Cell.State.END):
                        current.cell.state = Cell.State.PATH

                    path.append(current)
                    current = current.parent

                self.update_display()
                return path

            if current.cell != start:
                current.cell.state = Cell.State.SEARCHED

            for cell in [cell for cell in current.cell.get_neighbors(self.maze.cells) if cell.state == Cell.State.VISITED and cell not in closedlist]:
                gcost = current.gCost + self.get_distance(current.cell, cell)
                hcost = self.get_distance(cell, goal)
                openlist.append(Node(cell, current, gcost, hcost))

            self.update_display()
            
        return None

    def get_random_point(self):
        all_cells = [row for column in self.maze.cells for row in column if row.state == Cell.State.VISITED]
        shuffle(all_cells)
        return all_cells[randint(0, len(all_cells)-1)]

    def generate_random_start_end(self):
        self.reset_start_end()
        self.points = [self.get_random_point(), self.get_random_point()]
        self.points[0].state = Cell.State.START
        self.points[1].state = Cell.State.END
        print("New points generated: Start: {}, {} | End: {}, {}".format(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))

    def reset_start_end(self):
        for p in self.points:
            p.state = Cell.State.VISITED
        
        self.points.clear()
    
    def reset_maze_colors(self, include_start_end=False):
        for y in self.maze.cells:
            for x in y:
                if x != Cell.State.NOT_VISITED and x not in self.points:
                    x.state = Cell.State.VISITED
        
        if include_start_end:
            self.reset_start_end()

    def regenerate_maze(self):
        self.maze.generate(self.main_args['box_dims'], self.main_args['diagonal'])

    def get_cell(self, x, y):
        for array in self.maze.cells:
            for cell in array:
                if cell.x == int((x / self.main_args['box_dims'][0])) \
                        and cell.y == int((y / self.main_args['box_dims'][1])):
                    return cell
                
    def handle_events(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == MOUSEBUTTONDOWN:
                    self.pressed_keys[self.__mouse_button_string__(event.button)] = event
                if event.type == KEYDOWN:
                    self.pressed_keys[event.key] = event

                self.compute_current_highlighted_cell()
                self.handle_mouse_events()
                self.handle_key_events()
                self.pressed_keys.clear()
                self.update_display()

    def handle_key_events(self):
        if K_z in self.pressed_keys:
            self.mode = Pathfinder.Mode.AUTO if self.mode == Pathfinder.Mode.MANUAL else Pathfinder.Mode.MANUAL
            if self.mode == Pathfinder.Mode.AUTO:
                self.regenerate_maze()
            else:
                self.maze.visit_all_cells()

        if K_r in self.pressed_keys:
            Main.main()

        if K_f in self.pressed_keys:
            self.reset_maze_colors()

            if len(self.points) != 2:
                self.generate_random_start_end()
            
            start_time = time()
            self.a_star(self.points[0], self.points[1])
            end_time = time()
            print("Done in {} seconds".format(end_time - start_time))
        
        if K_p in self.pressed_keys:
            self.generate_random_start_end()

        if K_m in self.pressed_keys:
            self.regenerate_maze()

        if K_c in self.pressed_keys:
            self.reset_maze_colors(include_start_end=True)

        if K_x in self.pressed_keys:
            self.reset_maze_colors()

        if K_SPACE in self.pressed_keys:
            self.progress_points(self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1]))

    def handle_mouse_events(self): 
        if self.__mouse_button_string__(1) in self.pressed_keys:
            event = self.pressed_keys[self.__mouse_button_string__(1)]
            self.progress_points(self.get_cell(event.pos[0], event.pos[1]))

    def progress_points(self, cell):
        if len(self.points) == 2:
            self.reset_start_end()
        elif cell.state == Cell.State.VISITED:
                cell.state = Cell.State.START if not self.points else Cell.State.END
                self.points.append(cell)

    def compute_current_highlighted_cell(self):
        if K_d in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell[0] += self.main_args['box_dims'][0]
        elif K_s in self.pressed_keys or K_DOWN in self.pressed_keys:
            self.highlighted_cell[1] += self.main_args['box_dims'][1]
        elif K_a in self.pressed_keys or K_LEFT in self.pressed_keys:
            self.highlighted_cell[0] -= self.main_args['box_dims'][0]
        elif K_w in self.pressed_keys or K_RIGHT in self.pressed_keys:
            self.highlighted_cell[1] -= self.main_args['box_dims'][1]

        self.highlighted_cell = self.clamp(self.highlighted_cell[0],
                                            self.highlighted_cell[1], self.w - self.main_args['box_dims'][0],
                                            self.h - self.main_args['box_dims'][1], 0, 0)
        
        if K_v in self.pressed_keys and self.mode == Pathfinder.Mode.MANUAL:
            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.state = Cell.State.NOT_VISITED
            hcell.color = (0, 0, 0)

        if self.__mouse_button_string__(3) in self.pressed_keys and self.mode == Pathfinder.Mode.MANUAL:
            hcell = self.get_cell(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            hcell.state = Cell.State.NOT_VISITED
            hcell.color = (0, 0, 0)

        if K_b in self.pressed_keys and self.mode == Pathfinder.Mode.MANUAL:
            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.state = Cell.State.VISITED
            hcell.color = (255, 255, 255)

        pygame.draw.rect(self.surf, (0, 255, 0),
                            (self.highlighted_cell[0], self.highlighted_cell[1], self.main_args['box_dims'][0], self.main_args['box_dims'][1]))
        
    def update_display(self):
        self.surf.blit(self.blitMethod(self.maze.cells, self.w, self.h), (0, 0))
        pygame.display.update()
        self.fps.tick(self.FPS)

class Node:
    def __init__(self, cell, parent, gcost, hcost):
        self.cell = cell
        self.parent = parent

        self.gCost = gcost
        self.hCost = hcost
        self.fCost = gcost + hcost
