import OAI.NumberTheory.DirichletL.Nonvanishing
import OAI.NumberTheory.DirichletL.Continuation
import Zeta23.OPICARound4.PrimeDiscrepancyIntegral

/-!
# Combined import smoke test

The theorem below is deliberately a direct application of OpenAI's published
Lean theorem, not an assertion of an OPICA-specific analytic improvement.
-/
namespace OPICAOAI

/-- Exact re-use of the 7/8 nonvanishing theorem in the combined workspace. -/
theorem riemannZeta_ne_zero_above_seven_eighths
    {s : ℂ} (hs : (7 / 8 : ℝ) < s.re) : riemannZeta s ≠ 0 :=
  OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re hs

#check OAI.SevenEighths.Continuation.nonzero_of_common_signal
#check Zeta23.OPICARound4.prime_log_abel

end OPICAOAI
