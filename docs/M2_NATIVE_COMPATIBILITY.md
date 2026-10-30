# M2 — First original Zeta23 compilation under unified Lean 4.34.1

**Status: UNVERIFIED until a source-bound native build receipt exists.**

The pinned Zeta23 source at `ebbd787202ce2c67518946fc642af12ff009eaa6` was written against Lean `v4.33.0-rc2` and Mathlib `51e6992e...`. The unified bridge uses Lean `v4.34.1` and Mathlib `d13f23b7...`, exactly as required by the pinned OpenAI 7/8 proof.

## What this diagnostic does

A separate GitHub Actions workflow runs the original Zeta23 module `Zeta23.OPICARound4.PrimeDiscrepancyIntegral` in the same source-composition workspace used for OAI. It does not modify or patch the original sources.

The workflow is automatically triggered once when its file is installed on the main branch; future executions are manually dispatchable. It uses the existing serial `full-bridge-build` concurrency group, so it does not compete with an OAI build currently running.

Stages are separately timed and logged: source verification, dependency resolution (120 minutes), Mathlib cache retrieval (25 minutes), and original Zeta23 compilation (170 minutes), all under the 330-minute GitHub Actions job limit.

## Decision tree

- **Compile succeeds:** M2 earns a source-bound native build receipt for the specified original module; still check the broader Zeta23 theorem inventory and comparator before accepting full M2.
- **Compile fails due to changed Mathlib/Lean API:** record exact first failing declaration and import chain, then apply narrowly reviewed compatibility changes on a separate branch. Never add a missing axiom, `sorry`, or replace a theorem type.
- **Compile fails due to root package resolution/patches:** treat it as infrastructure and fix the bridge build, not the mathematics.
- **Timeout:** preserve logs and exact resolutions; replan the job using reproducible cache/build boundaries without weakening source locks.

The M2 job does **not** establish RH, Step 4, the OpenAI comparator, or a combined OAI+Zeta23 proof. Its first aim is to identify a real compilation result on the original Zeta23 source tree.
