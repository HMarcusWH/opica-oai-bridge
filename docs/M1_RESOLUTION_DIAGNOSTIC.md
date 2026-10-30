# M1 — Phased native dependency resolution and proof build

**Status:** build instrumentation, not proof acceptance. RH and Step 4 remain open.

Initial native run [#41100399831](https://github.com/HMarcusWH/opica-oai-bridge/actions/runs/41100399831) reached the native build step after pinned source checkout and Lean 4.34.1 setup. That step originally bundled Lake resolution, cache retrieval and Lean compilation, preventing useful phase-level GitHub API diagnostics until completion.

The revised CI provides three separately observable, bounded stages:

| Phase | Gate | Maximum runtime |
|---|---|---|
| Lake dependency resolution and exact OAI patches | `bash scripts/build.sh resolve` | 120 minutes |
| Mathlib cache | `bash scripts/build.sh cache` | 25 minutes |
| Native Lean theorem compilation | `BRIDGE_PRE_RESOLVED=1 bash scripts/build.sh oai` | 170 minutes |

The whole GitHub Actions job retains its 330-minute cap. These budgets leave time for checkout, Lean installation and artifact upload. A timeout is an engineering result, not a statement about the mathematics.

`scripts/verify_resolution.py` checks the locked source SHAs, original checkout identity, generated Lake configuration fingerprint, unique package names, and exact Mathlib revision after `lake update`. It emits only a `DEPENDENCY_RESOLVED_NOT_COMPILED` report. Cache and compilation steps independently re-check this contract. Native source-bound proof receipts are emitted only after successful Lean compilation.

The workflow runs on explicit dispatch and once upon changes to its own workflow file on `main`. Its concurrency group remains serial without cancellation. Source edits in other files do not trigger expensive native builds.

If resolution fails, inspect OAI's full 30-dependency and patch-clone configuration. If caching fails, inspect the original Mathlib revision and cache tool. If compilation fails, inspect the actual first Lean error and source-bound receipt. Only after an OAI theorem is kernel-checked should the independent comparator run and Zeta23 compatibility begin.
