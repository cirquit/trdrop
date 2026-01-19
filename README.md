# TRDrop v2

Video framerate, frametime, and screen tearing analysis tool for capture card footage.

## Setup

```bash
uv sync              # runtime only
uv sync --all-extras # with dev tools
```

## Lint & Test

```bash
make check  # run all
make lint   # isort, flake8, basedpyright
make test   # pytest
```

## Run

```bash
uv run trdrop
uv run python examples/pyav/01_read_video_info.py <video>
```
