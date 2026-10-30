# Mathematics work packages — source-faithful integration plan

**Scientific boundary:** RH OPEN; Step 4 OPEN. Every new mathematical result
must carry its original source and proof dependencies into a kernel-checked
consumer; no external theorem may be represented by an opaque `axiom` or a
`noncomputable def` masquerading as a proof.

## W1 — OAI 7/8 theorem interface

- Actual declaration: `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re`.
- File: `OAI/NumberTheory/DirichletL/Nonvanishing.lean`, *not* the `sorry`
  declaration in `ComparatorChallenges/QuasiRiemannHypothesis.lean`.
- Preserve strict inequality `7/8 < s.re`, no claim at `7/8`.
- Produce a real bridge proof using that declaration and record `#print axioms`.
- Independently rerun the upstream comparator and required kernel verification.
- Acceptance: one genuine combined import with no additional axioms.

## W2 — Zero configuration and exact displacement

- Derive a proof-level correspondence between `Zeta23`'s actual
  `zetaZeroConfig.carrier` and Mathlib `riemannZeta s = 0`.
- Verify the precise spectral range and zeta functional equation/reflection
  symmetry needed to handle both sides of the critical line.
- Then derive the intended bound `Theta <= 3/8` for the exact native
  `nativeZeroDisplacementSup`, not for an unrelated placeholder supremum.
- Use Paper X's rate theorem only through its exact Lean declaration and its
  stated fixed-order hypotheses; do not infer endpoint damping.
- Acceptance: no extra or silently strengthened zero-domain assumptions.

## W3 — Chebyshev / prime-discrepancy interface

- Prove the classical analytic implication `psi(x)-x = O_eps(x^(7/8+eps))`
  in the exact Mathlib Chebyshev normalization, with all range and epsilon
  quantifiers. This **does not** follow from importing OAI's nonvanishing
  statement by `simp`: explicit-formula/complex-analysis work is necessary.
- Import `Zeta23.OPICARound4.PrimeDiscrepancyIntegral.prime_log_abel` and the
  actual corrected test from `SourceDiscrepancy.lean`.
- Preserve all von Mangoldt prime powers, endpoints, `F'(y)-F(y)/2`, the
  archimedean remainder and the actual `(L,K,u)` parameter dependence.
- Obtain the weighted bound against `exp((3/8+eps)y)` but do not imply it
  provides the independent variation control for the selected ground.
- Acceptance: sign, normalization, and every prime-power seam audited.

## W4 — Common-signal continuation

- Port and generalize the OAI `Continuation.lean` mechanism, retaining the
  actual theorem hypotheses: Mellin local integrability, rapid decay at zero,
  polynomial growth, analytic factors, nonzero multiplier, and identity on
  the common initial half-plane.
- The existing OAI statement's margin cannot continue below 7/8 because
  `continuation_boundary_gt` forces that inequality. Reuse the pattern,
  never assert the original theorem itself improves the 7/8 region.
- Acceptance: independent Lean proof with a clearly parameterized signal
  exponent and no borrowed step-4 saving.

## W5 — Source-preserving Möbius echo

- Use the genuine causal target `v` from the fixed OPICA construction.
- Define the locally finite history
  `M_v(t) = sum_(n<=exp t) mu(n)/sqrt(n) * v(t-log n)` with causal domain.
- Prove the Laplace identity `LM_v(z) = V(z)/zeta(1/2+z)` first only where
  absolute convergence and divisor inversion are justified.
- Prove source visibility `V(p) != 0` at a hypothetical right-of-line zero
  with the actual OPICA result, handling multiplicity.
- OPEN: independently prove a uniform terminal bound that extends the
  reciprocal into a smaller half-plane. Do not smuggle it in as a lemma.
- Acceptance: exact history, source and transforms, no surrogate test.

## W6 — Align the two OPICA packet tracks

- **Deep detector:** generated quartic smooth trial, `N=ceil(L^4)`, selected
  predecessor and shift, and the actual `smoothSourceMain` expression.
