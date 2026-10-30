#!/usr/bin/env python3
"""Strict parser for Lean '#print axioms' proof audit of our smoke theorem."""
import re
import sys
from pathlib import Path

ALLOW = {"propext", "Quot.sound", "Classical.choice"}
THEOREM = "OPICAOAI.riemannZeta_ne_zero_above_seven_eighths"


def check(log: str) -> None:
    if any(k in log for k in ("error:", "sorryAx", "(sorry)", "admit")):
        raise ValueError("Failure, sorry or unsupported admission in kernel/axiom log")
    # The declaration is produced by Lean as: 'name' depends on axioms: [..]
    match = re.search(r"'" + re.escape(THEOREM) +
                      r"' depends on axioms: \[([^\]]*)\]", log)
    if not match:
        raise ValueError("Missing exact theorem axiom declaration; fail closed")
    axioms = {a.strip() for a in match.group(1).split(",") if a.strip()}
    if not axioms.issubset(ALLOW):
        raise ValueError(f"Unexpected proof axioms: {sorted(axioms - ALLOW)}")
    print(f"AXIOM AUDIT PASS: {THEOREM}; allowed = {sorted(axioms)}")


if __name__ == "__main__":
    try:
        check(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (Exception, IndexError) as exc:
        print(f"AXIOM AUDIT FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
