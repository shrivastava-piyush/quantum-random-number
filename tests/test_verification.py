"""Tests for the verification suite."""

from __future__ import annotations

import random

from qrng.verification.entropy import shannon_entropy
from qrng.verification.nist import monobit_frequency_test


def _uniform_bits(seed: int, n: int) -> str:
    rng = random.Random(seed)
    return "".join(str(rng.getrandbits(1)) for _ in range(n))


def test_shannon_entropy_uniform_high() -> None:
    bits = _uniform_bits(0xC0FFEE, 10_000)
    assert shannon_entropy(bits) >= 0.99


def test_shannon_entropy_all_zeros_is_zero() -> None:
    assert shannon_entropy("0" * 1024) == 0.0


def test_monobit_passes_on_uniform() -> None:
    bits = _uniform_bits(12345, 10_000)
    result = monobit_frequency_test(bits)
    assert result.passed


def test_monobit_fails_on_all_ones() -> None:
    result = monobit_frequency_test("1" * 1024)
    assert not result.passed
    assert result.p_value < 0.01
