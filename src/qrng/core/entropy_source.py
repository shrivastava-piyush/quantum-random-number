"""Quantum entropy source: parallel Hadamard-Measurement register."""

from __future__ import annotations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from ..backends.base import HardwareInterface
from ..backends.simulated import SimulatedBackend
from ..config import BackendConfig, CircuitConfig
from ..logging_utils import get_logger

_log = get_logger(__name__)


class QuantumEntropySource:
    """Generates raw quantum bits via an n-qubit Hadamard + measure circuit.

    This is the lowest layer of the stack -- it only knows how to produce
    uniformly distributed (on an ideal device) raw bits, which downstream
    post-processing will harden.
    """

    def __init__(
        self,
        circuit_config: CircuitConfig | None = None,
        backend: HardwareInterface | None = None,
        backend_config: BackendConfig | None = None,
    ) -> None:
        self.circuit_config = circuit_config or CircuitConfig()
        self.backend: HardwareInterface = backend or SimulatedBackend(backend_config)
        self._circuit = self._build_circuit(self.circuit_config.register_width)
        _log.debug(
            "QuantumEntropySource ready (width=%d, backend=%s)",
            self.circuit_config.register_width,
            self.backend.name,
        )

    @staticmethod
    def _build_circuit(width: int) -> QuantumCircuit:
        """Construct the parallel Hadamard register: H⊗n followed by measurement."""
        qreg = QuantumRegister(width, name="q")
        creg = ClassicalRegister(width, name="c")
        qc = QuantumCircuit(qreg, creg, name=f"qrng_h{width}")
        qc.h(qreg)
        qc.measure(qreg, creg)
        return qc

    @property
    def circuit(self) -> QuantumCircuit:
        return self._circuit

    def sample(self, shots: int = 1) -> list[str]:
        """Return ``shots`` raw bitstrings of width ``register_width``."""
        return self.backend.execute(self._circuit, shots=shots)

    def sample_raw_bits(self, n_bits: int) -> str:
        """Return a concatenated string of at least ``n_bits`` raw bits."""
        width = self.circuit_config.register_width
        shots = max(1, -(-n_bits // width))  # ceil division
        chunks = self.sample(shots=shots)
        joined = "".join(chunks)
        return joined[:n_bits]
