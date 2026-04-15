"""Von Neumann decorrelation (bias-removing) extractor.

Given an i.i.d. (but possibly biased) bit source, the Von Neumann procedure
emits an unbiased bit per non-equal pair: '01' -> 0, '10' -> 1, '00'/'11' -> dropped.
It assumes independence between successive bits but otherwise requires no
knowledge of the bias.
"""

from __future__ import annotations


def von_neumann_decorrelate(bits: str) -> str:
    """Return the Von Neumann-decorrelated bitstring.

    Works on non-overlapping pairs. Pairs that are '00' or '11' are discarded.
    Output is on average ~25% of the input length for an unbiased source.
    """
    if len(bits) < 2:
        return ""
    out: list[str] = []
    # Process non-overlapping pairs; trailing single bit is discarded.
    for i in range(0, len(bits) - 1, 2):
        pair = bits[i : i + 2]
        if pair == "01":
            out.append("0")
        elif pair == "10":
            out.append("1")
        # '00' and '11' are dropped.
    return "".join(out)
