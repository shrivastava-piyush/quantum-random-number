"""Throughput / latency benchmarking harness."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.processor import EntropyProcessor
    from ..core.provider import EntropyProvider


@dataclass(frozen=True)
class ThroughputBenchmark:
    """Result of a throughput/latency run."""

    total_bits: int
    duration_seconds: float
    raw_bits_produced: int
    post_processed_bits: int

    @property
    def bits_per_second(self) -> float:
        if self.duration_seconds <= 0:
            return float("inf")
        return self.total_bits / self.duration_seconds

    @property
    def latency_ms_per_bit(self) -> float:
        if self.total_bits <= 0:
            return float("inf")
        return (self.duration_seconds * 1_000.0) / self.total_bits

    def as_dict(self) -> dict[str, float | int]:
        return {
            "total_bits": self.total_bits,
            "duration_seconds": self.duration_seconds,
            "raw_bits_produced": self.raw_bits_produced,
            "post_processed_bits": self.post_processed_bits,
            "bits_per_second": self.bits_per_second,
            "latency_ms_per_bit": self.latency_ms_per_bit,
        }


def benchmark_throughput(
    provider: "EntropyProvider",
    processor: "EntropyProcessor",
    target_bits: int = 1024,
    oversample: float = 8.0,
) -> ThroughputBenchmark:
    """Time an end-to-end provider -> processor run.

    ``oversample`` defaults to 8x to leave headroom for the Von-Neumann
    extractor (which drops ~75% of bits on an unbiased source) plus the
    Toeplitz output ratio.
    """
    start = time.perf_counter()
    raw = provider.produce(target_bits, oversample=oversample)
    processed = processor.process(raw.bits, target_bits=target_bits)
    end = time.perf_counter()
    return ThroughputBenchmark(
        total_bits=len(processed.bits),
        duration_seconds=end - start,
        raw_bits_produced=len(raw.bits),
        post_processed_bits=len(processed.bits),
    )
