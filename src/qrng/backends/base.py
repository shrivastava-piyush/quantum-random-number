"""Abstract hardware interface for hybrid (simulator / QPU) execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from qiskit import QuantumCircuit


class HardwareInterface(ABC):
    """Abstract base class for any QRNG execution backend.

    Concrete implementations must provide :meth:`execute`, returning a list
    of measurement bitstrings (each 'n-qubit' wide, MSB-first per Qiskit's
    convention).
    """

    name: str = "abstract"

    @abstractmethod
    def execute(self, circuit: QuantumCircuit, shots: int = 1) -> list[str]:
        """Run ``circuit`` for ``shots`` shots and return raw bitstrings."""

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Return a serializable description of the backend (for telemetry)."""

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<{self.__class__.__name__} name={self.name!r}>"
