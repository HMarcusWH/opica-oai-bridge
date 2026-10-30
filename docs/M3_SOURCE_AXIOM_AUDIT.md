# M3: independent source-axiom proof audit

Status: **READY FOR NATIVE TEST**, not accepted.

The combined smoke consumer references two genuine source declarations and one wrapper:

| Origin | Declaration |
|---|---|
| OpenAI | `OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re` |
| Zeta23 | `Zeta23.OPICARound4.prime_log_abel` |
| Bridge | `OPICAOAI.riemannZeta_ne_zero_above_seven_eighths` |

The M3 `axioms` build must print and validate all three `#print axioms` outputs. Missing, duplicate, unsupported, or `sorryAx` dependencies cause a failure; a declaration with genuinely no axioms is accepted. A stale successful build receipt is deleted at gate startup.

This is not a comparator substitute. Independent comparator replay of OAI's trusted challenge statement, as well as a trusted expected type for the actual bridge and Zeta23 target, are still required for high-assurance proof acceptance. Do not mark M2 or M3 complete from static checks alone.

Source inputs and Lean/Mathlib commits are unchanged. Both upstream repositories remain unmodified. RH and OPICA Step 4 remain OPEN.
