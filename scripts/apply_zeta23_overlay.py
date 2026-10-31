#!/usr/bin/env python3
"""Reconstruct a reviewed Zeta23 compatibility tree; never alter its Git checkout.

Unmodified Lean files are read-only symlinks to the pristine pinned checkout;
reviewed files are byte-exact regular copies. Each edited file has an exact
original Git-blob SHA, ordered replacement list, and expected output blob SHA.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath

SCHEMA = "OPICA_OAI_ZETA23_COMPAT_OVERLAY_V1"
MANIFEST = Path("compat/zeta23/overlay.json")
OVERLAY = Path(".bridge/overlays/zeta23")
EVIDENCE = Path(".bridge/overlays/zeta23/evidence.json")


def git_blob(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_relpath(raw: str) -> Path:
    if not isinstance(raw, str):
        raise ValueError("Compatibility path must be a string")
    pp = PurePosixPath(raw)
    if (pp.is_absolute() or "\\" in raw or not raw.startswith("Zeta23/")
            or any(part in ("", ".", "..") for part in raw.split("/"))
            or pp.suffix != ".lean"):
        raise ValueError(f"Unsafe compatibility module path: {raw!r}")
    return Path(*pp.parts)


def read_manifest(root: Path, source_lock: dict) -> tuple[dict, bytes]:
    manifest_path = root / MANIFEST
    b = manifest_path.read_bytes()
    d = json.loads(b)
    if d.get("schema") != SCHEMA:
        raise ValueError("Unexpected compatibility manifest schema")
    if d.get("source_commit") != source_lock["zeta23"]["commit"]:
        raise ValueError("Compatibility source commit mismatches pristine source lock")
    if d.get("mathlib_commit") != source_lock["workspace_mathlib"]:
        raise ValueError("Compatibility Mathlib revision mismatches pinned workspace")
    if d.get("lean_toolchain") != source_lock["lean_toolchain"]:
        raise ValueError("Compatibility Lean toolchain mismatch")
    edits = d.get("files")
    if not isinstance(edits, list) or not edits:
        raise ValueError("No reviewed compatibility edits")
    seen = set()
    for f in edits:
        rel = validate_relpath(f.get("path"))
        if rel in seen:
            raise ValueError(f"Duplicate modified module {rel}")
        seen.add(rel)
        for key in ("source_git_blob", "patched_git_blob"):
            v = f.get(key)
            if not isinstance(v, str) or len(v) != 40 or any(c not in "0123456789abcdef" for c in v):
                raise ValueError(f"Invalid {key} for {rel}")
        rs = f.get("replacements")
        if not isinstance(rs, list) or not rs:
            raise ValueError(f"No replacements for {rel}")
        for r in rs:
            old, new, n = r.get("before"), r.get("after"), r.get("count")
            if (not isinstance(old, str) or not isinstance(new, str) or not old
                    or old == new or not isinstance(n, int) or isinstance(n, bool)
                    or n < 1 or n > 10 or "\n" in old or "\n" in new):
                raise ValueError(f"Invalid reviewed edit for {rel}")
            if any(token in new for token in ("sorry", "admit", "axiom ", "opaque ")):
                raise ValueError(f"Unapproved proof alteration for {rel}")
    return d, b


def materialized_bytes(source_file: Path, spec: dict) -> bytes:
    raw = source_file.read_bytes()
    original = git_blob(raw)
    if original != spec["source_git_blob"]:
        raise ValueError(f"Source blob mismatch for {spec['path']}: {original}")
    text = raw.decode("utf-8")
    for edit in spec["replacements"]:
        old, new, required = edit["before"], edit["after"], edit["count"]
        actual = text.count(old)
        if actual != required:
            raise ValueError(f"Review anchor mismatch in {spec['path']}: {old!r} {actual} != {required}")
        text = text.replace(old, new)
    result = text.encode("utf-8")
    if git_blob(result) != spec["patched_git_blob"]:
        raise ValueError(f"Patched Git blob mismatch for {spec['path']}")
    return result


def _source_files(source: Path):
    if not source.is_dir() or source.is_symlink():
        raise RuntimeError("Original Zeta23 directory is missing or is a symlink")
    # Reject any symlink from the original source; it must not reach outside the pin.
    for item in sorted(source.rglob("*")):
        if item.is_symlink():
            raise RuntimeError(f"Symlink found in pinned Zeta23 source: {item}")
        yield item


def _verify_tree(root: Path, source: Path, specs: dict[Path, dict], outputs: dict[Path, bytes]):
    overlay_dir = root / OVERLAY / "Zeta23"
    if overlay_dir.is_symlink() or not overlay_dir.is_dir():
        raise RuntimeError("Overlay directory was not generated correctly")
    expected = set()
    for item in _source_files(source):
        rel = item.relative_to(source)
        target = overlay_dir / rel
        expected.add(rel)
        if item.is_dir():
            if not target.is_dir() or target.is_symlink():
                raise RuntimeError(f"Overlay directory tampered: {rel}")
        elif rel in specs:
            if not target.is_file() or target.is_symlink() or target.read_bytes() != outputs[rel]:
                raise RuntimeError(f"Patched overlay file tampered: {rel}")
        elif item.is_file():
            if not target.is_symlink() or target.resolve() != item.resolve():
                raise RuntimeError(f"Original-source overlay link tampered: {rel}")
        else:
            raise RuntimeError(f"Unexpected original source entry: {rel}")
    actual = {p.relative_to(overlay_dir) for p in overlay_dir.rglob("*")}
    if actual != expected:
        raise RuntimeError(f"Unexpected paths in compatibility overlay: {sorted(map(str,actual ^ expected))[:6]}")


def prepare_overlay(root: Path, source_lock: dict) -> dict:
    """Idempotently prepare and byte-verify the active tree. No git edits."""
    root = root.resolve()
    source = root / ".bridge/vendor/zeta23/Zeta23"
    d, manifest_bytes = read_manifest(root, source_lock)
    specs = {validate_relpath(f["path"]).relative_to("Zeta23"): f for f in d["files"]}
    outputs = {}
    for rel, spec in specs.items():
        p = source / rel
        if not p.is_file() or p.is_symlink():
            raise RuntimeError(f"Missing pristine compat source: {rel}")
        outputs[rel] = materialized_bytes(p, spec)
    overlay_dir = root / OVERLAY / "Zeta23"
    evidence_path = root / EVIDENCE
    manifest_hash = sha256(manifest_bytes)
    evidence = {
        "schema": "OPICA_OAI_ZETA23_COMPAT_EVIDENCE_V1",
        "source_commit": d["source_commit"],
        "manifest_sha256": manifest_hash,
        "mode": "PRISTINE_FILE_LINKS_PLUS_REVIEWED_COPIES",
        "files": [{
            "path": spec["path"],
            "source_git_blob": spec["source_git_blob"],
            "patched_git_blob": spec["patched_git_blob"],
        } for spec in d["files"]],
        "lean_compiled": False,
        "step4_proved": False,
    }
    if (root / OVERLAY).is_symlink():
        raise RuntimeError("Overlay parent is a symlink")
    if (root / OVERLAY).exists():
        if not evidence_path.is_file() or evidence_path.is_symlink():
            raise RuntimeError("Existing overlay missing its evidence")
        if json.loads(evidence_path.read_text(encoding="utf-8")) != evidence:
            raise RuntimeError("Existing overlay evidence mismatch")
        _verify_tree(root, source, specs, outputs)
        return evidence
    overlay_dir.mkdir(parents=True, exist_ok=False)
    for item in _source_files(source):
        rel = item.relative_to(source)
        dest = overlay_dir / rel
        if item.is_dir():
            dest.mkdir()
        elif rel in outputs:
            dest.write_bytes(outputs[rel])
        elif item.is_file():
            dest.symlink_to(os.path.relpath(item, dest.parent))
        else:
            raise RuntimeError(f"Unsupported source entry: {rel}")
    _verify_tree(root, source, specs, outputs)
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence
