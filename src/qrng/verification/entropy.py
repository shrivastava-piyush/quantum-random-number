"""Shannon entropy computations."""

from __future__ import annotations

import numpy as np
from scipy.stats import entropy as scipy_entropy


def shannon_entropy(bits: str, base: int = 2) -> float:
    """Return the Shannon entropy of ``bits``'s empirical 0/1 distribution.

    The theoretical maximum for a uniform binary source is 1.0 (in base 2);
    production QRNG output should hit H >= 0.99.
    """
    if len(bits) == 0:
        return 0.0
    if any(c not in "01" for c in bits):
        raise ValueError("shannon_entropy requires a 0/1 bitstring")
    ones = bits.count("1")
    zeros = len(bits) - ones
    probs = np.array([zeros, ones], dtype=np.float64) / len(bits)
    return float(scipy_entropy(probs, base=base))
