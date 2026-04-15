"""NIST SP 800-22 statistical tests for randomness."""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.special import erfc


@dataclass(frozen=True)
class TestResult:
    """Outcome of a single NIST test."""

    name: str
    statistic: float
    p_value: float
    passed: bool
    threshold: float = 0.01

    def as_dict(self) -> dict[str, float | str | bool]:
        return {
            "name": self.name,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "passed": self.passed,
            "threshold": self.threshold,
        }


def monobit_frequency_test(bits: str, alpha: float = 0.01) -> TestResult:
    """NIST SP 800-22 §2.1 -- Frequency (Monobit) Test.

    H0: The sequence is a random sequence (equal 0s and 1s in the limit).

    Computes s_n = sum_i (2*b_i - 1), then s_obs = |s_n| / sqrt(n),
    and p = erfc(s_obs / sqrt(2)). p >= alpha -> pass.
    """
    n = len(bits)
    if n == 0:
        raise ValueError("monobit_frequency_test requires at least 1 bit")
    if any(c not in "01" for c in bits):
        raise ValueError("monobit_frequency_test requires a 0/1 bitstring")
    ones = bits.count("1")
    s_n = (2 * ones) - n
    s_obs = abs(s_n) / math.sqrt(n)
    p_value = float(erfc(s_obs / math.sqrt(2)))
    return TestResult(
        name="NIST SP 800-22 Frequency (Monobit)",
        statistic=s_obs,
        p_value=p_value,
        passed=p_value >= alpha,
        threshold=alpha,
    )
