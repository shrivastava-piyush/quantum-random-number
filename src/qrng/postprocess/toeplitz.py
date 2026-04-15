"""Toeplitz-hash randomness extractor.

A Toeplitz matrix T of shape (m, n) defined by a uniformly random
seed of (m + n - 1) bits is a universal family of hash functions
(Leftover Hash Lemma): if the input has min-entropy k, then for any
m <= k - 2 * log(1/eps) the output is eps-close to uniform. We
implement the matrix-vector multiplication in GF(2) via NumPy bitwise ops.
"""

from __future__ import annotations

import secrets

import numpy as np


class ToeplitzExtractor:
    """Linear (Toeplitz) randomness extractor over GF(2)."""

    def __init__(
        self,
        input_length: int,
        output_ratio: float = 0.5,
        seed: int | None = None,
    ) -> None:
        if input_length <= 1:
            raise ValueError("input_length must be > 1")
        if not 0.0 < output_ratio < 1.0:
            raise ValueError("output_ratio must be in (0, 1)")
        self.input_length = input_length
        self.output_length = max(1, int(input_length * output_ratio))
        self.seed = seed
        self._rng = (
            np.random.default_rng(seed)
            if seed is not None
            else np.random.default_rng(secrets.randbits(64))
        )
        # Toeplitz matrix is fully determined by its first column (m bits)
        # and first row (n bits), sharing the top-left corner -> m+n-1 bits.
        self._first_col = self._rng.integers(0, 2, size=self.output_length, dtype=np.uint8)
        self._first_row = self._rng.integers(0, 2, size=self.input_length, dtype=np.uint8)
        # Share corner: first_row[0] == first_col[0].
        self._first_row[0] = self._first_col[0]

    def _build_matrix(self) -> np.ndarray:
        m, n = self.output_length, self.input_length
        # Toeplitz: T[i, j] depends only on (i - j). Build via broadcasting.
        # diag index d = i - j, in range [-(n-1), m-1].
        # Use first_col for d >= 0 and first_row for d < 0.
        i = np.arange(m).reshape(-1, 1)
        j = np.arange(n).reshape(1, -1)
        d = i - j
        t = np.where(d >= 0, self._first_col[np.clip(d, 0, m - 1)], self._first_row[np.clip(-d, 0, n - 1)])
        return t.astype(np.uint8)

    def extract(self, bits: str) -> str:
        """Compute T @ x (mod 2) where ``x`` is the input bitstring."""
        if len(bits) != self.input_length:
            raise ValueError(
                f"Toeplitz extractor expected {self.input_length} bits, got {len(bits)}"
            )
        x = np.frombuffer(bits.encode("ascii"), dtype=np.uint8) - ord("0")
        t = self._build_matrix()
        # Matrix-vector over GF(2): parity of bitwise-AND rows.
        product = np.bitwise_and(t, x).sum(axis=1) & 1
        return "".join("1" if b else "0" for b in product.tolist())
