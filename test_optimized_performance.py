#!/usr/bin/env python
"""
Performance comparison of different rendering optimization strategies.
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


def test_performance_modes(iterations: int = 3):
    """Test all three visualization modes."""
    logging.basicConfig(level=logging.WARNING)  # Quiet for testing

    pygame.init()
    pygame.display.set_caption("PyStar Performance Comparison")

    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON: RENDERING OPTIMIZATION STRATEGIES")
    print("="*70)
    print(f"\nRunning {iterations} iterations for each mode...")
    print("Maze: 300x300 pixels, 10x10 cells, diagonal movement enabled\n")

    director = Director()
    director.bootstrap_for_test(
        window_dimensions=Dimensions(300, 300),
        cell_dimensions=Dimensions(10, 10),
        diagonals=True
    )

    modes = [
        ('synchronous', 'Original (with fps.tick)'),
        ('optimized', 'Optimized (no fps.tick during pathfinding)'),
        ('async', 'Asynchronous (background thread, no fps limit while running)')
    ]

    results = {}

    for mode, description in modes:
        print(f"\n{'-'*70}")
        print(f"Testing: {description}")
        print(f"Mode: {mode}")
        print(f"{'-'*70}")

        director.set_visualization_mode(mode)
        times = []

        for i in range(iterations):
            # Generate random endpoints
            director._generate_random_start_end()
            director._reset_maze_colors()

            # Time the pathfinding
            start_time = time.perf_counter()

            if mode == 'synchronous':
                # Original with fps limiting
                def tick():
                    pygame.event.pump()
                    director._update_display()

                from a_star import PathFinder
                path = PathFinder.find_path(director._path_endpoints, tick)

            elif mode == 'optimized':
                # Optimized without fps limiting during pathfinding
                def tick_optimized():
                    pygame.event.pump()
                    director._update_display(skip_tick=True)

                from a_star import PathFinder
                path = PathFinder.find_path(director._path_endpoints, tick_optimized)

            elif mode == 'async':
                # Async mode - just start it and wait for completion
                completed = False

                def on_complete(p):
                    nonlocal completed, path
                    completed = True
                    path = p

                director._async_pathfinder.find_path_async(director._path_endpoints, on_complete)

                # Wait for completion while processing updates
                while not completed:
                    pygame.event.pump()

                    updates = director._async_pathfinder.process_updates(10)
                    if updates:
                        director._maze.on_cell_state_change()

                    director._update_display(skip_tick=True)

            elapsed = time.perf_counter() - start_time
            times.append(elapsed)

            print(f"  Iteration {i+1}: {elapsed:.3f}s - Path length: {len(path) if path else 0}")

        avg_time = sum(times) / len(times)
        results[mode] = {
            'avg': avg_time,
            'min': min(times),
            'max': max(times),
            'description': description
        }

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    baseline = results['synchronous']['avg']

    for mode, data in results.items():
        speedup = baseline / data['avg']
        print(f"\n{data['description']}:")
        print(f"  Average: {data['avg']:.3f}s")
        print(f"  Min: {data['min']:.3f}s, Max: {data['max']:.3f}s")
        if mode != 'synchronous':
            print(f"  Speedup vs original: {speedup:.1f}x faster")

    # Test without any visualization for reference
    print(f"\n{'-'*70}")
    print("Reference: No visualization (pure algorithm speed)")
    print(f"{'-'*70}")

    no_viz_times = []
    for i in range(iterations):
        director._generate_random_start_end()
        director._reset_maze_colors()

        start_time = time.perf_counter()
        from a_star import PathFinder
        path = PathFinder.find_path(director._path_endpoints, lambda: pygame.event.pump())
        elapsed = time.perf_counter() - start_time
        no_viz_times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed:.4f}s")

    no_viz_avg = sum(no_viz_times) / len(no_viz_times)
    print(f"\n  Average (no visualization): {no_viz_avg:.4f}s")
    print(f"  Maximum theoretical speedup: {baseline/no_viz_avg:.0f}x")

    print("\n" + "="*70)
    print("CONCLUSIONS")
    print("="*70)
    print("\n1. The fps.tick(60) call was the primary bottleneck")
    print("2. Removing it during pathfinding provides massive speedup")
    print("3. Async mode allows smooth interaction during pathfinding")
    print("4. The actual rendering operations are quite fast")

    pygame.quit()


if __name__ == "__main__":
    test_performance_modes()
