#!/usr/bin/env python3
"""Write a source-bound receipt only after a native build command has succeeded.

This receipt does not certify the underlying mathematics or theorem provenance.
It records the toolchain and transitive Mathlib pin for independent review.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from verify_lock import ROOT, read_and_validate
from prepare_workspace import VENDOR_DIRS, assert_git_checkout

VALID_STAGES = {"oai", "zeta", "smoke", "axioms", "full"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tool_version(name: str) -> str:
    result = subprocess.run([name, "--version"], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    return (result.stdout or result.stderr).strip().splitlines()[0]


def validate_manifest(manifest: dict, mathlib_rev: str) -> None:
    packages = manifest.get("packages")
    if not isinstance(packages, list):
        raise ValueError("Missing resolved packages in Lake manifest")
    mathlib = [x for x in packages if x.get("name") == "mathlib"]
    if len(mathlib) != 1 or mathlib[0].get("rev") != mathlib_rev:
        raise ValueError("Resolved Mathlib is not the approved source lock revision")
    for p in packages:
        if p.get("type") == "git" and not p.get("rev"):
            raise ValueError(f"Unpinned git dependency in manifest: {p.get('name')}")


def receipt(stage: str, *, root: Path = ROOT,
            lean_version: str | None = None,
            lake_version: str | None = None) -> dict:
    if stage not in VALID_STAGES:
        raise ValueError(f"Invalid native gate: {stage}")
    data = read_and_validate(root)
    evidence_path = root / ".bridge/prepare-evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if (evidence.get("oai_head") != data["oai"]["commit"] or
            evidence.get("zeta23_head") != data["zeta23"]["commit"] or
            evidence.get("mathlib_target") != data["workspace_mathlib"]):
        raise ValueError("Source preparation evidence mismatch")
    for key, rel in VENDOR_DIRS.items():
        assert_git_checkout(root / rel, data[key]["commit"], data[key]["repo"])
    manifest_path = root / "lake-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, data["workspace_mathlib"])
    return {
        "schema": "OPICA_OAI_NATIVE_GATE_RECEIPT_V1",
        "gate": stage,
        "gate_command": f"bash scripts/build.sh {stage}",
        "command_exit": 0,
        "source_lock_sha256": sha256(root / "source-lock.json"),
        "lake_manifest_sha256": sha256(manifest_path),
        "generated_lake_sha256": sha256(root / "lakefile.lean"),
        "oai_commit": data["oai"]["commit"],
        "zeta23_commit": data["zeta23"]["commit"],
        "mathlib_commit": data["workspace_mathlib"],
        "lean_version": lean_version or tool_version("lean"),
        "lake_version": lake_version or tool_version("lake"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "independent_comparator": "NOT_ESTABLISHED_BY_THIS_RECEIPT",
        "mathematical_acceptance": "NOT_ESTABLISHED_BY_THIS_RECEIPT",
        "rh_status": "OPEN",
        "step4_status": "OPEN",
    }


def main() -> None:
    stage = sys.argv[1]
    r = receipt(stage)
    path = ROOT / ".bridge/gates" / f"{stage}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"NATIVE BUILD RECEIPT: {path} (not independent acceptance)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"NATIVE GATE RECEIPT REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)
