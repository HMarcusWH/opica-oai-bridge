#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/prepare_workspace.py --offline
for tool in lake comparator landrun lean4export; do
  if ! command -v "$tool" >/dev/null; then
    echo "Comparator prerequisite missing: $tool" >&2
    exit 1
  fi
done
# OAI comparator must be independently rerun from the exact pristine upstream
# package, not accepted merely because the combined bridge file imports it.
(
  cd .bridge/vendor/oai/lean
  lake update --keep-toolchain
  lake exe cache get
  lake env comparator ComparatorChallenges/QuasiRiemannHypothesis.json
)
