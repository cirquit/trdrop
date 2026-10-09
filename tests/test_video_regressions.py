"""Regression coverage for video timing, color conversion, and seek isolation."""

from __future__ import annotations

import threading
import time
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
import pytest
from av.video.stream import VideoStream
from PyQt6.QtGui import QGuiApplication

from trdrop.compositor.types import AggregatedMetrics, CompositorOutput
from trdrop.config import PresetConfig
from trdrop.engine import EngineState, InteractiveEngine
from trdrop.export.streaming_video import StreamingVideoExporter
from trdrop.video import reader as reader_module
from trdrop.video.reader import PyAVReader, _hdr_to_sdr


@pytest.fixture(scope="module")
def qapp():
    app = QGuiApplication.instance() or QGuiApplication([])
    return app


def _write_video(
    path: Path, count: int = 20, *, transfer: int = 1,
    primaries: int = 1, pix_fmt: str = "yuv420p", codec: str = "libx264",
) -> None:
    with av.open(str(path), "w") as container:
        stream = container.add_stream(codec, rate=30)
        assert isinstance(stream, VideoStream)
        stream.width, stream.height = 128, 96
        stream.pix_fmt = pix_fmt
        stream.codec_context.color_trc = transfer
        stream.codec_context.color_primaries = primaries
        stream.codec_context.colorspace = 1 if primaries == 1 else 9
        if codec == "libx264":
            stream.options = {"crf": "0", "preset": "ultrafast", "g": "12"}
        for index in range(count):
            data = np.full((96, 128, 3), 20 + index * 10, dtype=np.uint8)
            frame = av.VideoFrame.from_ndarray(data, format="rgb24")
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)


def _output(data: np.ndarray, index: int = 0) -> CompositorOutput:
    return CompositorOutput(data, AggregatedMetrics(index, ()))


@pytest.mark.parametrize("source_fps,output_fps,count", [
    (30, 60, 6), (60, 30, 6), (25, 60, 5), (30, 30, 6),
    (30000 / 1001, 60, 30), (60, 24000 / 1001, 60),
])
def test_export_preserves_time_and_frame_selection(tmp_path, source_fps, output_fps, count):
    path = tmp_path / "resampled.mp4"
    exporter = StreamingVideoExporter(
        path, output_fps, source_fps=source_fps,
        codec="libx264", crf=0, preset="ultrafast",
    )
    exporter.open()
    try:
        for index in range(count):
            data = np.full((64, 64, 3), 20 + (index % 10) * 20, dtype=np.uint8)
            exporter.write_frame(_output(data, index))
    finally:
        exporter.close()

    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        frames = list(container.decode(video=0))
        assert stream.duration is not None and stream.time_base is not None
        duration = float(stream.duration * stream.time_base)
        assert duration == pytest.approx(count / source_fps, abs=1 / output_fps)
        for frame in frames:
            assert frame.pts is not None and frame.time_base is not None
            timestamp = float(frame.pts * frame.time_base)
            # Each output timestamp must show the input frame covering that time.
            source_index = min(count - 1, int(timestamp * source_fps + 1e-8))
            actual = frame.to_ndarray(format="rgb24")[32, 32, 0]
            assert int(actual) == pytest.approx(20 + (source_index % 10) * 20, abs=2)
        assert len(frames) == len(np.arange(0, count / source_fps - 1e-9, 1 / output_fps))


def test_export_bt709_tags_match_encoded_pixels(tmp_path):
    path = tmp_path / "color.mp4"
    colors = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
    bars = np.repeat(np.repeat(colors[None, :, :], 64, axis=0), 64, axis=1)
    exporter = StreamingVideoExporter(path, 30, codec="libx264", crf=0, preset="ultrafast")
    exporter.open()
    exporter.write_frame(_output(bars))
    exporter.close()
    with av.open(str(path)) as container:
        frame = next(container.decode(video=0))
        context = container.streams.video[0].codec_context
        assert context.colorspace == context.color_trc == context.color_primaries == 1
        rgb = frame.to_ndarray(format="rgb24", src_colorspace="ITU709")
        np.testing.assert_allclose(rgb[32, [32, 96, 160]], colors, atol=3)


@pytest.mark.parametrize("transfer,primaries,pix_fmt", [
    (1, 1, "yuv420p10le"), (1, 1, "yuv420p12le"),
    (1, 9, "yuv420p10le"), (2, 9, "yuv420p10le"),
])
def test_high_bit_depth_sdr_is_not_tonemapped(tmp_path, monkeypatch, transfer, primaries, pix_fmt):
    path = tmp_path / "sdr.mkv"
    _write_video(path, 1, transfer=transfer, primaries=primaries, pix_fmt=pix_fmt, codec="ffv1")

    def unexpected_lut(*args):
        pytest.fail("SDR must not request an HDR LUT")

    monkeypatch.setattr(reader_module, "_get_tonemap_lut3d", unexpected_lut)
    with av.open(str(path)) as container:
        expected = next(container.decode(video=0)).to_ndarray(format="rgb24")
    reader = PyAVReader(path)
    try:
        out = np.empty(reader.frame_shape, dtype=np.uint8)
        assert reader.read(out)
        np.testing.assert_array_equal(out, expected)
    finally:
        reader.close()


