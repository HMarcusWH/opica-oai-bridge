#!/usr/bin/env bash
# Run after source preparation. Never changes an upstream repository or asserts Step 4.
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:-smoke}"
case "$mode" in oai|zeta|smoke|full|axioms) ;; *) echo "Unknown build mode $mode" >&2; exit 2;; esac
python3 scripts/verify_lock.py
python3 scripts/prepare_workspace.py --offline
command -v lake >/dev/null || { echo 'Lean Lake is not installed. Install elan/Lean 4.34.1 first.' >&2; exit 1; }
command -v lean >/dev/null || { echo 'Lean missing from PATH.' >&2; exit 1; }
lean --version
lake --version
# Preserve the project toolchain. The OAI Lake configuration has a custom
# dependency bootstrap and patch ledger: never bypass its configuration stage.
lake update --keep-toolchain
lake exe cache get
case "$mode" in
 oai) lake build +OAI.NumberTheory.DirichletL.Nonvanishing ;;
 zeta) lake build +Zeta23.OPICARound4.PrimeDiscrepancyIntegral ;;
 smoke)
   lake build +OAI.NumberTheory.DirichletL.Nonvanishing
   lake build +Zeta23.OPICARound4.PrimeDiscrepancyIntegral
   lake build +OPICAOAI.Smoke
   ;;
 full)
   lake build OAI
   lake build Zeta23
   lake build OPICAOAI
   ;;
 axioms)
   lake build +OPICAOAI.Smoke
   lake env lean OPICAOAI/PrintAxioms.lean | tee .bridge/axiom-audit.log
   python3 scripts/check_axioms.py .bridge/axiom-audit.log
   ;;
esac
python3 scripts/provenance_report.py
