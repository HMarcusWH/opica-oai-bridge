#!/usr/bin/env python3
"""Validate Lake resolution against pinned sources. Never assert proof acceptance."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from prepare_workspace import VENDOR_DIRS, assert_git_checkout
from verify_lock import ROOT, read_and_validate
from write_gate_receipt import validate_manifest

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check_resolution(*, root: Path = ROOT, verify_git: bool = True) -> dict:
    data = read_and_validate(root)
    evidence = json.loads((root / ".bridge/prepare-evidence.json").read_text(encoding="utf-8"))
    if evidence.get("schema") != "OPICA_OAI_PREPARE_EVIDENCE_V1":
        raise ValueError("Missing exact source preparation evidence")
    for section, evidence_field in (("oai", "oai_head"), ("zeta23", "zeta23_head")):
        if evidence.get(evidence_field) != data[section]["commit"]:
            raise ValueError(f"Prepared {section} source does not match lock")
        if verify_git:
            assert_git_checkout(root / VENDOR_DIRS[section],
                                data[section]["commit"], data[section]["repo"])
    if evidence.get("mathlib_target") != data["workspace_mathlib"]:
        raise ValueError("Prepared Mathlib source lock mismatch")
    lake_path = root / "lakefile.lean"
    if digest(lake_path) != evidence.get("generated_lake_sha256"):
        raise ValueError("Generated Lake configuration changed after preparation")
    manifest_path = root / "lake-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, data["workspace_mathlib"])
    packages = manifest["packages"]
    if len({p.get("name") for p in packages}) != len(packages):
        raise ValueError("Duplicate resolved package names")
    return {
        "schema": "OPICA_OAI_RESOLUTION_REPORT_V1",
        "stage": "DEPENDENCY_RESOLVED_NOT_COMPILED",
        "source_lock_sha256": digest(root / "source-lock.json"),
        "generated_lake_sha256": digest(lake_path),
        "manifest_sha256": digest(manifest_path),
        "mathlib_commit": data["workspace_mathlib"],
        "oai_commit": data["oai"]["commit"],
        "zeta23_commit": data["zeta23"]["commit"],
        "resolved_packages": len(packages),
        "native_proof_compiled": False,
        "step4_proved": False,
    }

def main() -> None:
    report = check_resolution()
    dest = ROOT / ".bridge/resolution-report.json"
    dest.parent.mkdir(exist_ok=True, parents=True)
    dest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("DEPENDENCY RESOLUTION VALIDATED (not a proof):", json.dumps(report))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"RESOLUTION VALIDATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
