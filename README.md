# OPICA × OpenAI Mathematical Bridge

> **Status:** bootstrap/source-composition scaffold. **RH: OPEN. Step 4: OPEN.**
>
> A checked import of two modules is **not** a new zeta theorem. All original
> source hashes, physical metrics, source-specific quantifiers, and open proof
> obligations must survive integration.

The repository composes two independently versioned, complete Lean source trees:

- [HMarcusWH/math](https://github.com/HMarcusWH/math) at pinned OpenAI-derived commit `4eaee87548250b2682affda7d05d947c05554bae` (upstream [openai/math](https://github.com/openai/math));
- [HMarcusWH/zeta-23-lean](https://github.com/HMarcusWH/zeta-23-lean) at pinned Round 4 PR #298 commit `ebbd787202ce2c67518946fc642af12ff009eaa6`.

Both are incorporated by local **read-only-in-intent pinned Git checkouts**, not by
copying or rewriting thousands of mathematical source files. The workspace
generates one Lake configuration from the exact verified OpenAI `lakefile.lean`,
retaining all 30 declared Git dependencies and its special dependency-patch hooks.
The source trees are projected into one namespace-preserving workspace using
symlinks. No external runtime theorem is postulated as an axiom.

## Start (Linux or WSL2)

Install Git, Python 3.11+, elan / Lean (`leanprover/lean4:v4.34.1`), and sufficient
build resources. The complete OAI dependency graph is large; prefer an ample
local SSD and memory. **Windows native is not the supported first build target.**

```bash
python3 scripts/verify_lock.py
python3 -m unittest discover -s tests -v
python3 scripts/prepare_workspace.py   # requires GitHub connectivity, pinned checkouts
bash scripts/build.sh oai                # OAI nonvanishing closure
bash scripts/build.sh zeta               # Zeta23 Round 4 compatibility gate
bash scripts/build.sh smoke              # cross-import proof; requires both earlier gates
bash scripts/build.sh axioms             # permitted-axiom audit
bash scripts/build.sh full               # full OAI and Zeta23 library build (costly)
```

The Zeta23 source is originally on Lean 4.33.0-rc2 and needs an audited
compatibility migration to compile with Lean 4.34.1; **that gate is still OPEN**.
The prepare script does not modify any tracked source files, does not insert
`sorry`, and fails closed on unexpected upstream configuration or source drift.

After successful Lake resolution, commit `lake-manifest.json` with the source
lock and verification evidence. A manifest is not pre-generated or fabricated.

## Relevant documentation

- [Build architecture and exact source wiring](docs/ARCHITECTURE.md)
- [Full build, bootstrap and acceptance plan](docs/BUILD_PLAN.md)
- [Mathematical integration work packages](docs/MATH_WORKPACKAGES.md)
- [Security, provenance and acceptance](docs/SECURITY_ACCEPTANCE.md)
- [Machine-readable open obligations](research/OPEN_OBLIGATIONS.json)
- [Milestone graph](research/MILESTONES.json)

## Important separation

OAI's theorem `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` is a genuine
external theorem under its own checked dependencies. Its comparator challenge
is *not* a proof file and deliberately contains `sorry`. The complete proof is
in `OAI/NumberTheory/DirichletL/Nonvanishing.lean` and its transitive imports.

OPICA's deep detector, common-cutoff two-parity packet, and native causal target
are different mathematical states unless a bridge explicitly identifies them.
The existing missing closing estimate (`C_DIRECT` or alternatives) cannot be
introduced through a source assumption, an axiom, or a dependency update.

## License and attribution

The bridge's original scaffold is Apache-2.0. Imported Git checkouts keep their
original licenses and attribution. OpenAI mathematics is Apache-2.0 licensed;
verify and preserve each transitive dependency's license independently.
See [NOTICE.md](NOTICE.md).

## Native build receipts and diagnostic artifacts

`make oai`, `make zeta`, `make smoke`, `make axioms`, and `make all` stream their
actual Lake logs into `.bridge/logs/<stage>.log`. **Only after each gate succeeds**
will a `.bridge/gates/<stage>.json` receipt be produced with observed Lean/Lake
versions, original source heads, and the checked Mathlib manifest SHA. The
native CI workflow uploads these records even when a command fails.

The OAI-only gate is automatically queued when the heavy workflow itself changes
on the `main` branch. Other expensive stages remain explicit manual workflows.
No successful preflight or native build receipt upgrades the OPEN RH/Step 4
mathematical status.
