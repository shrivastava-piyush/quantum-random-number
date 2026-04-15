"""Tests for Von Neumann and Toeplitz post-processing."""

from __future__ import annotations

from qrng.postprocess.toeplitz import ToeplitzExtractor
from qrng.postprocess.von_neumann import von_neumann_decorrelate


def test_von_neumann_basic_mapping() -> None:
    # 01 -> 0, 10 -> 1, 00/11 dropped.
    assert von_neumann_decorrelate("01100100") == "010"
    assert von_neumann_decorrelate("0011") == ""
    assert von_neumann_decorrelate("") == ""
    assert von_neumann_decorrelate("1") == ""


def test_von_neumann_only_zero_one_output() -> None:
    out = von_neumann_decorrelate("01" * 50 + "10" * 50)
    assert set(out).issubset({"0", "1"})
    assert len(out) == 100


def test_toeplitz_output_length_and_determinism() -> None:
    bits = "1010110010011100" * 4  # 64 bits
    ext_a = ToeplitzExtractor(input_length=len(bits), output_ratio=0.5, seed=42)
    ext_b = ToeplitzExtractor(input_length=len(bits), output_ratio=0.5, seed=42)
    out_a = ext_a.extract(bits)
    out_b = ext_b.extract(bits)
    assert out_a == out_b  # deterministic under same seed
    assert len(out_a) == 32
    assert set(out_a).issubset({"0", "1"})


def test_toeplitz_changes_with_seed() -> None:
    bits = "1" * 128
    a = ToeplitzExtractor(128, 0.5, seed=1).extract(bits)
    b = ToeplitzExtractor(128, 0.5, seed=2).extract(bits)
    assert a != b
