# Reviewed Zeta23 Lean 4.34.1 compatibility overlay

`overlay.json` is a source-pinned patch specification. The generator at
`scripts/apply_zeta23_overlay.py` creates `.bridge/overlays/zeta23/Zeta23/`
without changing `.bridge/vendor/zeta23` or the original Git repository.

Each edited file carries the original Git blob SHA, an exact replacement
anchor and count, and the Git blob SHA of the expected result. Everything
else is linked unchanged. The active source link `Zeta23/` points to the
overlay, while `Zeta23.lean` still points to the original facade.

Reviewed fixes (first four native-compiled in run #41155532561; fifth pending):

1. `StrongPNTPrefix`: use `Finset.prod_le_prod₀`, the nonnegative product
   theorem in the pinned Mathlib, instead of `Finset.prod_le_prod`.
2. `GammaRBracket`: use function-form `logDeriv_fun_mul`.
3. `RectangleLogDeriv`: use function-form `logDeriv_fun_mul`.
4. `DictionaryArchDiagonal`: use `logDeriv_fun_mul` and `logDeriv_fun_div`.
5. `WeilEF/Landau`: use `logDeriv_fun_prod`, `Finset.prod_le_prod₀`, and `Finset.prod_le_one₀`.

These substitutions adjust tactic lemma selection, not theorem declarations.
The expected resulting blobs were computed from the exact pinned source;
they are not Lean compiler receipts. This compatibility proposal must pass
native M2, combined M3 and an axiom audit before being accepted.

Do not edit the generated overlay in place; update the reviewed manifest and
expected hashes instead. An existing unexplained overlay fails closed.
