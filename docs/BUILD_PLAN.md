# Complete local build, bootstrap, deployment and acceptance plan

## Goal

Create a reusable, proof-trustworthy third repository integrating the full
OpenAI OAI and Zeta23 source trees in a single toolchain, with distinct
compilation, theorem-composition and source-exclusion gates. The bridge
supports further OPICA Step 4 research but **does not assert RH**.

## Source state at design checkpoint — 30 October 2026

- `opica-oai-bridge` was an empty, writable GitHub repository.
- OAI fork pinned at `4eaee875...`, same commit as the checked upstream.
- OAI: Lean `v4.34.1`, Mathlib `d13f23...`, 30 direct Git dependencies,
  special `run_cmd` and `post_update` compatibility patch hooks.
- Zeta23 PR #298: `ebbd787...`, Lean `v4.33.0-rc2`, Mathlib `51e699...`.
- The Round 4 source audits distinguish completed obstruction-preservation
  from **OPEN** opposing arithmetic estimates and current-head acceptance.
- The host constructing this scaffold has Git/Python but no Lean/Lake and no
  outbound GitHub DNS. Local tests can validate the generator; complete Lean
  compilation must occur on a configured Linux/WSL2 machine or CI runner.

## Milestone graph

| ID | Deliverable | Test/receipt | Blocking dependency |
|---|---|---|---|
| M0 | Lock, composer, Python tests, docs, fail-closed CI | `make preflight test` pass | None |
| M1 | Original OAI library builds on locked toolchain | Native 7/8 theorem and comparator | M0 |
| M2 | Original Zeta23 source compiles with reviewed compatibility changes | Round4 target, full theorem type/axiom audit | M0 |
| M3 | One Lean consumer imports both real libraries | `OPICAOAI.Smoke` and axiom audit | M1+M2 |
| M4 | Entire OAI and Zeta23 libraries build; manifest frozen | Full build, source/pin evidence | M3 |
| M5 | Zeros, Theta and prime discrepancy bridge theorems | Formal source-faithful proofs | M3 |
| M6 | Native Möbius echo/common-signal mechanism | Formal source Laplace and continuation | M3 |
| M7 | Real independent Step 4 arithmetic saving | Independent theorem/proof acceptance | M4+M5+M6 |

### M0 — Bootstrap scaffold (local)

1. Pin exact Git objects and toolchain in `source-lock.json`.
2. Implement `prepare_workspace.py` with offline simulation and strict source
   pin, blob, remote, symlink and generated Lake checks.
3. Generate Lake configuration *from original OAI lakefile* rather than
   silently rewriting 30 dependency declarations.
4. Write source smoke theorem and `#print axioms` consumer.
5. Implement static tests, negative controls, security documents and CI.
6. Run Python/static tests and ZIP the local source tree.
7. Initialize the empty GitHub `main` with a minimal bootstrap README, publish
   the complete scaffold to a separate reviewed branch, and open a draft PR.
8. **Do not call the repository compiler-green** until M1-M4 pass.

### M1 — OAI proof and toolchain

1. Prepare the pinned OAI checkout, verify original license and Lake blobs.
2. Inspect its patch dependencies, patch paths and semantics in the generated
   workspace. Preserve pre-resolution and post-update verification.
3. Run `lake update --keep-toolchain`, download Mathlib cache and compile
   `+OAI.NumberTheory.DirichletL.Nonvanishing`.
4. Inspect/record the theorem's actual type and `#print axioms`.
5. Separately replay the OAI comparator's
   `ComparatorChallenges/QuasiRiemannHypothesis.json` using the required
   `comparator`, `landrun` and `lean4export` versions.
6. Prove a primitive OAI-only wrapper test and hash-check the dependency
   and compiler outputs.

### M2 — Zeta23 Lean 4.34 migration

1. Preserve original Round 4 commit and formal-source registries; do not
   change main or PR #298.
2. Use the unified OAI/Mathlib lock and build
   `+Zeta23.OPICARound4.PrimeDiscrepancyIntegral`.
3. Classify each failure: syntax/API change, missing dependency, lemma
   incompatibility, kernel change, or genuine theorem-proposition conflict.
4. Apply only audited compatibility patches to an isolated checkout. Require
   exact preimage/postimage fingerprints and clean diff review.
