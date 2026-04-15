"""Quantum Random Number Generator (QRNG).

A production-grade QRNG package optimized for classical simulation,
with a provider/consumer architecture and a hybrid-execution interface
that keeps the path open to real QPU hardware.

Public API:
    QuantumEntropySource  -- AerSimulator-backed entropy source.
    EntropyProvider       -- Executes quantum circuits and emits raw bits.
    EntropyProcessor      -- Runs Von Neumann + Toeplitz post-processing.
    QRNGConfig            -- Pydantic configuration model.
    HardwareInterface     -- Abstract base class for backends.
    SimulatedBackend      -- Aer-backed implementation.
    IBMQBackend           -- Placeholder for IBM Quantum hardware.
    generate_bits         -- High-level convenience function.
"""

from __future__ import annotations

from .backends import HardwareInterface, IBMQBackend, SimulatedBackend
from .config import QRNGConfig
from .core.entropy_source import QuantumEntropySource
from .core.processor import EntropyProcessor
from .core.provider import EntropyProvider
from .facade import generate_bits

__all__ = [
    "EntropyProcessor",
    "EntropyProvider",
    "HardwareInterface",
    "IBMQBackend",
    "QRNGConfig",
    "QuantumEntropySource",
    "SimulatedBackend",
    "generate_bits",
]

__version__ = "0.1.0"