- **Common cutoff:** actual physical even/odd matrices, shared `(L,K)`,
  negative ground alternatives including tie, genuine odd adjoint and metric.
- Never identify the two tracks without a proven map of construction,
  aperture, cutoff, physical Hilbert metric, shift and selected source.
- The corrected source ray `S(r)=1` is not a unit-Hilbert-norm condition.
- Acceptance: explicit adapters only; no retrospective packet mixing.

## W7 — Step 4 contradiction candidates

- **First:** `C_DIRECT`: under a hypothetical zero, the original actual
  smooth trial has `Re W(g_L,g_L) <= -4 exp(beta*L)`. The missing independent
  estimate is `Re W(g_L,g_L) >= -C exp(eps*L)` with eps < beta on the same
  sufficiently late generated packet, with correct quantifier order.
- **Second:** `C_SMOOTH_SCHUR`: an independent upper for the complete
  `Re<G_sm,P^-1 G_sm> - Re W(g,g) - eta||g||^2`, using the actual inverse,
  full signed prime/pole/archimedean source, and shifted mass.
- **Third:** independent causal echo saving or approved signed observation
  alternative, preserving history and noncommuting source selections.
- Registration in research JSON does not prove any leaf; a checked bridge
  theorem can discharge a leaf only when the actual types and proof are present.
- Acceptance: full independent arithmetic closing proof, not a circular
  restatement of RH or Weil positivity.

## W8 — Adversarial numerical and theorem controls

- Retain the audit's genuine K=3..5 finite matrix cases and physical metrics
  as optional *numerical* regression, not a source of infinite sign claims.
- Retain modified non-zeta q=2 negative-two-parity countermodel: rank-one
  transport is not by itself a source-blind negative-index cap.
- Retain genuinely sign-changing K=5 source discrepancy checks: generic
  source selected signs are not universal.
- Verify large-K/aperture quantifiers and source-only envelopes rather than
  promoting positive finite samples to a proof.
- Acceptance: numeric work is labeled exploratory unless interval-certified;
  no numerical result is used as an analytic inequality for all apertures.

## Proposed modules after bootstrap compatibility is established

```text
OPICAOAI/ZeroConfiguration.lean
OPICAOAI/ZeroDisplacement.lean
OPICAOAI/NativeWindowRates.lean
OPICAOAI/ChebyshevExplicitFormula.lean
OPICAOAI/PrimeDiscrepancyBound.lean
OPICAOAI/Continuation/Core.lean
OPICAOAI/Continuation/SourceSignal.lean
OPICAOAI/MobiusEcho/Definition.lean
OPICAOAI/MobiusEcho/LaplaceIdentity.lean
OPICAOAI/MobiusEcho/SourceVisibility.lean
OPICAOAI/DetectorPacket/SourceAlignment.lean
OPICAOAI/Step4/DirectWeilUpper.lean
OPICAOAI/Step4/SmoothSchurUpper.lean
OPICAOAI/Step4/CausalClosure.lean
OPICAOAI/Step4/Consumers.lean
```

These are **work packages, not files with placeholder `sorry` proofs**. Add a
module only when its definitions/hypotheses and proof obligations are finalized;
keep open propositions in machine-readable research contracts, not as axioms.

## M5 source-bound bridge candidate (pending native verification)

Draft PR #3 adds `OPICAOAI/ZeroDisplacementBridge.lean` with the exact
OAI 7/8 theorem on Zeta23's actual `zetaZeroConfig` and its named
`nativeZeroDisplacementSup` scalar. It also consumes the genuine fixed-source
terminal-window limit. `make zero` / manual `zero` CI stage builds and audits
those new theorem declarations (after M1-M3). These sources are **UNACCEPTED**
until the unified Lean build, exact types and permitted-axiom checks succeed;
`C_DIRECT` and Step 4 remain OPEN. See `M5_ZERO_DISPLACEMENT_CANDIDATE.md`.
