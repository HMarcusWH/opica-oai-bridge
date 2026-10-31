#!/usr/bin/env python3
"""Compose pinned, complete OAI and Zeta23 source trees into one Lake workspace.

This only prepares local sources and generates the Lake file. It does NOT claim
Lean compatibility, theorem acceptance, or successful compilation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from verify_lock import ROOT, read_and_validate
from apply_zeta23_overlay import prepare_overlay

VENDOR_DIRS = {"oai": Path(".bridge/vendor/oai"), "zeta23": Path(".bridge/vendor/zeta23")}
REQUIRED_MARKERS = (
    "package OAI where",
    "@[default_target] lean_lib OAI",
    "private def preResolutionPatchNames",
    "post_update pkg do",
    "require mathlib from git",
)


def cmd(*args: str, cwd: Path | None = None) -> str:
    p = subprocess.run(list(args), cwd=cwd, check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.strip()


def assert_git_checkout(directory: Path, expected_rev: str, expected_remote: str) -> None:
    if not (directory / ".git").exists():
        raise RuntimeError(f"Not a Git checkout: {directory}")
    actual = cmd("git", "rev-parse", "HEAD", cwd=directory)
    if actual != expected_rev:
        raise RuntimeError(f"Source checkout drift: {directory}: {actual}, expected {expected_rev}")
    remote = cmd("git", "remote", "get-url", "origin", cwd=directory)
    if remote != expected_remote:
        raise RuntimeError(f"Unexpected origin for {directory}: {remote}")
    if cmd("git", "status", "--porcelain", "--untracked-files=no", cwd=directory):
        raise RuntimeError(f"Source checkout has tracked modifications: {directory}")


def ensure_checkout(directory: Path, metadata: dict, offline: bool = False) -> None:
    url = metadata["repo"]
    sha = metadata["commit"]
    if not directory.exists():
        if offline:
            raise RuntimeError(f"Offline checkout missing: {directory}")
        directory.parent.mkdir(parents=True, exist_ok=True)
        cmd("git", "clone", "--filter=blob:none", "--no-checkout", url, str(directory))
        try:
            cmd("git", "-C", str(directory), "checkout", "--detach", sha)
        except subprocess.CalledProcessError:
            cmd("git", "-C", str(directory), "fetch", "origin", sha)
            cmd("git", "-C", str(directory), "checkout", "--detach", sha)
    assert_git_checkout(directory, sha, url)


def assert_blob(file: Path, expected_sha: str) -> None:
    value = cmd("git", "hash-object", str(file))
    if value != expected_sha:
        raise RuntimeError(f"Git blob mismatch {file}: got {value}, expected {expected_sha}")


def render_lakefile(upstream: str, mathlib_sha: str) -> str:
    """Keep OAI's full dependency and patch code; change only explicit package wiring."""
    for marker in REQUIRED_MARKERS:
        if upstream.count(marker) != 1:
            raise ValueError(f"Unexpected upstream Lake structure: marker {marker!r} count {upstream.count(marker)}")
    if f'"https://github.com/leanprover-community/mathlib4.git" @ "{mathlib_sha}"' not in upstream:
        raise ValueError("Upstream Lake Mathlib revision does not match bridge lock")
    transformed = upstream.replace("package OAI where", "package OPICAOAI where", 1)
    transformed = transformed.replace("@[default_target] lean_lib OAI", "lean_lib OAI", 1)
    result = (
        "-- GENERATED FILE. Do not edit: python3 scripts/prepare_workspace.py\n"
        "-- Based on exact pinned OAI lakefile; upstream dependency patches retained.\n"
        + transformed.rstrip() + "\n\n"
        + "lean_lib Zeta23 where\n"
          "  roots := #[`Zeta23]\n"
          "  globs := #[`Zeta23.+]\n\n"
          "@[default_target] lean_lib OPICAOAI where\n"
          "  roots := #[`OPICAOAI]\n"
          "  globs := #[`OPICAOAI.+]\n"
    )
    if "@[default_target] lean_lib OAI" in result:
        raise AssertionError("Full OAI root must not become bridge default target")
    return result


