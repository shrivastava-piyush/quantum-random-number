"""End-to-end pipeline tests (require qiskit-aer)."""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit_aer")

from qrng import QRNGConfig, generate_bits  # noqa: E402
from qrng.config import BackendConfig, CircuitConfig, PostProcessConfig  # noqa: E402
from qrng.core.entropy_source import QuantumEntropySource  # noqa: E402
from qrng.core.processor import EntropyProcessor  # noqa: E402
from qrng.core.provider import EntropyProvider  # noqa: E402
from qrng.verification.entropy import shannon_entropy  # noqa: E402
from qrng.verification.nist import monobit_frequency_test  # noqa: E402


def test_generate_bits_returns_requested_length() -> None:
    cfg = QRNGConfig(
        circuit=CircuitConfig(register_width=16),
        backend=BackendConfig(device="CPU", precision="double", seed_simulator=7),
        postprocess=PostProcessConfig(toeplitz_seed=7),
    )
    bits = generate_bits(128, config=cfg)
    assert len(bits) == 128
    assert set(bits).issubset({"0", "1"})


def test_pipeline_quality_on_sim() -> None:
    cfg = QRNGConfig(
        circuit=CircuitConfig(register_width=24),
        backend=BackendConfig(device="CPU", precision="double"),
    )
    source = QuantumEntropySource(circuit_config=cfg.circuit, backend_config=cfg.backend)
    provider = EntropyProvider(source)
    processor = EntropyProcessor(cfg.postprocess)

    raw = provider.produce(2048, oversample=12.0)
    processed = processor.process(raw.bits, target_bits=2048)

    assert shannon_entropy(processed.bits) >= 0.99
    assert monobit_frequency_test(processed.bits).passed