@pytest.mark.parametrize("transfer", [16, 18])
def test_reader_selects_transfer_specific_lut(tmp_path, monkeypatch, transfer):
    path = tmp_path / "hdr.mkv"
    _write_video(path, 1, transfer=transfer, primaries=9, pix_fmt="yuv420p10le", codec="ffv1")
    calls = []
    sentinel = np.empty(0, dtype=np.uint8)

    def get_lut(trc, primaries):
        calls.append((trc, primaries))
        return sentinel

    def apply_lut(img, lut):
        assert lut is sentinel
        return _hdr_to_sdr(img.astype(np.float64) / 255.0, transfer, 9)

    monkeypatch.setattr(reader_module, "_get_tonemap_lut3d", get_lut)
    monkeypatch.setattr(reader_module, "_apply_lut3d", apply_lut)
    reader = PyAVReader(path)
    try:
        assert reader.read(np.empty(reader.frame_shape, dtype=np.uint8))
        assert calls == [(transfer, 9)]
    finally:
        reader.close()


@pytest.mark.parametrize("transfer,midgrey", [(16, 176), (18, 146)])
def test_hdr_reference_greys_and_monotonic_ramp(transfer, midgrey):
    # ST 2084 signal 0.5 is 92.25 nits; HLG signal 0.5 is 50.70 nits
    # on the BT.2100 1000-nit reference display. Their SDR values must differ.
    ramp = np.repeat(np.linspace(0, 1, 257)[:, None], 3, axis=1)
    out = _hdr_to_sdr(ramp, transfer, 9).astype(int)
    assert (out[0] == 0).all()
    assert (out[-1] >= 254).all()
    np.testing.assert_allclose(out[128], midgrey, atol=1)
    assert (np.diff(out, axis=0) >= 0).all()
    assert (np.ptp(out, axis=1) <= 1).all()


def test_reader_seek_decodes_past_keyframe(tmp_path):
    path = tmp_path / "seek.mp4"
    _write_video(path)
    with av.open(str(path)) as container:
        expected = [frame.to_ndarray(format="rgb24") for frame in container.decode(video=0)]
    reader = PyAVReader(path)
    try:
        out = np.empty(reader.frame_shape, dtype=np.uint8)
        for index in [7, 0, 18, 3]:
            reader.seek(index)
            assert reader.read(out)
            np.testing.assert_array_equal(out, expected[index])
    finally:
        reader.close()


def test_seek_does_not_change_pending_export_or_resume_sequence(tmp_path, qapp):
    path = tmp_path / "input.mp4"
    _write_video(path)
    with av.open(str(path)) as container:
        expected = [frame.to_ndarray(format="rgb24") for frame in container.decode(video=0)]
    config = PresetConfig()
    config.export.resolution = (128, 96)
    config.rendering.fps_plot.visible = False
    config.rendering.frametime_plot.visible = False
    config.get_video_config(0).fps_text.visible = False
    engine = InteractiveEngine()
    engine.load([path], config=config)
    pending = threading.Event()
    release = threading.Event()
    exported = []

    def slow_export(output):
        if output.metrics.frame_index == 8:
            engine.pause()
            pending.set()
            assert release.wait(10)
        exported.append((output.metrics.frame_index, output.frame.copy()))

    engine._export_output = slow_export
    try:
        engine.start()
        assert pending.wait(10)
        deadline = time.monotonic() + 5
        while engine.processed_frames < 9 and time.monotonic() < deadline:
            time.sleep(0.001)
        assert engine.processed_frames >= 9
        for index in [5, 0, 7]:
            result = engine.seek(index)
            np.testing.assert_array_equal(result.prev_frames[0], expected[index])
            np.testing.assert_array_equal(result.frames[0], expected[index + 1])
            np.testing.assert_array_equal(result.composited_frame, expected[index + 1])
            assert engine._seek_compositor is not None
            restored = engine._seek_compositor.snapshot_video_states()[0]
            assert restored.total_frames == index + 1
            assert restored.smoothed_fps == result.fps_values[0]
        release.set()
        engine.resume()
        assert engine._processing_thread is not None
        engine._processing_thread.join(10)
        assert engine.state == EngineState.COMPLETED
        assert [index for index, _ in exported] == list(range(19))
        for index, frame in exported:
            np.testing.assert_array_equal(frame, expected[index + 1])
    finally:
        release.set()
        engine.reset()


def test_engine_exports_preset_dimensions_and_cadence(tmp_path, qapp, monkeypatch):
    path = tmp_path / "input.mp4"
    _write_video(path, 7)
    # Exercise a valid even width whose RGB row needs Qt alignment padding.
    config = PresetConfig()
    config.export.resolution = (318, 238)
    config.export.fps = 60
    output_path = tmp_path / "output.mp4"
    monkeypatch.setattr("trdrop.export.streaming_video.get_best_encoder", lambda: "libx264")
    engine = InteractiveEngine()
    engine.load([path], output_video=output_path, config=config)
    try:
        engine.start()
        assert engine._processing_thread is not None
        engine._processing_thread.join(10)
        assert engine.state == EngineState.COMPLETED
        with av.open(str(output_path)) as container:
            stream = container.streams.video[0]
            assert (stream.width, stream.height) == config.export.resolution
            assert stream.average_rate == Fraction(60)
            assert stream.duration is not None and stream.time_base is not None
            assert stream.duration * stream.time_base == Fraction(6, 30)
            assert len(list(container.decode(video=0))) == 12
    finally:
        engine.reset()
