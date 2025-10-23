#!/usr/bin/env python
"""
Detailed performance profiling to identify rendering bottlenecks.
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame
from display import Director
from models import Dimensions
import logging
from log import ColorfulStreamHandler
import cProfile
import pstats
from io import StringIO


class RenderingProfiler:
    def __init__(self):
        self.tick_count = 0
        self.render_time = 0
        self.event_time = 0
        self.blit_time = 0
        self.present_time = 0
        self.draw_time = 0

    def reset(self):
        self.tick_count = 0
        self.render_time = 0
        self.event_time = 0
        self.blit_time = 0
        self.present_time = 0
        self.draw_time = 0


def profile_pathfinding_detailed():
    """Profile pathfinding with detailed timing breakdown."""
    logging.basicConfig(level=logging.WARNING)  # Reduce logging noise

    pygame.init()
    pygame.display.set_caption("PyStar Bottleneck Analysis")

    director = Director()
    director.bootstrap_for_test(
        window_dimensions=Dimensions(300, 300),
        cell_dimensions=Dimensions(10, 10),
        diagonals=True
    )

    profiler = RenderingProfiler()

    # Monkey-patch the update_display to measure components
    original_update = director._update_display

    def profiled_update():
        profiler.tick_count += 1

        start = time.perf_counter()

        # Original highlighting logic
        if director._input_handler.drawing_mode:
            current_pos = director._input_handler.cursor_position
            last_pos = director._input_handler.last_cursor_position

            if last_pos != current_pos:
                # Highlight new cell
                cell_to_highlight = director._maze.get_cell(current_pos.x, current_pos.y)
                if cell_to_highlight:
                    cell_to_highlight.highlight()

                # Unhighlight previous cell
                if last_pos:
                    cell_to_unhighlight = director._maze.get_cell(last_pos.x, last_pos.y)
                    if cell_to_unhighlight:
                        cell_to_unhighlight.unhighlight()

                director._input_handler.last_cursor_position = current_pos.copy()

        # Measure draw_surf time
        draw_start = time.perf_counter()
        render_batch = director._maze.draw_surf(
            director._screen.window_dimensions.width,
            director._screen.window_dimensions.height
        )
        profiler.draw_time += time.perf_counter() - draw_start

        if render_batch:
            # Measure blit time
            blit_start = time.perf_counter()
            for rect in render_batch.rects:
                director._screen.surf.blit(render_batch.surface, rect, rect)
            profiler.blit_time += time.perf_counter() - blit_start

            # Measure display update time
            present_start = time.perf_counter()
            pygame.display.update(render_batch.rects)
            profiler.present_time += time.perf_counter() - present_start

        # Measure fps tick
        director._fps.tick(director.FPS)

        profiler.render_time += time.perf_counter() - start

    director._update_display = profiled_update

    print("\n" + "="*60)
    print("DETAILED BOTTLENECK ANALYSIS")
    print("="*60 + "\n")

    # Test 1: Single pathfinding run with tick function
    director._generate_random_start_end()
    director._reset_maze_colors()

    def tick_with_render():
        event_start = time.perf_counter()
        pygame.event.pump()
        profiler.event_time += time.perf_counter() - event_start
        director._update_display()

    print("Running pathfinding WITH rendering...")
    profiler.reset()

    start = time.perf_counter()
    from a_star import PathFinder
    path = PathFinder.find_path(director._path_endpoints, tick_with_render)
    total_with_render = time.perf_counter() - start

    print(f"\nWith Rendering:")
    print(f"  Total time: {total_with_render:.3f}s")
    print(f"  Tick calls: {profiler.tick_count}")
    print(f"  Time per tick: {(total_with_render/profiler.tick_count*1000):.2f}ms")
    print(f"\n  Time breakdown:")
    print(f"    Event pumping: {profiler.event_time:.3f}s ({profiler.event_time/total_with_render*100:.1f}%)")
    print(f"    Drawing surface: {profiler.draw_time:.3f}s ({profiler.draw_time/total_with_render*100:.1f}%)")
    print(f"    Blitting: {profiler.blit_time:.3f}s ({profiler.blit_time/total_with_render*100:.1f}%)")
    print(f"    Display update: {profiler.present_time:.3f}s ({profiler.present_time/total_with_render*100:.1f}%)")
    print(f"    Other render: {(profiler.render_time-profiler.draw_time-profiler.blit_time-profiler.present_time):.3f}s")

    # Test 2: Without any rendering
    director._reset_maze_colors()
    director._generate_random_start_end()

    def tick_no_render():
        pygame.event.pump()

    print("\n" + "-"*40)
    print("Running pathfinding WITHOUT rendering...")

    start = time.perf_counter()
    path2 = PathFinder.find_path(director._path_endpoints, tick_no_render)
    total_no_render = time.perf_counter() - start

    print(f"\nWithout Rendering:")
    print(f"  Total time: {total_no_render:.3f}s")
    print(f"  Speedup: {total_with_render/total_no_render:.1f}x")

    # Test 3: Profile the maze drawing specifically
    print("\n" + "-"*40)
    print("Profiling draw_surf method specifically...")

    # Force a full redraw
    director._maze._needs_write = True
    for col in director._maze._cells:
        for cell in col:
            director._maze._changed_cells.add(cell)

    pr = cProfile.Profile()
    pr.enable()

    for _ in range(100):
        director._maze.draw_surf(
            director._screen.window_dimensions.width,
            director._screen.window_dimensions.height
        )

    pr.disable()

    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(15)

    print("\nTop 15 functions by cumulative time (100 draw_surf calls):")
    print(s.getvalue())

    pygame.quit()


if __name__ == "__main__":
    profile_pathfinding_detailed()
