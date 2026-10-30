/-
Copyright (c) 2026 Marcus Hermansson.
Released under Apache 2.0 as described in the file LICENSE.
-/
import OAI.NumberTheory.DirichletL.Nonvanishing
import Zeta23.OPICAFollowup.NativeWindowRate
import Mathlib.Tactic

/-!
# The pinned 7/8 theorem on the *actual* Zeta23 zero configuration

No new zero object, analytic assumption, arithmetic source or rightmost zero
is introduced. This module composes the exact OpenAI nonvanishing theorem with
Zeta23's existing zetaZeroConfig and nativeZeroDisplacementSup.

STATUS: SOURCE CANDIDATE. Requires native Lean 4.34.1 compatibility and a
successful cross-library compiler/axiom audit before it is an accepted proof.
RH and Step 4 remain open.
-/

noncomputable section
open Filter
open scoped Topology

namespace OPICAOAI

/-- A genuine Zeta23 nontrivial zeta zero lies at or to the left of 7/8. -/
theorem actual_zeta_zero_re_le_seven_eighths
    (ρ : Zeta23.zetaZeroConfig.carrier) :
    (ρ : ℂ).re ≤ (7 / 8 : ℝ) := by
  by_contra h
  have hgt : (7 / 8 : ℝ) < (ρ : ℂ).re := lt_of_not_ge h
  have hz : riemannZeta (ρ : ℂ) = 0 := ρ.property.1
  exact (OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re hgt) hz

/-- The known 1-s symmetry of the actual zero set gives the left bound. -/
theorem actual_zeta_zero_re_ge_one_eighth
    (ρ : Zeta23.zetaZeroConfig.carrier) :
    (1 / 8 : ℝ) ≤ (ρ : ℂ).re := by
  have href : Zeta23.IsNontrivialZero (1 - (ρ : ℂ)) :=
    Zeta23.zeta_one_sub_zero ρ.property
  have hbound : (1 - (ρ : ℂ)).re ≤ (7 / 8 : ℝ) := by
    by_contra h
    have hgt : (7 / 8 : ℝ) < (1 - (ρ : ℂ)).re := lt_of_not_ge h
    exact (OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re hgt) href.1
  have hreal : (1 - (ρ : ℂ)).re = 1 - (ρ : ℂ).re := by simp
  linarith

/-- The actual Zeta23 zero-displacement scalar is at most 3/8.
The supremum need not be attained. -/
theorem native_zero_displacement_sup_le_three_eighths :
    Zeta23.OPICAFollowup.nativeZeroDisplacementSup ≤ (3 / 8 : ℝ) := by
  by_contra h
  have hgt : (3 / 8 : ℝ) <
      Zeta23.OPICAFollowup.nativeZeroDisplacementSup := lt_of_not_ge h
  obtain ⟨ρ, hρ⟩ :=
    Zeta23.OPICAFollowup.native_zero_sup_bounds.2.2.2
      (3 / 8 : ℝ) (by norm_num) hgt
  have hupper := actual_zeta_zero_re_le_seven_eighths ρ
  linarith

/-- Consequence for the *fixed original* prime field and literal real terminal
windows. This is an eventually-valid 3/8+epsilon envelope, not an improvement
below the OpenAI zero-free line and not an independent Step 4 upper. -/
theorem native_fixed_window_rate_eventually_lt_three_eighths_add
    (d : ℕ) (C ε : ℝ) (hC : 1 < C) (hε : 0 < ε) :
    ∀ᶠ T : ℝ in atTop,
      Zeta23.OPICAFollowup.nativeWindowLogRate d C T <
        (3 / 8 : ℝ) + ε := by
  have hrate :
      Tendsto (fun T : ℝ => Zeta23.OPICAFollowup.nativeWindowLogRate d C T)
        atTop (𝓝 Zeta23.OPICAFollowup.nativeZeroDisplacementSup) :=
    Zeta23.OPICAFollowup.NativeWindowProof.Asymptotic.fixedSource_continuous_window_rate d hC
  have hmargin :
      Zeta23.OPICAFollowup.nativeZeroDisplacementSup <
        (3 / 8 : ℝ) + ε := by
    linarith [native_zero_displacement_sup_le_three_eighths]
  exact (tendsto_order.1 hrate).2 ((3 / 8 : ℝ) + ε) hmargin

#print axioms native_zero_displacement_sup_le_three_eighths
#print axioms native_fixed_window_rate_eventually_lt_three_eighths_add

end OPICAOAI
