"""Video reader implementations."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from trdrop.interfaces.video import VideoReader
from trdrop.profiling import get_profiler


class PyAVReader(VideoReader):
    """Video reader using PyAV (libav/ffmpeg bindings)."""

    def __init__(self, path: str | Path) -> None:
        import av

        self._path = Path(path)
        self._container: Any = av.open(str(path))
        self._stream: Any = self._container.streams.video[0]
        self._stream.thread_type = "AUTO"

        self._fps = float(self._stream.average_rate or self._stream.base_rate or 30)
        self._width: int = self._stream.width
        self._height: int = self._stream.height
        self._total_frames: int = self._stream.frames or self._estimate_frames()

        self._frame_iter: Iterator[Any] | None = None
        self._filter_graph: Any | None = None
        self._current_frame = -1

    def _estimate_frames(self) -> int:
        """Estimate frame count from duration if not available."""
        if self._stream.duration:
            time_base = float(self._stream.time_base)
            duration_sec = self._stream.duration * time_base
            return int(duration_sec * self._fps)
        return 0

    @property
    def path(self) -> Path:
        return self._path

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def total_frames(self) -> int:
        return self._total_frames

    def read(self, out: np.ndarray) -> bool:
        """Read next frame into buffer."""
        if out.shape != self.frame_shape or out.dtype != np.uint8:
            raise ValueError(
                f"Buffer must be {self.frame_shape} uint8, got {out.shape} {out.dtype}"
            )

        if self._frame_iter is None:
            self._frame_iter = self._container.decode(video=0)
            self._filter_graph = None

            # Detect HDR via color transfer characteristic (integer enum from FFmpeg)
            # AVCOL_TRC_SMPTE2084 (PQ) = 16, AVCOL_TRC_ARIB_STD_B67 (HLG) = 18
            _TRC_PQ = 16
            _TRC_HLG = 18
            trc_val = getattr(self._stream.codec_context, "color_trc", None)
            pix_fmt = getattr(self._stream.codec_context, "pix_fmt", "") or ""
            is_hdr = trc_val in (_TRC_PQ, _TRC_HLG) or "10le" in pix_fmt or "12le" in pix_fmt

            if is_hdr:
                try:
                    import av.filter
                    self._filter_graph = av.filter.Graph()
                    src = self._filter_graph.add_buffer(template=self._stream)

                    # Step 1: Convert to float planar format for tonemap processing
                    fmt_in = self._filter_graph.add("format", "pix_fmts=gbrpf32le")
                    src.link_to(fmt_in)

                    # Step 2: Linearize PQ/HLG transfer curve to linear light
                    # colorspace converts BT.2020 primaries + PQ/HLG transfer to linear light + BT.709 primaries
                    cs_linear = self._filter_graph.add(
                        "colorspace",
                        "all=bt709:trc=linear:iall=bt2020:itrc=smpte2084"
                        if trc_val == _TRC_PQ else
                        "all=bt709:trc=linear:iall=bt2020:itrc=arib-std-b67"
                    )
                    fmt_in.link_to(cs_linear)

                    # Step 3: Tonemap from linear HDR luminance to SDR range
                    tm = self._filter_graph.add("tonemap", "tonemap=hable:desat=0")
                    cs_linear.link_to(tm)

                    # Step 4: Apply BT.709 gamma curve
                    cs_out = self._filter_graph.add("colorspace", "all=bt709:trc=bt709:iall=bt709:itrc=linear")
                    tm.link_to(cs_out)

                    # Step 5: Convert back to standard pixel format
                    fmt_out = self._filter_graph.add("format", "pix_fmts=yuv420p")
                    cs_out.link_to(fmt_out)

                    sink = self._filter_graph.add("buffersink")
                    fmt_out.link_to(sink)
                    self._filter_graph.configure()
                    print(f"HDR detected (trc={trc_val}, pix_fmt={pix_fmt}). Tonemapping to SDR enabled.")
                except Exception as e:
                    print(f"Warning: HDR tonemap filter setup failed ({e}), falling back to basic decode.")
                    self._filter_graph = None

        assert self._frame_iter is not None
        profiler = get_profiler()
        try:
            # Time the decode operation
            t0 = time.perf_counter()
            frame = next(self._frame_iter)
            
            if self._filter_graph is not None:
                self._filter_graph.push(frame)
                frame = self._filter_graph.pull()

            self._current_frame += 1
            # Copy frame data to output buffer
            arr = frame.to_ndarray(format="rgb24")
            np.copyto(out, arr)
            t1 = time.perf_counter()
            profiler.add_timing("read_decode", (t1 - t0) * 1000)
            return True
        except StopIteration:
            return False

    def seek(self, frame_index: int) -> None:
        """Seek to specific frame."""
        if frame_index < 0:
            frame_index = 0

        time_base = float(self._stream.time_base)
        target_ts = int(frame_index / self._fps / time_base)

        self._container.seek(target_ts, stream=self._stream)
        self._frame_iter = None
        self._filter_graph = None
        self._current_frame = frame_index - 1

    def close(self) -> None:
        """Close the video file."""
        self._container.close()
