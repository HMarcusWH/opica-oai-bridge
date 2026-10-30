#!/usr/bin/env python3
"""Fail-closed #print axioms audit; independent checks of OAI, Zeta23 and bridge."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOW = frozenset(("propext", "Quot.sound", "Classical.choice"))
THEOREM = "OPICAOAI.riemannZeta_ne_zero_above_seven_eighths"
SOURCE_THEOREMS = (
    "OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re",
    "Zeta23.OPICARound4.prime_log_abel",
)
ALL_THEOREMS = SOURCE_THEOREMS + (THEOREM,)


def _axioms_for(log: str, name: str) -> set[str]:
    quoted = "'" + re.escape(name) + "'"
    dependencies = re.findall(
        quoted + r" depends on axioms: \[([^\]]*)\]", log
    )
    independent = re.findall(
        quoted + r" does not depend on any axioms", log
    )
    if len(dependencies) + len(independent) != 1:
        raise ValueError(
            f"Expected exactly one Lean axiom output for {name}; "
            f"found {len(dependencies)} dependency declarations and "
            f"{len(independent)} no-axiom declarations"
        )
    return set(a.strip() for a in dependencies[0].split(",") if a.strip()) if dependencies else set()


def check(log: str, *, all_sources: bool = False) -> None:
    # Do not accept successful-looking output coexisting with compiler errors.
    if any(k in log for k in ("error:", "sorryAx", "(sorry)", "admit")):
        raise ValueError("Failure, sorry or unsupported admission in kernel/axiom log")
    targets = ALL_THEOREMS if all_sources else (THEOREM,)
    for target in targets:
        axioms = _axioms_for(log, target)
        extras = axioms - ALLOW
        if extras:
            raise ValueError(f"Unexpected proof axioms for {target}: {sorted(extras)}")
        print(f"AXIOM AUDIT PASS: {target}; actual = {sorted(axioms)}")


if __name__ == "__main__":
    try:
        if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--all-sources"):
            raise ValueError("usage: check_axioms.py LOG [--all-sources]")
        check(Path(sys.argv[1]).read_text(encoding="utf-8"),
              all_sources=(len(sys.argv) == 3))
    except (Exception, IndexError) as exc:
        print(f"AXIOM AUDIT FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
