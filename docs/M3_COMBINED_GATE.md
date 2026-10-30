# M3 — source-faithful combined OAI × Zeta23 kernel check

**Unverified until the native CI gate succeeds.** The existing original OpenAI 7/8 theorem compiled in M1 run `41100399831` (7,061 build jobs). M2 must separately show the original Zeta23 Round 4 prime-discrepancy module compiles under that same Lean/Mathlib version.

## Workflow

`M3 Combined OAI-Zeta23 import and axiom check` automatically starts when `M2 Zeta23 Lean 4.34 compatibility diagnostic` **completes successfully on `main`**. The M3 job is skipped on M2 failure, cancellation, or other branches. A manual dispatch permits a source-bound replay. All heavyweight native workflows share one serialized `full-bridge-build` concurrency group and do not cancel running jobs.

The job checks out **only the bridge's default branch** with a read-only token and no persistent credentials. It does not execute, restore caches from, or download artifacts from a triggered M2 run. The mathematical sources are freshly fetched at exact commits from `source-lock.json`; pins and generated Lake configuration are verified before proceeding.

The native command `BRIDGE_PRE_RESOLVED=1 bash scripts/build.sh smoke` compiles the real `OAI.NumberTheory.DirichletL.Nonvanishing` and `Zeta23.OPICARound4.PrimeDiscrepancyIntegral`, then `OPICAOAI.Smoke`. `BRIDGE_PRE_RESOLVED=1 bash scripts/build.sh axioms` runs `OPICAOAI/PrintAxioms.lean` to inspect the actual wrapper's transitive axioms, and rejects anything beyond the existing allowlist.

These independent stages produce source-bound native receipts only on success, with logs and failure artifacts otherwise. `M3` does not establish the separate independent comparator test required for the final mathematical acceptance gate, and it does not prove an independent Step 4 estimate or RH.

## Acceptance and failure modes

- **Pass:** a genuinely combined OAI/Zeta23 import and one source-bound 7/8 wrapper proof compile with a permitted-axiom audit in one Lean environment. A completed receipt is necessary; static preflight is not sufficient.
- **M2 fails:** this job does not run automatically. Inspect M2's first native failure, repair the *compatible shared environment* without changing theorem statements, then rerun M2.
- **Resolution/timeout:** retain source SHA, exact Mathlib pin, manifest, and stage logs, and improve caching or isolate source errors. Do not assume mathematical failure from infrastructure timeouts.
- **Compiler/type error:** locate the first actual Lean source error and ensure missing imports/definitions are resolved before adding bridge mathematical consumers.
- **Axiom error:** explicitly fail M3; do not add a permitted `sorry` or weaken `check_axioms.py` to mark a theorem accepted.

## Next mathematical consumer

Only after M3 succeeds should `OPICAOAI.ZeroDisplacementBridge` (draft PR #3) be compiled and audited using its dedicated `zero` native stage. That proof candidate combines OpenAI's literal 7/8 theorem with Zeta23's genuine zero configuration and source-specific fixed-window rate, but **does not prove a tighter zero-free bound or Step 4**.
