# Build architecture — exact engineering specification

## 1. Why source composition instead of a naive `require OAI`?

A Lake dependency approach is legitimate, but OAI's `lean/lakefile.lean` is not
an ordinary small library. At the pinned commit it declares 30 direct Git
dependencies and implements an `OAI`-package-relative `run_cmd` pre-resolution
patch bootstrap and `post_update` patch verification. Simply mounting it as a
nested package leaves path and patch-resolution behavior to be tested; a third
repo also cannot load two different Mathlib versions simultaneously.

The selected primary mode uses one generated root Lake configuration sourced
from that exact verified OAI file. All 30 original dependency declarations,
configuration code, and patch audit logic are retained. The transform is
strictly textual and checks every expected marker exactly once:

1. `package OAI where` -> `package OPICAOAI where`;
2. Remove *only* `@[default_target]` before `lean_lib OAI`, to avoid building
   the entire upstream mathematical collection for an elementary smoke test;
3. Add `lean_lib Zeta23` and `@[default_target] lean_lib OPICAOAI` declarations.

The original OAI `patches/` directory is projected into the bridge root so that
the existing pre-resolution patch script can locate its exact patch data.
The upstream `require mathlib` must match the locked `d13f23...` revision.
Unexpected changes **stop** preparation rather than getting guessed around.

This mode incorporates both complete source trees but leaves them as Git
checkouts. The bridge generates links, not copies of mathematical modules.
It remains a hypothesis about build compatibility until native `lake` gates pass.

## 2. File ownership

```text
opica-oai-bridge/
  source-lock.json                # authoritative reviewed remote/source pins
  lean-toolchain                  # Lean v4.34.1
  lakefile.lean                   # GENERATED, ignored; OAI config + Zeta + bridge
  lake-manifest.json              # resolved dependency lock (commit after pass)
  .bridge/vendor/oai/             # ignored, pinned HMarcusWH/math checkout
  .bridge/vendor/zeta23/          # ignored, pinned Zeta23 PR298 checkout
  OAI/ -> .bridge/vendor/oai/lean/OAI
  OAI.lean -> .bridge/vendor/oai/lean/OAI.lean
  ComparatorChallenges/ -> .bridge/vendor/oai/lean/ComparatorChallenges
  patches/ -> .bridge/vendor/oai/lean/patches
  Zeta23/ -> .bridge/vendor/zeta23/Zeta23
  Zeta23.lean -> .bridge/vendor/zeta23/Zeta23.lean
  OPICAOAI/Smoke.lean             # first genuine dual-import theorem
  OPICAOAI/PrintAxioms.lean       # permitted-axiom audit
  compat/zeta23/                 # reviewed Lean4.34 compatibility patches only
  compat/oai/                    # upstream config compatibility notes
  scripts/                       # preparation, build, comparator, pin and audit
  tests/                         # no-network preflight / adversarial tests
  .github/workflows/             # light PR preflight, manually triggered build
  docs/                           # source, proof and production contracts
  research/                       # open obligations, work-package registry
```

## 3. Root package and toolchain

`OPICAOAI` is the only root package. It exposes original `OAI` and `Zeta23`
modules unchanged by name, plus new `OPICAOAI` adapters. It inherits OAI's
entire declared dependency graph from the pinned upstream Lake config, which
also includes the single locked Mathlib revision. Original Zeta23's `lakefile.toml`
is retained for provenance but not evaluated as a competing root manifest.

Lean is **4.34.1** for the entire build. Zeta23 at the pinned PR #298 revision
was authored for **4.33.0-rc2** and a different Mathlib. All compiler and
library repairs must occur in an independent compatibility overlay, with a
complete diff review, before M2 can pass. No fallback to unproved theorem
constants is permitted. If compatibility is too invasive, a separate Zeta23
compatibility branch can replace the local overlay, but must be pinned to a
new exact SHA and preserve theorem types and axiom dependencies.

## 4. Exact source integrity

The preparation procedure checks full 40-character commits, exact remotes,
clean tracked source trees, original `lakefile.lean` and `lakefile.toml` Git
blob hashes, expected OAI patch hooks, toolchain pin and Mathlib pin. It fails
on unknown source revisions or hand-edited generated Lake code.

The verification report separately records observed source checkouts,
source-lock digest, resolved manifest digest, and explicitly **does not**
assert mathematical acceptance. A human-approved update changes the lock and
its static regression tests in one reviewed PR.

## 5. Supported build target progression

```bash
python3 scripts/prepare_workspace.py
bash scripts/build.sh oai
bash scripts/build.sh zeta
bash scripts/build.sh smoke
bash scripts/build.sh axioms
bash scripts/verify_comparator.sh
bash scripts/build.sh full
```

Use `lake build +Module.Name` for narrow prerequisites, not the root OAI
default target. `full` is the costly, explicitly invoked package build.
The source-specific comparator must be rerun independently from the pinned
original OAI workspace, with `comparator`, `landrun` and `lean4export`
installed and exact comparator configuration verified.

## 6. Fallback package-dependency experiment

If source composition is blocked by a reproducible Lake error, create an
*independent*, isolated experiment using direct dependencies instead:

```toml
[[require]]
name = "OAI"
git = "https://github.com/HMarcusWH/math.git"
rev = "4eaee87548250b2682affda7d05d947c05554bae"
subDir = "lean"

[[require]]
name = "Zeta23"
git = "https://github.com/HMarcusWH/zeta-23-lean.git"
rev = "<verified Lean4.34-compatible commit>"
```

This is a *comparison design*, not an installed second Lake configuration. It
requires a tested solution for OAI's package-relative patch hooks and one
harmonized mathlib pin. Do not silently switch modes or use an unverified SHA.

## 7. Limits

The bootstrap code cannot certify Lean compatibility without Lean and the full
Git objects available on the host. A generated Lake file, static test pass, or
green preflight is not an OAI proof replay or a Zeta23 terminal certificate.