5. Replay existing Zeta23 original theorem types and permitted axiom sets.
6. Verify all 48 Round 4 owned modules and 500 supporting declarations against
   actual source registries, not merely logs of older PR commits.
7. Re-run its governed independent consumers and non-calibration gates.

### M3 — Cross-library smoke

1. Compile `OPICAOAI/Smoke.lean` importing the genuine OAI theorem and OPICA
   `PrimeDiscrepancyIntegral.lean`.
2. Check the exact 7/8 theorem type and an imported OPICA source declaration.
3. Run `OPICAOAI/PrintAxioms.lean` and fail on unexpected axioms.
4. Check the source paths and proof import closure against the source lock.
5. Record the first complete cross-import acceptance receipt.

### M4 — Full code build

1. Pin and check all transitive dependencies in `lake-manifest.json`.
2. Build `OAI`, `Zeta23`, `OPICAOAI` libraries in the same environment.
3. Split expensive builds into independently replayable source-bound jobs.
4. Confirm no `sorryAx` or unknown axioms in promoted theorem dependencies.
5. Run comparator and deterministic known-invalid controls, preserving
   no-secret, no-write CI isolation.
6. Publish traceable build artifacts and hashes; no accepted flag from only
   a green workflow shell.

### M5 — Arithmetic bridges

1. Match actual zero configurations and derive Theta <= 3/8.
2. Derive a verified Chebyshev error theorem from the 7/8 zero-free region.
3. Combine the exact Zeta23 all-von-Mangoldt Abel identity with the source-
   selected derivative and endpoints.
4. Link Paper X fixed-source native rates to the actual native `Theta` object.
5. Verify that source-envelope and damping conclusions have the correct
   epsilon, `d`, `T`, and uniformity scopes.

### M6 — Causal/common-signal bridge

1. Reuse OAI continuation architecture, not its 7/8-specific margin as a
   fictional improvement.
2. Define exact Möbius echo for the predetermined causal target.
3. Prove the source transform identity in the convergence half-plane.
4. Prove source visibility and identify zeros/poles including multiplicity.
5. State a **separately OPEN** independent echo growth estimate.
6. Compare it against `C_DIRECT` and `C_SMOOTH_SCHUR` without conflating
   the original smooth detector and the native causal target.

### M7 — Terminal research and release decision

1. Prioritize an independent lower bound for genuine original smooth `W(g,g)`
   on the permitted late generated packets (the audit's `C_DIRECT`).
2. Preserve `C_SMOOTH_SCHUR`, common cutoff, and causal routes as alternatives.
3. Check all source-actual, correct metric, cutoff, aperture, phase, shift,
   detector and quantifier dependencies before using a generated packet.
4. If a genuinely independent contradictory estimate is proved, route it
   through the existing Zeta23 Million Dollar PR's terminal verification;
   the bridge cannot self-certify it by changing an OPEN property flag.

## Local commands

```bash
# Linux / WSL2, from the clone of this bridge repo
make preflight test
make prepare
make oai
make zeta
make smoke
make axioms
make comparator
make all       # expensive, only after M1-M3 passes
```

### Hardware/CI planning

The OpenAI repo and source dependencies are large, so budget substantial disk
and memory; check free resources before selecting a full-build runner. GitHub
six-hour whole-job limits and cancellation hazards must be accounted for in
separate governed job/attempt artifacts. The manual integration workflow is a
convenience runner, not a promise of full acceptance on hosted hardware.

## User-visible stage reporting

Each stage has one of: `OPEN`, `SOURCE_PREPARED`, `NATIVE_CHECKED`,
`INDEPENDENTLY_VERIFIED`, or `FAILED` with a reproducible reason. Static tests
cannot confer `NATIVE_CHECKED`; a Lean compile cannot confer independent
source/theorem acceptance; an import of 7/8 cannot confer `RH_PROVED`.

## Release sequence

- Bootstrap main with README so the empty repo has a default branch.
- Put all files on `bootstrap/source-composition` and open a **draft** PR.
- Keep the draft until M0 source tests and review are done; do not merge on
  paper-only correctness assertions.
- Work on independent M1, M2 compatibility branches; pin their exact inputs.
- Promote the full bridge only after M3 and M4 checks are source-bound.
- Do not modify original OAI or Zeta23 main, or touch Round 4's terminal
  acceptance infrastructure, through an incidental bridge build.
