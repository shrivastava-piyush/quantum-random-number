"""Placeholder IBM Quantum backend for future QPU compatibility."""

from __future__ import annotations

from typing import Any

from qiskit import QuantumCircuit

from .base import HardwareInterface


class IBMQBackend(HardwareInterface):
    """Thin placeholder implementation for IBM Quantum hardware.

    A real implementation would use ``qiskit-ibm-runtime``'s ``Sampler`` /
    ``SamplerV2`` primitive against a real QPU. We keep the method surface
    identical to :class:`SimulatedBackend` so that the rest of the pipeline
    (provider, processor, verification) is backend-agnostic.
    """

    name = "ibmq"

    def __init__(
        self,
        backend_name: str = "ibm_brisbane",
        channel: str = "ibm_quantum",
        token: str | None = None,
        instance: str | None = None,
    ) -> None:
        self.backend_name = backend_name
        self.channel = channel
        self.token = token
        self.instance = instance
        self._service: Any = None  # Lazily initialised.

    def _require_runtime(self) -> Any:
        """Import ``qiskit-ibm-runtime`` on demand, so the core package stays slim."""
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "IBMQBackend requires the 'ibmq' extra. Install with: pip install 'qrng[ibmq]'."
            ) from exc
        return QiskitRuntimeService

    def execute(self, circuit: QuantumCircuit, shots: int = 1) -> list[str]:
        raise NotImplementedError(
            "IBMQBackend.execute is a placeholder. Install qiskit-ibm-runtime and wire "
            "up a Sampler primitive against a real QPU to enable hardware execution."
        )

    def describe(self) -> dict[str, Any]:
        return {
            "backend": self.name,
            "remote_backend": self.backend_name,
            "channel": self.channel,
            "instance": self.instance,
            "initialized": False,
        }
