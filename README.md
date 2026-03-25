# TRDrop v2

Video framerate, frametime, and screen tearing analysis tool for capture card footage.

Supports up to 4 videos side-by-side comparison. Automatically detects HDR (PQ/HLG) content and tonemaps to SDR for correct output.

## Setup

```bash
uv sync              # runtime only
uv sync --all-extras # with dev tools
```

## Run

```bash
uv run trdrop
```

## Usage

### Quick Start

1. Launch the app, you will see an empty window with a control bar at the top
2. Click **"+"** or drag video files into the window (up to 4 videos)
3. *(Optional)* Click **"Video..."** to set the output video path, click **"CSV..."** to set the metrics export path
4. Click **"Start"** to begin processing
5. Wait for the progress bar to reach 100%, or click **"Pause"** to inspect individual frames

### Control Bar

From left to right:

| Control | Description |
|---------|-------------|
| State Indicator | Colored circle showing engine state (gray=idle, blue=ready, green=processing, orange=paused, purple=complete, red=error) |
| **"+"** | Add video files (MP4, MKV, AVI, MOV, WebM). Supports multiple selection. Max 4 videos |
| **"-"** | Remove the last loaded video |
| Video Count | Shows number of loaded videos (0-4) |
| **"CSV..."** | Set CSV export path. Exports frame-by-frame metrics (fps, frametime, duplicate detection per frame) |
| **"Video..."** | Set video export path. Exports composited video with overlays as MP4 |
| **"Config..."** | Load or save a YAML preset file for overlay configuration (see [Preset Configuration](#preset-configuration)) |
| **"Profile"** | Enable performance profiling. Generates `trdrop_profile.csv` and summary on completion |
| **"Start"** | Begin processing (enabled when videos are loaded) |
| **"Pause"** / **"Resume"** | Pause or resume processing |
| **"Reset"** | Clear everything and return to idle state |
| Seek Spinbox + **"Seek"** | Jump to a specific frame (enabled when paused or completed) |

### Menu Bar

- **File > Add Video...** (Ctrl+O / Cmd+O) — Same as "+" button
- **File > Quit** (Ctrl+Q / Cmd+Q) — Exit the application
- **Help > About** — Version info

### Drag and Drop

Drag video files directly into the window to load them. Supported formats: MP4, MKV, AVI, MOV, WebM.

### Workflow

1. **Load videos** — Use "+" button, menu, or drag-and-drop
2. **Configure exports** — Set CSV and/or video output paths (optional, but at least one is needed for output)
3. **Load preset** — Click "Config..." to load a YAML preset for overlay style customization (optional)
4. **Start processing** — The preview area shows composited frames in real-time with FPS overlay
5. **Inspect frames** — Pause processing, enter a frame number, and click "Seek" to view that frame's metrics
6. **View results** — After completion, check the exported video and/or CSV file

### Outputs

- **Video (.mp4)** — Composited video with all loaded videos arranged in a grid, FPS/frametime text overlays, and optional FPS plot
- **CSV (.csv)** — One row per frame per video, columns include: frame_index, is_duplicate, diff_ratio, windowed_fps, smoothed_fps, frametime_ms, etc.

## Preset Configuration

TRDrop uses YAML preset files to control overlay appearance. Click **"Config..."** in the control bar:

- **"Yes"** — Load an existing YAML preset
- **"No"** — Save the default preset as a template to edit

See `trdrop_preset.example.yaml` for a fully commented example with all available parameters.

### Key Concepts

- **Coordinates** are normalized 0.0–1.0 (0.5 = center of the frame)
- **Reference** can be `global` (relative to entire output frame) or `video:N` (relative to video N's region)
- **Colors** are RGBA arrays `[R, G, B, A]` with values 0–255

## HDR Support

TRDrop automatically detects HDR video content (PQ/HLG transfer curves, BT.2020 color primaries) and applies tonemapping to SDR for correct display and export. This includes:

- PQ EOTF (Perceptual Quantizer) decoding
- BT.2020 to BT.709 color gamut mapping
- Reinhard tonemapping
- BT.709 gamma encoding

No configuration needed — HDR detection and conversion happen automatically.

## Lint & Test

```bash
make check  # run all
make lint   # isort, flake8, basedpyright
make test   # pytest
```
