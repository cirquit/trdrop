"""Observable configuration store.

Provides a simple modify-and-notify pattern for config changes.
Subscribers receive the current config on any change and decide
what they care about.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Generator

if TYPE_CHECKING:
    from trdrop.config.types import PresetConfig


class ConfigStore:
    """
    Observable config store with modify-and-notify pattern.

    Subscribers are notified after any modification and receive
    the current config. Each subscriber is responsible for tracking
    what it cares about and deciding if action is needed.

    Example:
        store = ConfigStore(PresetConfig())

        # Subscribe to changes
        def on_change(config: PresetConfig) -> None:
            if config.processing != cached_processing:
                invalidate_cache()
            render_preview()

        unsubscribe = store.subscribe(on_change)

        # Modify via lambda
        store.modify(lambda c: setattr(c.rendering.fps_plot, 'visible', False))

        # Modify via context manager
        with store.edit() as config:
            config.rendering.fps_plot.visible = False
            config.videos[0].fps_text.position = new_position

        # Replace entirely (e.g., loading from file)
        store.replace(load_preset("my_preset.yaml"))

        # Unsubscribe when done
        unsubscribe()
    """

    def __init__(self, config: PresetConfig | None = None) -> None:
        """
        Initialize config store.

        Args:
            config: Initial config. If None, creates default PresetConfig.
        """
        # Import here to avoid circular import
        from trdrop.config.types import PresetConfig

        self._config = config if config is not None else PresetConfig()
        self._subscribers: list[Callable[[PresetConfig], None]] = []

    @property
    def config(self) -> PresetConfig:
        """Current config (read-only by convention)."""
        return self._config

    def modify(self, fn: Callable[[PresetConfig], None]) -> None:
        """
        Modify config via function, then notify subscribers.

        Args:
            fn: Function that mutates the config in place.

        Example:
            # Simple single-field change
            store.modify(lambda c: setattr(c.rendering.fps_plot, 'visible', False))

            # Multiple changes
            def update(c):
                c.rendering.fps_plot.visible = False
                c.processing.window_size = 120
            store.modify(update)
        """
        fn(self._config)
        self._notify()

    @contextmanager
    def edit(self) -> Generator[PresetConfig, None, None]:
        """
        Modify config via context manager, then notify subscribers.

        Provides natural Python syntax for modifications. Notification
        happens after the context block completes.

        Example:
            with store.edit() as config:
                config.rendering.fps_plot.visible = False
                config.videos[0].fps_text.position = Position(0.1, 0.1, VideoRef(0))
        """
        yield self._config
        self._notify()

    def replace(self, new_config: PresetConfig) -> None:
        """
        Replace entire config, then notify subscribers.

        Use this when loading a config from file or resetting to defaults.

        Args:
            new_config: The new config to use.
        """
        self._config = new_config
        self._notify()

    def subscribe(
        self, callback: Callable[[PresetConfig], None]
    ) -> Callable[[], None]:
        """
        Subscribe to config changes.

        The callback receives the current config after any modification.
        The subscriber is responsible for comparing against its cached
        state to determine if action is needed.

        Args:
            callback: Function called with current config on changes.

        Returns:
            Unsubscribe function. Call it to remove the subscription.

        Example:
            def on_change(config: PresetConfig) -> None:
                if config.processing != self._cached_processing:
                    self._cached_processing = copy.copy(config.processing)
                    self.invalidate_cache()
                self.render()

            unsubscribe = store.subscribe(on_change)
            # ... later ...
            unsubscribe()
        """
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

        return unsubscribe

    def _notify(self) -> None:
        """Notify all subscribers with current config."""
        for callback in self._subscribers:
            callback(self._config)
