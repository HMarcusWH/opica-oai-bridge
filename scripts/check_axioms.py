#!/usr/bin/env python3
"""Fail-closed parser for explicit Lean '#print axioms' proof audit receipts."""
import re
import sys
from pathlib import Path

ALLOW = {"propext", "Quot.sound", "Classical.choice"}
TARGETS = {
    "smoke": ("OPICAOAI.riemannZeta_ne_zero_above_seven_eighths",),
    "zero": (
        "OPICAOAI.native_zero_displacement_sup_le_three_eighths",
        "OPICAOAI.native_fixed_window_rate_eventually_lt_three_eighths_add",
    ),
}


def check(log: str, stage: str = "smoke") -> None:
    if stage not in TARGETS:
        raise ValueError("Unexpected axiom audit stage")
    if any(k in log for k in ("error:", "sorryAx", "(sorry)", "admit")):
        raise ValueError("Failure, sorry or unsupported admission in kernel/axiom log")
    # Each exported declaration must occur exactly once; no missing or duplicate data.
    for theorem in TARGETS[stage]:
        pattern = r"'" + re.escape(theorem) + r"' depends on axioms: \[([^\]]*)\]"
        matches = re.findall(pattern, log)
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one axiom declaration for {theorem}, found {len(matches)}")
        axioms = {a.strip() for a in matches[0].split(",") if a.strip()}
        if not axioms.issubset(ALLOW):
            raise ValueError(f"{theorem}: unexpected proof axioms: {sorted(axioms - ALLOW)}")
        print(f"AXIOM AUDIT PASS: {theorem}; allowed = {sorted(axioms)}")


if __name__ == "__main__":
    try:
        check(Path(sys.argv[1]).read_text(encoding="utf-8"),
              sys.argv[2] if len(sys.argv) > 2 else "smoke")
    except (Exception, IndexError) as exc:
        print(f"AXIOM AUDIT FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
