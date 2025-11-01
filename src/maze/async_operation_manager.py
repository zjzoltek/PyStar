"""
Base class for asynchronous operations that run algorithms in separate threads.
Provides common infrastructure for thread management, queue-based updates, and cancellation.
"""

import threading
import queue
from typing import Optional, Callable, Generic, TypeVar
from abc import ABC

# Type variable for the update type each implementation will use
UpdateType = TypeVar('UpdateType')


class AsyncOperationManager(Generic[UpdateType], ABC):
    """
    Abstract base class for running operations asynchronously with queue-based updates.

    This class provides the common infrastructure for:
    - Thread management and lifecycle
    - Queue-based communication between threads
    - Cancellation support
    - Update processing with batching

    Subclasses need to implement the _run_operation method with their specific algorithm.
    """

    def __init__(self):
        self._update_queue: queue.Queue[UpdateType] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._cancel_requested = False

    def start_async(
        self,
        target_method: Callable,
        args: tuple,
        name: str = "AsyncOperation"
    ) -> None:
        """
        Start the operation in a background thread.

        Args:
            target_method: The method to run in the background thread
            args: Arguments to pass to the target method
            name: Name for the thread (for debugging)
        """
        if self._thread and self._thread.is_alive():
            return  # Already running

        self._running = True
        self._cancel_requested = False
        self._thread = threading.Thread(
            target=target_method,
            args=args,
            daemon=True,
            name=name
        )
        self._thread.start()

    def process_updates(self, batch_size: int = 10) -> list[UpdateType]:
        """
        Process pending updates from the operation thread.

        Args:
            batch_size: Maximum number of updates to process

        Returns:
            List of updates to apply
        """
        updates = []
        try:
            for _ in range(batch_size):
                update = self._update_queue.get_nowait()
                updates.append(update)
        except queue.Empty:
            pass

        return updates

    def cancel(self) -> None:
        """Request cancellation of the operation."""
        self._cancel_requested = True
        self._running = False

    def stop(self) -> None:
        """Stop the operation thread and wait for it to finish."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    @property
    def is_running(self) -> bool:
        """Check if the operation is currently running."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def has_updates(self) -> bool:
        """Check if there are pending updates to process."""
        return not self._update_queue.empty()

    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self._cancel_requested

    def _queue_update(self, update: UpdateType) -> None:
        """
        Queue an update to be processed by the main thread.

        Args:
            update: The update to queue
        """
        self._update_queue.put(update)

    def _should_continue(self) -> bool:
        """
        Check if the operation should continue running.

        Returns:
            True if the operation should continue, False if it should stop
        """
        return self._running and not self._cancel_requested