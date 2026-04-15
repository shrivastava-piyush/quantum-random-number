"""Entropy processor: consumes raw bits and applies post-processing."""

from __future__ import annotations

from dataclasses import dataclass

from ..config import PostProcessConfig
from ..logging_utils import get_logger
from ..postprocess.toeplitz import ToeplitzExtractor
from ..postprocess.von_neumann import von_neumann_decorrelate

_log = get_logger(__name__)


@dataclass(frozen=True)
class ProcessedEntropy:
    """Post-processed entropy ready for consumers."""

    bits: str
    raw_input_bits: int
    after_von_neumann_bits: int
    after_toeplitz_bits: int

    def __len__(self) -> int:
        return len(self.bits)


class EntropyProcessor:
    """Applies Von Neumann decorrelation + Toeplitz extraction to raw bits.

    This is the *Consumer* in the provider/consumer pattern. The processor is
    stateless with respect to the backend and only depends on the input
    bitstring and its :class:`PostProcessConfig`.
    """

    def __init__(self, config: PostProcessConfig | None = None) -> None:
        self.config = config or PostProcessConfig()

    def process(self, raw_bits: str, target_bits: int | None = None) -> ProcessedEntropy:
        """Run the full post-processing pipeline on ``raw_bits``.

        Args:
            raw_bits: Input bitstring (only '0'/'1' characters).
            target_bits: Optional final length. If the pipeline produces more
                than this it is truncated; if it produces less a ValueError is
                raised so callers can request more raw entropy.
        """
        if any(c not in "01" for c in raw_bits):
            raise ValueError("raw_bits must contain only '0' and '1' characters")

        after_vn = (
            von_neumann_decorrelate(raw_bits)
            if self.config.enable_von_neumann
            else raw_bits
        )

        if self.config.enable_toeplitz and after_vn:
            extractor = ToeplitzExtractor(
                input_length=len(after_vn),
                output_ratio=self.config.toeplitz_output_ratio,
                seed=self.config.toeplitz_seed,
            )
            final = extractor.extract(after_vn)
        else:
            final = after_vn

        if target_bits is not None:
            if len(final) < target_bits:
                raise ValueError(
                    f"Post-processing yielded {len(final)} bits, "
                    f"below requested target {target_bits}. "
                    "Request more raw entropy via Provider.produce(oversample=...)."
                )
            final = final[:target_bits]

        _log.debug(
            "Processed: raw=%d vn=%d toeplitz=%d",
            len(raw_bits),
            len(after_vn),
            len(final),
        )
        return ProcessedEntropy(
            bits=final,
            raw_input_bits=len(raw_bits),
            after_von_neumann_bits=len(after_vn),
            after_toeplitz_bits=len(final),
        )
