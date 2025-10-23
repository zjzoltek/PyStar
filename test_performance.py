#!/usr/bin/env python
"""
Performance test script for PyStar A* visualization.
Tests both the refactored code and rendering performance.
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


def test_pathfinding_performance(iterations: int = 10, use_visualization: bool = True):
    """Test pathfinding performance with incremental rendering."""
    logging.basicConfig(level=logging.INFO, handlers=[ColorfulStreamHandler(sys.stdout)])

    pygame.init()
    pygame.display.set_caption("PyStar Performance Test")

    director = Director()
    director.bootstrap_for_test(window_dimensions=Dimensions(300, 300), cell_dimensions=Dimensions(10, 10), diagonals=True)

    print(f"\n{'='*50}")
    print(f"PERFORMANCE TEST RESULTS ({'WITH' if use_visualization else 'WITHOUT'} VISUALIZATION)")
    print(f"{'='*50}\n")

    # Test pathfinding with visualization
    total_time = 0
    for i in range(iterations):
        # Generate random endpoints
        director._generate_random_start_end()

        # Time the pathfinding with visualization
        start_time = time.perf_counter()

        # Run pathfinding with tick function for visualization
        def tick():
            pygame.event.pump()
            if use_visualization:
                director._update_display()

        director._reset_maze_colors()
        from a_star import PathFinder
        path = PathFinder.find_path(director._path_endpoints, tick)

        elapsed = time.perf_counter() - start_time
        total_time += elapsed

        print(f"Iteration {i+1}: {elapsed:.3f}s - Path length: {len(path) if path else 0}")

        # Clear for next iteration
        director._reset_maze_colors(include_start_end=True)

    avg_time = total_time / iterations
    print(f"\n{'='*50}")
    print(f"Average pathfinding time with visualization: {avg_time:.3f}s")
    print(f"Total time for {iterations} iterations: {total_time:.3f}s")
    print(f"{'='*50}\n")

    pygame.quit()


def test_refactored_models():
    """Test that the refactored models work correctly."""
    print("\n" + "="*50)
    print("TESTING REFACTORED MODELS")
    print("="*50)

    # Test PathEndpoints (formerly StartEnd)
    from models import PathEndpoints, Cell, Dimensions
    from enums import State

    class MockMaze:
        def on_cell_state_change(self, cell=None):
            pass

    maze = MockMaze()
    dim = Dimensions(10, 10)

    # Create test cells
    cell1 = Cell(0, 0, dim, maze)
    cell2 = Cell(1, 1, dim, maze)
    cell3 = Cell(2, 2, dim, maze)

    # Test PathEndpoints
    endpoints = PathEndpoints()

    assert endpoints.is_empty(), "Should start empty"
    assert not endpoints.is_complete(), "Should not be complete when empty"

    # Select first cell
    endpoints.select_cell(cell1)
    assert endpoints.start == cell1, "First cell should be start"
    assert not endpoints.is_complete(), "Should not be complete with only start"

    # Select second cell
    endpoints.select_cell(cell2)
    assert endpoints.end == cell2, "Second cell should be end"
    assert endpoints.is_complete(), "Should be complete with both endpoints"

    # Select third cell (should reset)
    endpoints.select_cell(cell3)
    assert endpoints.start == cell3, "Should reset and set new start"
    assert endpoints.end is None, "End should be None after reset"

    print("[PASS] PathEndpoints class working correctly")
    print("[PASS] Cell selection logic working correctly")
    print("[PASS] State management working correctly")
    print("\nAll refactored models passed tests!\n")


if __name__ == "__main__":
    # First test the refactored models
    test_refactored_models()

    # Then test performance
    print("\nStarting performance test...")
    print("Press Ctrl+C to stop early\n")

    try:
        test_pathfinding_performance(iterations=5, use_visualization=True)
        test_pathfinding_performance(iterations=5, use_visualization=False)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        pygame.quit()