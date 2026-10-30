# M5 candidate: exact OAI 7/8 -> Zeta23 native displacement

**Stage:** SOURCE CANDIDATE; native Lean compilation is pending M1/M2/M3.
**Original source pins:** OAI `4eaee87548250b2682affda7d05d947c05554bae`; Zeta23 `ebbd787202ce2c67518946fc642af12ff009eaa6`.
**Proof authority:** none until a clean native compile and independent axiom/comparator checks.

## Source-exact imports

- `OAI.NumberTheory.DirichletL.Nonvanishing`: `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re`, proving `riemannZeta s ≠ 0` for `7/8 < s.re`.
- `Zeta23.Statement.SeamClosed`, transitively through `Zeta23.OPICAFollowup.NativeWindowRate`: `zetaZeroConfig.carrier` is exactly the genuine nontrivial zeta-zero subtype (not a new abstract zero population).
- `Zeta23.ZetaReflect`, transitively: `zeta_one_sub_zero` gives actual 1−s symmetry.
- `Zeta23.OPICAFollowup.NativeExplicitFormula`: `nativeZeroDisplacementSup` is the supremum of `insert 0 (range (max (Re ρ − 1/2) 0))`. `native_zero_sup_bounds` gives the strict supremum selection theorem without assuming a maximum.
- `Zeta23.OPICAFollowup.NativeWindowRate`: `NativeWindowProof.Asymptotic.fixedSource_continuous_window_rate` proves convergence of the native fixed-source rate to that literal supremum.

## New attempted Lean results

1. Right-side zero bound `Re ρ ≤ 7/8` on Zeta23's actual zero subtype, by direct application of OAI nonvanishing and `ρ.property.1`.
2. Left-side zero bound `Re ρ ≥ 1/8` via Zeta23's proven 1−ρ zero involution.
3. `nativeZeroDisplacementSup ≤ 3/8`, using Zeta23's own strict-supremum selection theorem and the OAI right-side bound; no rightmost zero assumed.
4. For every fixed original native source order d, fixed C>1 and epsilon>0, the physical terminal-window logarithmic rate is eventually below `3/8 + epsilon`, by the already-proved Zeta23 limit and the new Theta bound.

This is a composition of existing mathematics, **not** a new zero-free region, and **not** a Step 4 contradiction.

## Acceptance steps

- First qualify M1 (OAI) and M2 (Zeta23) using one compatible Lean/Mathlib environment.
- Execute `lake build +OPICAOAI.ZeroDisplacementBridge` after the merged-environment smoke.
- Check exact theorem types and the `#print axioms` output, excluding `sorryAx`, `native_decide` and any unapproved axiom.
- Run independent expected-type consumer / comparator on the new bridge declarations.
- Keep this module separate from Step 4 terminal consumers until accepted.
- Do not claim the 7/8 theorem automatically proves any independent Chebyshev bound, source-selected variation bound, or zero-free extension below 7/8.
