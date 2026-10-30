# Provenance, security and acceptance

## Threat and failure model

1. **Untrusted upstream build scripts:** OAI's Lake config executes local Git
   operations and applies dependency patches during resolution; audit exact
   pinned code before running. No credentials or repository-write token should
   be present during `lake update`, `run_cmd`, comparator or build.
2. **Dependency version drift:** one Lean toolchain and one Mathlib revision;
   exact SHA and manifest checksum checks must gate every reproducibility run.
3. **Source alteration:** all Git checkouts verify expected origin, head and
   pristine tracked files; compatibility patches require a separate audit.
4. **Challenge/solution confusion:** upstream comparator challenge files use
   `sorry` by design. Never import a challenge as proof authority.
5. **Proof trust:** allow only `propext`, `Quot.sound`, `Classical.choice` for the
   OAI 7/8 bridge, and audit Zeta23 declarations by their own complete policy.
6. **Circular inference:** external 7/8 does not imply a stricter zero-free
   half-plane; a theorem wrapper assuming Step 4 is not a proved closing leaf.
7. **Numerical confusion:** exploratory finite floats and source-altered
   countermodels cannot be promoted into certified universal inequalities.
8. **Resource failure:** huge OpenAI dependency graphs and CI resources can
   time out or exhaust disk. Never reinterpret cancellation or OOM as proof
   failure or success; collect precise receipts and split builds.

## Gate separation

| Gate | Scope | Approval |
|---|---|---|
| Preflight | JSON pins, Python, shell syntax and adversarial local composer | Automatic PR check |
| OAI source | Native Lean nonvanishing transitive closure and exact comparator | Manual/recorded |
| Zeta23 compat | Full source audit, theorem-type/axiom preservation, Round4 native gates | Manual/recorded |
| Cross import | One combined Lean consumer, `#print axioms` | Manual/recorded |
| Full packages | Complete OAI and Zeta23 compilation under unified Mathlib | Explicit dispatch |
| Mathematical bridge | Every relevant new theorem has its own compiler/axiom evidence | Independent review |
| RH closure | New source-specific independent inequality, correct quantifiers and full governed proof checks | Currently OPEN |

The root light GitHub Actions workflow never executes downloaded mathematical
code. After the initial diagnostic OAI run, the heavy workflow is
**manual-dispatch-only** to avoid rerunning the expensive source compilation
on every infrastructure commit. It runs with
`contents:read` and `persist-credentials:false` and uploads source-bound
native logs, exact-source receipts and diagnostics on both success and failure.
The bootstrap-only `leanprover/lean-action` step points to the pinned original
OAI manifest before the unified Lake manifest exists; it does not compile code
or download the Mathlib cache itself. `build.sh` owns dependency resolution and
compile commands after the toolchain is installed. All source runners remain
without repository-write credentials. A larger runner may be needed for full OAI.

A gate receipt in `.bridge/gates/<stage>.json` is emitted **only after** its
native commands succeed and a resolved manifest with the exact pinned Mathlib
revision is available. It records source SHA, compiler, Lake and dependency
fingerprints; it is not a substitute for independently replayed comparator or
for the source-specific OPICA terminal proof acceptance.

## Reproducibility receipts

After a *successful* resolved build, freeze and commit:

- `source-lock.json` and exact upstream Git tree IDs;
- `lake-manifest.json`, all transitive Git SHAs and dependency patch hashes;
- actual Lean, Lake and Mathlib version observations;
- upstream comparator output and permitted-axiom evidence;
- clean build logs for OAI, Zeta23, combined imports and negative controls;
- source-to-theorem mapping for every bridge theorem;
- controlled CI attempt number, job status and artifact digest.

Do **not** commit fake placeholder manifests, mark OPEN proofs PROVED, or
silently change existing Zeta23 PR #298 acceptance contracts. The original
Million Dollar PR remains its own independent verification authority.

## Compatibility-overlay rule

The initial scaffold explicitly refuses `.patch` files in `compat/zeta23/`.
This is intentional. After the first real Lean 4.34.1 compilation identifies
actual compatibility failures, add a reviewed patch applier that verifies
preimage/postimage hashes and exact modified theorem types before accepting
those overlays. Never auto-apply arbitrary user-provided patches from CI.

## License

The bridge scaffold is under Apache-2.0. Both mathematical source trees keep
their own license/NOTICE files. No upstream source is reproduced in the bridge
repository itself. Check the licenses of all OAI transitive dependencies.
