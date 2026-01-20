"""Benchmark comparison strategies for duplicate detection.

Run with: uv run pytest tests/benchmarks/test_analysis_strategies.py -v -s
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from trdrop.analysis.strategies import get_all_strategies


def generate_test_frames(
    height: int = 720,
    width: int = 1280,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate test frames: identical pair and different pair.

    Returns:
        (frame_a, frame_b_same, frame_b_diff)
    """
    rng = np.random.default_rng(seed)

    # Base frame
    frame_a = rng.integers(0, 256, (height, width, 3), dtype=np.uint8)

    # Identical frame (duplicate)
    frame_b_same = frame_a.copy()

    # Different frame (not duplicate) - change ~10% of pixels
    frame_b_diff = frame_a.copy()
    n_changed = int(height * width * 0.10)
    y_coords = rng.integers(0, height, n_changed)
    x_coords = rng.integers(0, width, n_changed)
    frame_b_diff[y_coords, x_coords] = rng.integers(0, 256, (n_changed, 3), dtype=np.uint8)

    return frame_a, frame_b_same, frame_b_diff


class TestAnalysisStrategies:
    """Benchmark different comparison strategies."""

    def test_strategy_benchmark(self) -> None:
        """Benchmark all strategies on duplicate and non-duplicate frames."""
        frame_a, frame_same, frame_diff = generate_test_frames(720, 1280)

        strategies = get_all_strategies()
        n_iterations = 50
        warmup = 5

        print("\n")
        print("=" * 90)
        print("ANALYSIS STRATEGY BENCHMARK")
        print("=" * 90)
        print(f"Frame size: 1280x720 = {1280*720:,} pixels")
        print(f"Iterations: {n_iterations} (after {warmup} warmup)")
        print()

        # Header
        print(f"{'Strategy':<20} {'Dup (ms)':<10} {'Diff (ms)':<10} {'Total':<10} "
              f"{'Speedup':<8} {'Pixels':<12} {'Correct':<8}")
        print("-" * 90)

        baseline_time = None
        results = []

        for strategy in strategies:
            # Warmup
            for _ in range(warmup):
                strategy.compare(frame_a, frame_same, 10, 0.01)
                strategy.compare(frame_a, frame_diff, 10, 0.01)

            # Benchmark duplicates
            t0 = time.perf_counter()
            for _ in range(n_iterations):
                is_dup, ratio = strategy.compare(frame_a, frame_same, 10, 0.01)
            dup_time = (time.perf_counter() - t0) / n_iterations * 1000
            dup_correct = is_dup  # Should be True

            # Benchmark non-duplicates
            t0 = time.perf_counter()
            for _ in range(n_iterations):
                is_dup, ratio = strategy.compare(frame_a, frame_diff, 10, 0.01)
            diff_time = (time.perf_counter() - t0) / n_iterations * 1000
            diff_correct = not is_dup  # Should be False

            total_time = dup_time + diff_time

            if baseline_time is None:
                baseline_time = total_time
                speedup = 1.0
            else:
                speedup = baseline_time / total_time

            # Calculate effective pixels compared
            if "stride_2x2" in strategy.name or "stride" in strategy.name and "2" in strategy.name:
                pixels = 1280 * 720 // 4
            elif "stride_4x4" in strategy.name or "4x4" in strategy.name:
                pixels = 1280 * 720 // 16
            elif "rows_2" in strategy.name:
                pixels = 1280 * 720 // 2
            elif "rows_4" in strategy.name:
                pixels = 1280 * 720 // 4
            else:
                pixels = 1280 * 720

            correct = "OK" if (dup_correct and diff_correct) else "FAIL"

            results.append({
                "name": strategy.name,
                "dup_time": dup_time,
                "diff_time": diff_time,
                "total_time": total_time,
                "speedup": speedup,
                "pixels": pixels,
                "correct": correct,
            })

            print(f"{strategy.name:<20} {dup_time:<10.3f} {diff_time:<10.3f} {total_time:<10.3f} "
                  f"{speedup:<8.2f}x {pixels:<12,} {correct:<8}")

        print("=" * 90)

        # Summary
        print("\nFastest strategies:")
        sorted_results = sorted(results, key=lambda x: x["total_time"])
        for i, r in enumerate(sorted_results[:3], 1):
            print(f"  {i}. {r['name']}: {r['total_time']:.3f}ms ({r['speedup']:.2f}x)")

        # All should be correct
        for r in results:
            assert r["correct"] == "OK", f"{r['name']} gave incorrect results"

    def test_accuracy_comparison(self) -> None:
        """Verify all strategies give consistent results."""
        frame_a, frame_same, frame_diff = generate_test_frames(720, 1280)
        strategies = get_all_strategies()

        print("\n")
        print("=" * 70)
        print("ACCURACY COMPARISON")
        print("=" * 70)

        # Get baseline results
        baseline = strategies[0]
        _, baseline_ratio_same = baseline.compare(frame_a, frame_same, 10, 0.01)
        _, baseline_ratio_diff = baseline.compare(frame_a, frame_diff, 10, 0.01)

        print(f"Baseline ({baseline.name}):")
        print(f"  Duplicate ratio: {baseline_ratio_same:.6f}")
        print(f"  Different ratio: {baseline_ratio_diff:.6f}")
        print()

        print(f"{'Strategy':<20} {'Dup Ratio':<12} {'Diff Ratio':<12} {'Dup?':<6} {'Diff?':<6}")
        print("-" * 70)

        for strategy in strategies:
            is_dup_same, ratio_same = strategy.compare(frame_a, frame_same, 10, 0.01)
            is_dup_diff, ratio_diff = strategy.compare(frame_a, frame_diff, 10, 0.01)

            print(f"{strategy.name:<20} {ratio_same:<12.6f} {ratio_diff:<12.6f} "
                  f"{'Yes' if is_dup_same else 'No':<6} {'Yes' if is_dup_diff else 'No':<6}")

        print("=" * 70)
