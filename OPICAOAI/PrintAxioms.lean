import OPICAOAI.Smoke

/-!
# Full source-level dependency audit for the combined bridge

Audits source declarations independently, rather than checking only a wrapper
that happens to import both libraries. These lines are not axioms or proofs;
they emit kernel-traced dependency reports which scripts/check_axioms.py
requires in the source-bound M3 gate.
-/

#print axioms OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re
#print axioms Zeta23.OPICARound4.prime_log_abel
#print axioms OPICAOAI.riemannZeta_ne_zero_above_seven_eighths
