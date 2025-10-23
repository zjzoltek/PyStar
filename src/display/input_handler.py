from typing import Dict, Optional
from pygame.event import Event
from pygame.locals import *
import models


class InputHandler:
    """Handles keyboard and mouse input events."""

    LEFT_CLICK = 1
    RIGHT_CLICK = 3

    def __init__(self):
        self._pressed_keys: Dict[int, Event] = {}
        self._drawing_mode: bool = False
        self._cursor_position: models.Point = models.Point(0, 0)
        self._last_cursor_position: Optional[models.Point] = None

    def process_event(self, event: Event) -> None:
        """Process a single pygame event."""
        if event.type == MOUSEBUTTONDOWN:
            self._pressed_keys[event.button] = event
        elif event.type == KEYDOWN:
            self._pressed_keys[event.key] = event

    def clear_pressed_keys(self) -> None:
        """Clear the pressed keys buffer."""
        self._pressed_keys.clear()

    def is_key_pressed(self, key: int) -> bool:
        """Check if a specific key was pressed."""
        return key in self._pressed_keys

    def get_mouse_event(self, button: int) -> Optional[Event]:
        """Get mouse event for a specific button."""
        return self._pressed_keys.get(button)

    @property
    def drawing_mode(self) -> bool:
        return self._drawing_mode

    @drawing_mode.setter
    def drawing_mode(self, value: bool) -> None:
        self._drawing_mode = value

    @property
    def cursor_position(self) -> models.Point:
        return self._cursor_position

    @cursor_position.setter
    def cursor_position(self, value: models.Point) -> None:
        self._cursor_position = value

    @property
    def last_cursor_position(self) -> Optional[models.Point]:
        return self._last_cursor_position

    @last_cursor_position.setter
    def last_cursor_position(self, value: Optional[models.Point]) -> None:
        self._last_cursor_position = value

    def update_cursor_position(self, delta_x: int, delta_y: int, max_point: models.Point, min_point: models.Point) -> models.Point:
        """Update cursor position with bounds checking."""
        new_x = self._cursor_position.x + delta_x
        new_y = self._cursor_position.y + delta_y

        # Clamp to bounds
        new_x = max(min_point.x, min(new_x, max_point.x))
        new_y = max(min_point.y, min(new_y, max_point.y))

        self._cursor_position = models.Point(new_x, new_y)
        return self._cursor_position