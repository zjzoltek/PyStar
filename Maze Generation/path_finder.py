import heapq
import sys
from enum import Enum
from math import sqrt
from random import randint, seed, shuffle
from time import time

import pygame
from maze.cell import Cell
from maze.depth_first import Maze
from pygame.locals import *


class Path_Finder:
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
        self.mode = self.Mode.AUTO
        self.blitMethod = Maze.gen_surf_box
        self.highlighted_cell = [0, 0]

        seed(randint(0, 1000))
        self.regenerate_maze()
        self.handle_events()
    
    def a_star(self, start: Cell, goal: Cell) -> None:
        openlist = []
        closedlist = set()
        time_outside_astar = 0
        current = Node(start, None, 0, self.get_distance(start, goal))
        heapq.heappush(openlist, current)

        while openlist:
            current = heapq.heappop(openlist)
            closedlist.add(current.cell)
            
            if current.cell.x == goal.x and current.cell.y == goal.y:
                print(f'Time outside a-star: {time_outside_astar}')
                path = []
                while current.parent is not None:
                    if not current.cell.is_terminator():
                        current.cell.mark_as_route()

                    path.append(current)
                    current = current.parent
                return path

            if not current.cell.is_terminator():
                current.cell.mark_as_searched()

            for cell in current.cell.neighbors:
                if not cell.is_transversible() or cell in closedlist:
                    continue
                    
                gcost = current.gCost + self.get_distance(current.cell, cell)
                hcost = self.get_distance(cell, goal)
                n = Node(cell, current, gcost, hcost)
                heapq.heappush(openlist, n)

            a = time()
            pygame.event.pump()
            self.update_display()
            b = time()
            time_outside_astar += b - a
        return None

    def get_random_point(self):
        all_cells = [row for column in self.maze.cells for row in column if row.is_transversible()]
        shuffle(all_cells)
        return all_cells[randint(0, len(all_cells)-1)]

    def generate_random_start_end(self):
        self.reset_start_end()
        self.points = [self.get_random_point(), self.get_random_point()]
        self.points[0].mark_as_start()
        self.points[1].mark_as_end()
        print("New points generated: Start: {}, {} | End: {}, {}".format(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y))

    def reset_start_end(self):
        for p in self.points:
            p.mark_as_open()
        
        self.points.clear()
    
    def reset_maze_colors(self, include_start_end=False):
        for column in self.maze.cells:
            for cell in column:
                if cell.is_openable():
                    cell.mark_as_open()
        
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
            self.mode = self.Mode.AUTO if self.mode == self.Mode.MANUAL else self.Mode.MANUAL
            if self.mode == self.Mode.AUTO:
                self.regenerate_maze()
            else:
                self.maze.clear()

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
        elif cell.is_transversible() and not cell.is_terminator():
            if not self.points:
                cell.mark_as_start()
            else:
                cell.mark_as_end()
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
        
        if K_v in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.mark_as_wall()
            hcell.color = (0, 0, 0)

        if self.__mouse_button_string__(3) in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.get_cell(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            hcell.mark_as_wall()
            hcell.color = (0, 0, 0)

        if K_b in self.pressed_keys and self.mode == self.Mode.MANUAL:
            hcell = self.get_cell(self.highlighted_cell[0], self.highlighted_cell[1])
            hcell.state.mark_as_open()
            hcell.color = (255, 255, 255)

        pygame.draw.rect(self.surf, (0, 255, 0),
                            (self.highlighted_cell[0] *  self.main_args['box_dims'][0], \
                                self.highlighted_cell[1] *  self.main_args['box_dims'][1], \
                                    self.main_args['box_dims'][0], self.main_args['box_dims'][1]))
        
    def update_display(self):
        self.surf.blit(self.blitMethod(self.maze.cells, self.w, self.h), (0, 0))
        pygame.display.flip()
        self.fps.tick(self.FPS)

class Node:
    def __init__(self, cell, parent, gcost, hcost):
        self.cell = cell
        self.parent = parent

        self.gCost = gcost
        self.hCost = hcost
        self.fCost = gcost + hcost
    
    def __repr__(self):
        return repr(self.cell)
    
    def __lt__(self, other):
        return self.fCost < other.fCost
    
    def __gt__(self, other):
        return self.fCost > other.fCost
    
    def __le__(self, other):
        return self.fCost <= other.fCost
    
    def __ge__(self, other):
        return self.fCost >= other.fCost
    
    def __eq__(self, other):
        return self.fCost == other.fCost
    
    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return hash(self.__repr__())
