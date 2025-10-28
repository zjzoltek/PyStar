# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyStar is a high-performance Python maze generation and pathfinding visualization tool that:

- Generates mazes using randomized depth-first search algorithm
- Finds shortest paths using A* algorithm with heuristic optimization
- Provides multiple visualization modes for different performance/interactivity trade-offs
- Supports both orthogonal and diagonal movement in pathfinding
- Features incremental rendering with dirty rectangle optimization for performance
- Includes comprehensive input validation and error handling systems

## Running the Application

```bash
# Launch interactive visualization (includes all modes)
python src/main.py

# Performance testing and comparison
python test_performance.py
python test_optimized_performance.py
python profile_bottleneck.py  # Detailed profiling
```

## Architecture Overview

PyStar follows a modular, event-driven architecture with clear separation of concerns:

- **Event Orchestration**: Director pattern for coordinating user input, rendering, and algorithm execution
- **Observer Pattern**: Cell state changes trigger rendering updates through ICellStateListener
- **Strategy Pattern**: Multiple visualization modes (synchronous, optimized, async) with runtime switching
- **Command Pattern**: InputHandler processes and dispatches user actions
- **Incremental Rendering**: Dirty rectangle optimization minimizes unnecessary redraws
- **Producer-Consumer**: Async pathfinding uses queues for thread-safe communication

## Architecture Components

### Core Classes

1. **Director** (`src/display/director.py`): Main event orchestrator managing user input, display updates, visualization modes (synchronous, optimized, async), and coordination between components
2. **Maze** (`src/maze/depth_first.py`): Generates mazes using depth-first search with neighbor tracking and state management via observer pattern
3. **PathFinder** (`src/a_star/path_finder.py`): Static class implementing A* search with optional tick callback for visualization
4. **AsyncPathfinder** (`src/display/async_pathfinding.py`): Thread-based pathfinding with queue-based update communication

### Rendering System

- **IncrementalRenderer** (`src/display/incremental_renderer.py`): Core rendering engine with dirty rectangle optimization, cell batching, and surface caching
- **VisualizationRenderer** (`src/display/incremental_renderer.py`): Wrapper for smooth algorithm animation with configurable speed and frame-based updates
- **Screen** (`src/display/screen.py`): Manages pygame surface, window configuration, and interactive setup dialogs
- **InputHandler** (`src/display/input_handler.py`): Centralized keyboard and mouse event processing with drawing mode support

### State Management

- **Cell States** (`enums.State`): WALL, OPEN, SEARCHED, START, END, ROUTE, HIGHLIGHTED with color mappings and behavior methods
- **Color Definitions** (`enums.Color`): RGB color constants for all cell states with RGB type alias
- **PathUpdate** (`enums.PathUpdate`): SEARCHED, COMPLETE, ROUTE for async communication
- **ICellStateListener** (`models.Cell`): Observer protocol interface for cell state change notifications

### Data Models

- **Cell** (`models.Cell`): Individual maze cell with neighbors, state, dimensions, and highlight functionality
- **Node** (`models.Node`): A* algorithm node with parent tracking, f/g/h costs, and heap operations support
- **Point** (`models.Point`): 2D coordinate representation with copy functionality
- **Dimensions** (`models.Dimensions`): Width/height container for consistent sizing
- **PathEndpoints** (`models.PathEndpoints`): Manages start/end point selection with automatic state transitions (replaces former StartEnd)
- **ValueRange** (`models.ValueRange`): Range validation helper with inclusive/exclusive bounds

## Controls

### Navigation
- `f` - Find path (auto-generates endpoints if needed)
- `p` - Generate random start/end points
- `m` - Re-generate maze
- `c` - Clear all colors and endpoints
- `x` - Clear path colors only
- `Space` - Select cell as start/end point
- Left-click - Select cell as start/end point

### Drawing Mode
- `z` - Toggle drawing mode
- WASD/Arrow keys - Move cursor
- `v` - Place wall at cursor
- `b` - Open cell at cursor
- Right-click - Place wall at mouse position

### Visualization Modes
- `1` - Synchronous mode (original, with fps limiting)
- `2` - Optimized mode (fast, no fps limiting)
- `3` - Asynchronous mode (background thread)

## Performance Characteristics

The application supports three visualization modes with different performance profiles:

1. **Synchronous Mode**: Maintains 60 FPS during pathfinding for smooth visualization
2. **Optimized Mode**: ~370x faster by removing frame rate limiting during algorithm execution
3. **Asynchronous Mode**: ~2500x faster by running pathfinding in a separate thread

Typical performance on 300x300 maze (30x30 cells):
- Pure algorithm (no visualization): ~0.5ms
- Optimized visualization: ~9ms
- Asynchronous visualization: ~1ms
- Original synchronous: ~3.5s

## Supporting Systems

### Input Validation Framework
- **Validator** (`src/validation/validator.py`): Composable validation system with chainable conditions
- **Conditions** (`src/validation/`): Type checking, range validation, length validation, and set membership validation
- **Console** (`src/display/console.py`): Interactive command-line interface with integrated validation

### Error Handling
- **Custom Exceptions** (`src/errors/`): Specialized error types for argument validation and type checking
- Includes `ArgOutOfRangeError`, `IncorrectNumberOfArgsError`, `InvalidArgTypeError`, `InvalidArgValueError`

### Logging and Profiling
- **ColorfulStreamHandler** (`src/log/colorful_stream_handler.py`): Custom logging handler with colored output
- **Performance Decorators** (`src/log/decorators.py`): `@timed` decorator for method execution timing
- **Profiling Scripts**: Comprehensive performance analysis tools for bottleneck identification

### Test Infrastructure
- **Performance Testing** (`test_performance.py`): Validates refactored models and measures rendering performance
- **Optimization Comparison** (`test_optimized_performance.py`): Benchmarks all three visualization modes
- **Bottleneck Analysis** (`profile_bottleneck.py`): Detailed profiling with cProfile integration

## Development Notes

- Python 3.12+ with pygame 2.6+
- Uses Python's built-in threading and queue modules for async operations
- Logging via custom ColorfulStreamHandler for colored console output
- Type hints are partially implemented but inconsistent (uses modern syntax like `type` aliases)
- No external dependencies beyond pygame
- No unit tests exist currently (only performance/integration tests)
- Extensive use of dataclasses and protocols for clean architecture
- Observer pattern implementation for cell state change notifications
