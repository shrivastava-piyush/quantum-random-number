"""Entropy provider: orchestrates circuit execution to meet a bit budget."""

from __future__ import annotations

from dataclasses import dataclass

from ..logging_utils import get_logger
from .entropy_source import QuantumEntropySource

_log = get_logger(__name__)


@dataclass(frozen=True)
class RawEntropy:
    """Raw bits emitted by the provider along with execution telemetry."""

    bits: str
    shots: int
    register_width: int
    backend: str

    def __len__(self) -> int:
        return len(self.bits)


class EntropyProvider:
    """Produces raw entropy from a :class:`QuantumEntropySource`.

    This is the *Provider* in the provider/consumer split: it is responsible
    for circuit execution and batching, but it does *not* perform any
    statistical post-processing. That is the consumer's (EntropyProcessor's) job.
    """

    def __init__(self, source: QuantumEntropySource | None = None) -> None:
        self.source = source or QuantumEntropySource()

    def produce(self, n_bits: int, oversample: float = 1.0) -> RawEntropy:
        """Produce at least ``n_bits`` raw bits.

        Args:
            n_bits: Target number of bits.
            oversample: Multiplier used to request extra bits for downstream
                consumers that shrink their input (e.g. Von Neumann).
        """
        if n_bits <= 0:
            raise ValueError("n_bits must be positive")
        if oversample < 1.0:
            raise ValueError("oversample must be >= 1.0")
        target = int(n_bits * oversample)
        width = self.source.circuit_config.register_width
        shots = max(1, -(-target // width))
        _log.debug(
            "Producing %d raw bits (target=%d, shots=%d, width=%d)",
            target,
            target,
            shots,
            width,
        )
        chunks = self.source.sample(shots=shots)
        bits = "".join(chunks)[:target]
        return RawEntropy(
            bits=bits,
            shots=shots,
            register_width=width,
            backend=self.source.backend.name,
        )
