"""AerSimulator-backed hardware interface implementation."""

from __future__ import annotations

from typing import Any

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from ..config import BackendConfig
from ..logging_utils import get_logger
from .base import HardwareInterface

_log = get_logger(__name__)


def _gpu_available() -> bool:
    """Best-effort detection of an Aer GPU build."""
    try:
        available = AerSimulator().available_devices()  # type: ignore[attr-defined]
        return any(str(d).upper() == "GPU" for d in available)
    except Exception as exc:  # pragma: no cover - environment-dependent
        _log.debug("GPU detection failed: %s", exc)
        return False


class SimulatedBackend(HardwareInterface):
    """Classical simulation backend wrapping :class:`qiskit_aer.AerSimulator`."""

    name = "aer-simulator"

    def __init__(self, config: BackendConfig | None = None) -> None:
        self.config = config or BackendConfig()
        self._simulator = self._build_simulator()

    def _resolve_device(self) -> str:
        requested = self.config.device
        if requested == "auto":
            device = "GPU" if _gpu_available() else "CPU"
            _log.info("Auto-selected Aer device: %s", device)
            return device
        if requested == "GPU" and not _gpu_available():
            _log.warning("GPU requested but not available; falling back to CPU.")
            return "CPU"
        return requested

    def _build_simulator(self) -> AerSimulator:
        device = self._resolve_device()
        options: dict[str, Any] = {
            "method": self.config.method,
            "device": device,
            "precision": self.config.precision,
        }
        if self.config.seed_simulator is not None:
            options["seed_simulator"] = self.config.seed_simulator
        if self.config.max_parallel_threads:
            options["max_parallel_threads"] = self.config.max_parallel_threads
        _log.debug("Instantiating AerSimulator with options: %s", options)
        return AerSimulator(**options)

    def execute(self, circuit: QuantumCircuit, shots: int = 1) -> list[str]:
        # The H+measure register needs no coupling-map routing, so we skip
        # transpilation. This also avoids AerSimulator's 30-qubit default cap.
        result = self._simulator.run(circuit, shots=shots, memory=True).result()
        # 'memory' preserves per-shot bitstrings; 'counts' collapses duplicates.
        memory = result.get_memory(circuit)
        return [bitstring.replace(" ", "") for bitstring in memory]

    def describe(self) -> dict[str, Any]:
        opts = self._simulator.options
        return {
            "backend": self.name,
            "device": getattr(opts, "device", None),
            "method": getattr(opts, "method", None),
            "precision": getattr(opts, "precision", None),
            "seed_simulator": getattr(opts, "seed_simulator", None),
        }
