#!/usr/bin/env bash
# Fail-closed native build: write gate receipts only after every required command passes.
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:-smoke}"
case "$mode" in resolve|cache|oai|zeta|smoke|full|axioms) ;; *) echo "Unknown build mode $mode" >&2; exit 2;; esac
mkdir -p .bridge/logs .bridge/gates
log=".bridge/logs/${mode}.log"
: > "$log"
run_logged() {
  printf '\n## ' | tee -a "$log"
  printf '%q ' "$@" | tee -a "$log"
  printf '\n' | tee -a "$log"
  "$@" 2>&1 | tee -a "$log"
}
run_logged python3 scripts/verify_lock.py
run_logged python3 scripts/prepare_workspace.py --offline
command -v lake >/dev/null || { echo 'Lean Lake is not installed. Install elan/Lean 4.34.1 first.' >&2; exit 1; }
command -v lean >/dev/null || { echo 'Lean missing from PATH.' >&2; exit 1; }
run_logged lean --version
run_logged lake --version
# OAI's Lake pre-resolution patch hooks must remain active. Keep our root toolchain.
if [[ "$mode" == "resolve" ]]; then
  run_logged lake update --keep-toolchain
  run_logged python3 scripts/verify_resolution.py
  exit 0
fi
if [[ "$mode" == "cache" ]]; then
  run_logged python3 scripts/verify_resolution.py
  run_logged lake exe cache get
  exit 0
fi
if [[ "${BRIDGE_PRE_RESOLVED:-0}" == "1" ]]; then
  run_logged python3 scripts/verify_resolution.py
elif [[ "${BRIDGE_PRE_RESOLVED:-0}" == "0" ]]; then
  run_logged lake update --keep-toolchain
  run_logged python3 scripts/verify_resolution.py
  run_logged lake exe cache get
else
  echo 'BRIDGE_PRE_RESOLVED must be 0 or 1' >&2
  exit 2
fi
case "$mode" in
  oai) run_logged lake build +OAI.NumberTheory.DirichletL.Nonvanishing ;;
  zeta) run_logged lake build +Zeta23.OPICARound4.PrimeDiscrepancyIntegral ;;
  smoke)
    run_logged lake build +OAI.NumberTheory.DirichletL.Nonvanishing
    run_logged lake build +Zeta23.OPICARound4.PrimeDiscrepancyIntegral
    run_logged lake build +OPICAOAI.Smoke
    ;;
  full)
    run_logged lake build OAI
    run_logged lake build Zeta23
    run_logged lake build OPICAOAI
    ;;
  axioms)
    run_logged lake build +OPICAOAI.Smoke
    lake env lean OPICAOAI/PrintAxioms.lean 2>&1 | tee .bridge/axiom-audit.log | tee -a "$log"
    run_logged python3 scripts/check_axioms.py .bridge/axiom-audit.log
    ;;
esac
run_logged python3 scripts/write_gate_receipt.py "$mode"
run_logged python3 scripts/provenance_report.py
