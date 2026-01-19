"""Processing pipeline for video analysis."""

from __future__ import annotations


class ProcessingPipeline:
    """
    Main processing pipeline for video analysis.

    TODO: Implement pipeline stages:
    - Frame reading from VideoReader
    - Duplicate detection via DuplicateAnalyzer
    - Tear detection via TearAnalyzer
    - Result storage in VideoResultBuffer
    - Progress reporting
    """

    def run(self) -> None:
        """Run the processing pipeline."""
        raise NotImplementedError("ProcessingPipeline.run() not yet implemented")
