# Zeta23 compatibility overlays

The pinned PR #298 Zeta23 source uses Lean 4.33.0-rc2 and a different Mathlib.
The bridge targets Lean 4.34.1. Any required migration patches belong in this
directory and must be restricted to build compatibility, source-pinned and reviewed.
No patches exist at bootstrap; therefore Zeta23 native compilation is unverified.

Never change theorem statements, weaken hypotheses, add axioms, or bypass
comparators as a compatibility repair. If theorem statements need changing, stop
and obtain explicit mathematical review before proceeding.
