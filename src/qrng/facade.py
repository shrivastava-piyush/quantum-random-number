"""High-level convenience facade."""

from __future__ import annotations

from .config import QRNGConfig
from .core.entropy_source import QuantumEntropySource
from .core.processor import EntropyProcessor
from .core.provider import EntropyProvider


def generate_bits(n_bits: int, config: QRNGConfig | None = None) -> str:
    """One-shot convenience: build pipeline, produce + post-process ``n_bits``."""
    cfg = config or QRNGConfig()
    source = QuantumEntropySource(
        circuit_config=cfg.circuit, backend_config=cfg.backend
    )
    provider = EntropyProvider(source)
    processor = EntropyProcessor(cfg.postprocess)
    # Oversample generously to absorb Von-Neumann drop + Toeplitz shrinkage.
    raw = provider.produce(n_bits, oversample=12.0)
    processed = processor.process(raw.bits, target_bits=n_bits)
    return processed.bits
