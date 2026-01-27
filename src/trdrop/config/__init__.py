"""Configuration system for TRDrop.

This module provides:
- Type-safe configuration with explicit reference frames
- YAML serialization/deserialization
- Observable store for GUI reactivity
- Coordinate translation utilities

Example usage:

    from trdrop.config import (
        PresetConfig,
        Position,
        GlobalRef,
        VideoRef,
        ConfigStore,
        save_preset,
        load_preset,
    )

    # Create a config
    config = PresetConfig()
    config.rendering.fps_plot.visible = True
    config.videos[0].fps_text.position = Position(0.1, 0.1, VideoRef(0))

    # Save to YAML
    save_preset(config, "my_preset.yaml")

    # Load from YAML
    loaded = load_preset("my_preset.yaml")

    # Use config store for GUI reactivity
    store = ConfigStore(config)

    def on_change(cfg: PresetConfig) -> None:
        print("Config changed!")

    store.subscribe(on_change)

    # Modify via lambda
    store.modify(lambda c: setattr(c.rendering.fps_plot, 'visible', False))

    # Or via context manager
    with store.edit() as cfg:
        cfg.rendering.fps_plot.visible = True
"""

from trdrop.config.coordinates import CoordinateSystem, ViewportState
from trdrop.config.layout import compute_layout
from trdrop.config.observable import ConfigStore
from trdrop.config.serialization import (
    load_preset,
    preset_from_yaml,
    preset_to_yaml,
    save_preset,
)
from trdrop.config.types import (
    Anchor,
    ExportConfig,
    FpsPlotConfig,
    FpsTextConfig,
    FrameLayout,
    FrametimePlotConfig,
    FrametimeTextConfig,
    GlobalRef,
    LayoutConfig,
    LayoutMode,
    PlotStyle,
    Position,
    PresetConfig,
    ProcessingConfig,
    Reference,
    RenderingConfig,
    Size,
    VideoCodec,
    VideoOverlayConfig,
    VideoRef,
    VideoRegion,
)

__all__ = [
    # Reference types
    "GlobalRef",
    "VideoRef",
    "Reference",
    # Position and Size
    "Position",
    "Size",
    "Anchor",
    # Layout types
    "VideoRegion",
    "FrameLayout",
    "LayoutMode",
    "LayoutConfig",
    "compute_layout",
    # Overlay configs
    "FpsTextConfig",
    "FrametimeTextConfig",
    "FpsPlotConfig",
    "FrametimePlotConfig",
    "PlotStyle",
    "VideoOverlayConfig",
    # Main configs
    "ProcessingConfig",
    "RenderingConfig",
    "ExportConfig",
    "VideoCodec",
    "PresetConfig",
    # Serialization
    "preset_to_yaml",
    "preset_from_yaml",
    "save_preset",
    "load_preset",
    # Observable store
    "ConfigStore",
    # Coordinates
    "ViewportState",
    "CoordinateSystem",
]