def relative_link(root: Path, link_name: str, source: str) -> None:
    link = root / link_name
    dest = root / source
    if not dest.exists():
        raise RuntimeError(f"Source path missing for symlink {link_name}: {dest}")
    if link.is_symlink():
        if link.resolve() != dest.resolve():
            raise RuntimeError(f"Symlink mismatch: {link_name}")
        return
    if link.exists():
        raise RuntimeError(f"Refusing to overwrite existing {link_name}")
    link.symlink_to(os.path.relpath(dest, link.parent), target_is_directory=dest.is_dir())


def make_links(root: Path) -> None:
    links = {
        "OAI": ".bridge/vendor/oai/lean/OAI",
        "OAI.lean": ".bridge/vendor/oai/lean/OAI.lean",
        "ComparatorChallenges": ".bridge/vendor/oai/lean/ComparatorChallenges",
        "patches": ".bridge/vendor/oai/lean/patches",
        "Zeta23": ".bridge/overlays/zeta23/Zeta23",
        "Zeta23.lean": ".bridge/vendor/zeta23/Zeta23.lean",
    }
    # Upgrade a previous, verified pristine link to the reviewed overlay link;
    # refuse any other symlink target or a real Zeta23 directory.
    link = root / "Zeta23"
    old_target = root / ".bridge/vendor/zeta23/Zeta23"
    if link.is_symlink() and link.resolve() == old_target.resolve():
        link.unlink()
    for name, path in links.items():
        relative_link(root, name, path)


def prepare(root: Path, data: dict, offline: bool = False) -> dict:
    if os.name == "nt":
        raise RuntimeError("Use Linux or WSL2. Windows native symlink privileges are not assumed.")
    root = root.resolve()
    for name, rel in VENDOR_DIRS.items():
        ensure_checkout(root / rel, data[name], offline)
    oai_lake = root / VENDOR_DIRS["oai"] / "lean/lakefile.lean"
    zeta_lake = root / VENDOR_DIRS["zeta23"] / "lakefile.toml"
    assert_blob(oai_lake, data["oai"]["lakefile_blob"])
    assert_blob(zeta_lake, data["zeta23"]["lakefile_blob"])
    # No patch to the mathematical source can be applied by this bootstrap.
    for patch in sorted((root / "compat/zeta23").glob("*.patch")):
        raise RuntimeError(f"Unreviewed Zeta23 overlay {patch.name}: add a separate audited patch procedure")
    overlay_evidence = prepare_overlay(root, data)
    make_links(root)
    lake = render_lakefile(oai_lake.read_text(encoding="utf-8"), data["workspace_mathlib"])
    lake_path = root / "lakefile.lean"
    if lake_path.exists() and lake_path.read_text(encoding="utf-8") != lake:
        raise RuntimeError("Generated Lake file drift; refusing to overwrite a modified file")
    lake_path.write_text(lake, encoding="utf-8")
    status = {
        "schema": "OPICA_OAI_PREPARE_EVIDENCE_V1",
        "lean_compiled": False,
        "step4_proved": False,
        "oai_head": data["oai"]["commit"],
        "zeta23_head": data["zeta23"]["commit"],
        "mathlib_target": data["workspace_mathlib"],
        "generated_lake_sha256": hashlib.sha256(lake.encode()).hexdigest(),
        "source_mode": "PINNED_SOURCE_COMPOSITION_REVIEWED_ZETA23_OVERLAY",
        "compat_manifest_sha256": overlay_evidence["manifest_sha256"],
        "compat_patched_modules": len(overlay_evidence["files"]),
    }
    state_path = root / ".bridge/prepare-evidence.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Only accept verified existing vendor checkouts")
    args = parser.parse_args()
    read_and_validate(ROOT)
    evidence = prepare(ROOT, read_and_validate(ROOT), args.offline)
    print("SOURCE PREPARATION OK, not a Lean build:", json.dumps(evidence))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PREPARATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
