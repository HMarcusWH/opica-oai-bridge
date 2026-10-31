# M2 — Reviewed Zeta23 compatibility overlay (Lean 4.34.1)

**Status: COMPILER CANDIDATE; M2 not accepted until the native rerun succeeds.**

The original M2 run [#41114877082](https://github.com/HMarcusWH/opica-oai-bridge/actions/runs/41114877082) resolved every pinned package and reached Lean. It found four failing source modules, with exact file locations. The original pin is `ebbd787202ce2c67518946fc642af12ff009eaa6`. OpenAI's 7/8 theorem compiled independently twice on the shared `d13f23b7...` Mathlib/Lean 4.34.1 stack.

## What changes

The pristine checkout remains at `.bridge/vendor/zeta23`. The bridge generates `.bridge/overlays/zeta23/Zeta23` and changes the root `Zeta23/` source link to it. Unmodified source modules become symlinks to the exact original. Only the five manifest-listed modules become regular, patched files. `Zeta23.lean` still links to the original facade. Imports retain their original namespaces.

The committed manifest at `compat/zeta23/overlay.json` includes source Git blob SHA, exact replacement anchor and count, and expected output Git blob SHA for each edit. The generator checks every original hash, outputs the expected bytes, and ensures all other source paths remain unmodified links. An unknown source revision, overlay mutation, malformed manifest, new unapproved edit, or unexpected existing overlay fails closed. The manifest SHA is recorded by build receipt and resolution report.

| Module | Lean 4.34 lemma change | Why |
| --- | --- | --- |
| `FromPNTPlus/StrongPNTPrefix.lean` | `Finset.prod_le_prod` → `Finset.prod_le_prod₀` (twice) | Real nonnegative finite products, not unrestricted ordered-multiplication structure |
| `WeilEF/GammaRBracket.lean` | `logDeriv_mul` → `logDeriv_fun_mul` | New function-form logarithmic derivative lemma for lambda functions |
| `Analytic/RectangleLogDeriv.lean` | `logDeriv_mul` → `logDeriv_fun_mul` (twice) | Same explicit-lambda mismatch at two contour residues |
| `CCM/DictionaryArchDiagonal.lean` | `logDeriv_mul` → `logDeriv_fun_mul` (three), `logDeriv_div` → `logDeriv_fun_div` (one) | Function-form product and quotient derivatives |
| `WeilEF/Landau.lean` | `logDeriv_prod` → `logDeriv_fun_prod`; `Finset.prod_le_prod` → `Finset.prod_le_prod₀`; `Finset.prod_le_one` → `Finset.prod_le_one₀` | Function-form finite-product derivative and nonnegative finite-product comparisons |

The replacement lemma names are grounded in the exact pinned Mathlib source: `Mathlib.Algebra.Order.BigOperators.GroupWithZero.Finset` and `Mathlib.Analysis.Calculus.LogDeriv`. All changes are to tactic references, not theorem declarations, definitions, hypotheses, or mathematical statements. The output blob fingerprints were generated from the original pinned Zeta23 files before the PR.

## Native proof acceptance

The overlay generator's static tests do **not** prove Lean compatibility. The M2 branch workflow must resolve all original pinned dependencies, compile `Zeta23.OPICARound4.PrimeDiscrepancyIntegral`, and emit a source-bound receipt listing the overlay hash. If more compiler failures appear, repair them in further reviewed, source-bound manifest revisions; no `sorry`, new `axiom`, axiom relaxation or statement change is allowed. Only after native M2 succeeds may M3 compile a combined OAI/Zeta23 theorem and independently inspect source axioms and expected types. RH and OPICA Step 4 remain OPEN.

Historical `zeta-23-lean` GitHub Actions are unchanged and continue to use their own toolchain.

## First native rerun: four repairs certified, Landau exposed

The reviewed compatibility run [#41155532561](https://github.com/HMarcusWH/opica-oai-bridge/actions/runs/41155532561) compiled all four original broken modules with the bridge overlay, and failed only at the new downstream module `Zeta23.WeilEF.Landau`. The exact compiler errors were the lambda-form `logDeriv_prod` rewrite and finite product inequalities `prod_le_prod` and `prod_le_one`, which changed instance requirements on Lean 4.34's pinned Mathlib. This fifth blob-fingerprinted substitution is grounded in the pinned Mathlib definitions and requires a new complete native build. No theorem declarations or assumptions are changed. M2/M3 remain unaccepted until green native receipts.
