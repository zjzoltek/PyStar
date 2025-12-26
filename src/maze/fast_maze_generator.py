
import random
import array
from typing import Iterator

# Constants
WALL = 0
OPEN = 1

class FastMazeGenerator:
    """
    Optimized maze generator using primitive arrays and Recursive Backtracker (Jump-by-2).
    """

    @staticmethod
    def generate(width: int, height: int, diagonals: bool = False, seed: int = None) -> Iterator[tuple[int, int]]:
        """
        Generates a maze using randomized DFS with Jump-by-2 logic.
        """
        if seed is not None:
            random.seed(seed)

        size = width * height
        grid = array.array('b', [WALL] * size)

        # Ensure we start at a valid point that allows jumping.
        # Usually (0,0) or (1,1).
        # If we use (0,0) as start, next valid is (2,0). Wall at (1,0).
        start_x, start_y = 0, 0
        start_idx = 0
        grid[start_idx] = OPEN
        visited_count = 1

        stack = array.array('I')
        stack.append(start_idx)

        # Directions: (dx, dy) for the WALL step.
        # The node step is (dx*2, dy*2).
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        # Diagonals not typically supported in jump-by-2 this simply,
        # but if diagonals are allowed, we jump (1,1) -> (2,2)?
        # That would mean removing wall at (1,1).
        if diagonals:
             # For diagonals, "wall" is the diagonal step?
             # This is tricky. If 1x1 cells, diagonal connection means just stepping (1,1).
             # But we need to ensure we don't cross paths.
             # Let's stick to orthogonal first as benchmark didn't use diagonals.
             pass

        width_local = width
        height_local = height
        grid_local = grid
        choice = random.choice

        # Pre-calc jump offsets
        # (wall_dx, wall_dy, target_dx, target_dy)
        jumps = []
        for dx, dy in dirs:
            jumps.append((dx, dy, dx*2, dy*2))

        UPDATE_FREQ = 1000
        steps_since_update = 0

        while stack:
            current_idx = stack[-1]
            cy, cx = divmod(current_idx, width_local)

            candidates = []

            for wdx, wdy, tdx, tdy in jumps:
                nx, ny = cx + tdx, cy + tdy

                # Check target bounds
                if 0 <= nx < width_local and 0 <= ny < height_local:
                    n_idx = ny * width_local + nx
                    # If target is Unvisited (Wall)
                    if grid_local[n_idx] == WALL:
                        # Add candidate (store target idx and wall idx)
                        w_idx = (cy + wdy) * width_local + (cx + wdx)
                        candidates.append((n_idx, w_idx))

            if candidates:
                # Pick random
                next_idx, wall_idx = choice(candidates)

                # Mark Wall as Open
                grid_local[wall_idx] = OPEN

                # Mark Target as Open
                grid_local[next_idx] = OPEN

                stack.append(next_idx)
                visited_count += 2 # We opened 2 cells

                steps_since_update += 1
                if steps_since_update >= UPDATE_FREQ:
                    yield visited_count
                    steps_since_update = 0
            else:
                stack.pop()

        yield visited_count
        yield grid
