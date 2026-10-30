#!/usr/bin/env python3
"""Record reproducible environment observations without claiming acceptance."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from verify_lock import ROOT, read_and_validate


def git_head(path: Path) -> str | None:
    if not path.exists():
        return None
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path,
                       capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def main() -> None:
    d = read_and_validate()
    oai = ROOT / ".bridge/vendor/oai"
    zeta = ROOT / ".bridge/vendor/zeta23"
    manifest = ROOT / "lake-manifest.json"
    report = {
        "schema": "OPICA_OAI_PROVENANCE_V1",
        "source_lock_sha256": hashlib.sha256((ROOT / "source-lock.json").read_bytes()).hexdigest(),
        "oai_checkout": git_head(oai),
        "zeta_checkout": git_head(zeta),
        "target_oai": d["oai"]["commit"],
        "target_zeta23": d["zeta23"]["commit"],
        "target_mathlib": d["workspace_mathlib"],
        "lake_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest.exists() else None,
        "compiler_success": "NOT_ESTABLISHED_BY_THIS_REPORT",
        "mathematical_acceptance": "NOT_ESTABLISHED_BY_THIS_REPORT",
    }
    dest = ROOT / ".bridge/provenance-report.json"
    dest.parent.mkdir(exist_ok=True, parents=True)
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"PROVENANCE FAILED: {e}", file=sys.stderr)
        sys.exit(1)
