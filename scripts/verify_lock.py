#!/usr/bin/env python3
"""Static, network-free source pin validation. Never resolves moving branches."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHA = re.compile(r"^[0-9a-f]{40}$")
EXPECTED = {
    "schema": "OPICA_OAI_SOURCE_LOCK_V1",
    "lean_toolchain": "leanprover/lean4:v4.34.1",
    "workspace_mathlib": "d13f23b723b8a846827a245b89c10fc7d3f11612",
    "oai_repo": "https://github.com/HMarcusWH/math.git",
    "oai_commit": "4eaee87548250b2682affda7d05d947c05554bae",
    "oai_lakefile_blob": "cd24ca2ee09fb6fe33e82400534d9e60a616125b",
    "zeta_repo": "https://github.com/HMarcusWH/zeta-23-lean.git",
    "zeta_commit": "ebbd787202ce2c67518946fc642af12ff009eaa6",
    "zeta_lakefile_blob": "a0b94fc92bf5bd94cbdcedab56a3673b399f1a29",
}


def validate_lock(data: dict, toolchain: str) -> None:
    if data.get("schema") != EXPECTED["schema"]:
        raise ValueError("Unexpected lock schema")
    if data.get("lean_toolchain") != EXPECTED["lean_toolchain"]:
        raise ValueError("Unexpected Lean toolchain")
    if toolchain.strip() != data["lean_toolchain"]:
        raise ValueError("lean-toolchain does not match source-lock.json")
    if data.get("workspace_mathlib") != EXPECTED["workspace_mathlib"]:
        raise ValueError("Mathlib revision drift; needs a reviewed lock update")
    for part in ("oai", "zeta23"):
        if part not in data or not isinstance(data[part], dict):
            raise ValueError(f"Missing {part} repository record")
        repo = data[part]
        if repo.get("repo") != EXPECTED[f"{part if part != 'zeta23' else 'zeta'}_repo"]:
            raise ValueError(f"Unexpected {part} remote")
        for field in ("commit", "lakefile_blob"):
            value = repo.get(field, "")
            if not SHA.fullmatch(value):
                raise ValueError(f"{part}.{field} must be a full hexadecimal SHA")
            expected_prefix = "oai" if part == "oai" else "zeta"
            if value != EXPECTED[f"{expected_prefix}_{field}"]:
                raise ValueError(f"{part}.{field} drift; review lock changes first")
    if data["oai"].get("subdir") != "lean":
        raise ValueError("OAI package must remain in lean/")
    if data.get("allowed_proof_axioms") != ["propext", "Quot.sound", "Classical.choice"]:
        raise ValueError("Axiom allowlist differs from comparator policy")


def read_and_validate(root: Path = ROOT) -> dict:
    data = json.loads((root / "source-lock.json").read_text(encoding="utf-8"))
    toolchain = (root / "lean-toolchain").read_text(encoding="utf-8")
    validate_lock(data, toolchain)
    return data


if __name__ == "__main__":
    try:
        d = read_and_validate()
        print("PIN LOCK OK: OAI", d["oai"]["commit"][:12], "Zeta23", d["zeta23"]["commit"][:12])
    except Exception as exc:
        print(f"LOCK VERIFICATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
