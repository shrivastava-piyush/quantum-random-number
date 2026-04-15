"""Pydantic-backed configuration for the QRNG pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

DeviceLiteral = Literal["auto", "GPU", "CPU"]
PrecisionLiteral = Literal["single", "double"]


class BackendConfig(BaseModel):
    """Configuration for the simulator / hardware backend."""

    device: DeviceLiteral = Field(
        default="auto",
        description="'auto' detects GPU at runtime, else CPU. Force with 'GPU'/'CPU'.",
    )
    precision: PrecisionLiteral = Field(
        default="double",
        description="Statevector precision; 'double' gives high-precision simulation.",
    )
    method: str = Field(
        default="statevector",
        description="Aer simulation method (statevector, matrix_product_state, ...).",
    )
    shots: int = Field(default=1, ge=1, description="Shots per circuit execution.")
    seed_simulator: int | None = Field(
        default=None,
        description="Optional deterministic seed. Leave unset for physical-style entropy.",
    )
    max_parallel_threads: int = Field(
        default=0, ge=0, description="0 lets Aer auto-select (number of cores)."
    )


class CircuitConfig(BaseModel):
    """Configuration for the Hadamard register circuit."""

    register_width: int = Field(
        default=24,
        ge=1,
        le=30_000,
        description=(
            "Width of the parallel Hadamard register (qubits per circuit). "
            "The statevector method has O(2^n) memory cost, so defaults stay "
            "well below ~30 qubits; for wider registers switch backend.method "
            "to 'matrix_product_state' or 'stabilizer'."
        ),
    )


class PostProcessConfig(BaseModel):
    """Post-processing / randomness-extraction configuration."""

    enable_von_neumann: bool = Field(default=True)
    enable_toeplitz: bool = Field(default=True)
    toeplitz_output_ratio: float = Field(
        default=0.5,
        gt=0.0,
        lt=1.0,
        description="Output-length / input-length ratio for the Toeplitz extractor.",
    )
    toeplitz_seed: int | None = Field(
        default=None,
        description="Optional deterministic seed for the Toeplitz matrix.",
    )


class QRNGConfig(BaseModel):
    """Top-level configuration."""

    backend: BackendConfig = Field(default_factory=BackendConfig)
    circuit: CircuitConfig = Field(default_factory=CircuitConfig)
    postprocess: PostProcessConfig = Field(default_factory=PostProcessConfig)
    log_level: str = Field(default="INFO")

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper
