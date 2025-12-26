
import unittest
import sys
import os
import array
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from maze.fast_maze_generator import FastMazeGenerator, WALL, OPEN

class TestFastMazeGenerator(unittest.TestCase):
    def test_small_maze_generation(self):
        width, height = 10, 10
        gen = FastMazeGenerator.generate(width, height)

        grid = None
        for item in gen:
            if not isinstance(item, int):
                grid = item

        self.assertIsNotNone(grid)
        self.assertEqual(len(grid), width * height)

        # Check that we have walls and open spaces
        self.assertTrue(OPEN in grid)
        self.assertTrue(WALL in grid)

        # Check start point (0,0) is open
        self.assertEqual(grid[0], OPEN)

    def test_connectivity(self):
        # A valid maze should have all OPEN cells connected.
        width, height = 20, 20
        gen = FastMazeGenerator.generate(width, height)

        grid = None
        for item in gen:
            if not isinstance(item, int):
                grid = item

        # Perform BFS to check connectivity of OPEN cells
        start_idx = 0
        if grid[start_idx] != OPEN:
            self.fail("Start point is not open")

        queue = [start_idx]
        visited = {start_idx}
        count = 0

        total_open = grid.count(OPEN)

        while queue:
            curr = queue.pop(0)
            count += 1
            cx, cy = curr % width, curr // width

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    n_idx = ny * width + nx
                    if grid[n_idx] == OPEN and n_idx not in visited:
                        visited.add(n_idx)
                        queue.append(n_idx)

        self.assertEqual(count, total_open, "Not all open cells are connected!")

if __name__ == '__main__':
    unittest.main()
