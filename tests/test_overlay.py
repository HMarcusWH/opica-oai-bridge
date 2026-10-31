"""Adversarial no-network validation of the pinned Zeta23 compatibility overlay."""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from apply_zeta23_overlay import (  # noqa: E402
    MANIFEST, OVERLAY, git_blob, prepare_overlay, validate_relpath,
    read_manifest,
)

PIN = "e" * 40
MATHLIB = "d" * 40
LOCK = {"zeta23": {"commit": PIN}, "workspace_mathlib": MATHLIB,
        "lean_toolchain": "leanprover/lean4:v4.34.1"}


def fixture(root: Path) -> dict:
    source = root / ".bridge/vendor/zeta23/Zeta23"
    (source / "CCM").mkdir(parents=True)
    (source / "CCM/Patched.lean").write_text("theorem old : True := by trivial\n", encoding="utf-8")
    (source / "CCM/Unchanged.lean").write_text("theorem unchanged : True := by trivial\n", encoding="utf-8")
    old = (source / "CCM/Patched.lean").read_bytes()
    new = old.replace(b"by trivial", b"by exact True.intro")
    data = {
        "schema": "OPICA_OAI_ZETA23_COMPAT_OVERLAY_V1",
        "source_commit": PIN,
        "mathlib_commit": MATHLIB,
        "lean_toolchain": "leanprover/lean4:v4.34.1",
        "files": [{
            "path": "Zeta23/CCM/Patched.lean",
            "source_git_blob": git_blob(old),
            "patched_git_blob": git_blob(new),
            "replacements": [{"before": "by trivial", "after": "by exact True.intro", "count": 1}],
        }]
    }
    (root / MANIFEST).parent.mkdir(parents=True)
    (root / MANIFEST).write_text(json.dumps(data), encoding="utf-8")
    return data


class OverlayAdversarialTests(unittest.TestCase):
    def test_real_manifest_pins_five_original_and_five_results(self):
        data = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(data["source_commit"], "ebbd787202ce2c67518946fc642af12ff009eaa6")
        self.assertEqual(data["mathlib_commit"], "d13f23b723b8a846827a245b89c10fc7d3f11612")
        self.assertEqual({f["path"] for f in data["files"]}, {
            "Zeta23/FromPNTPlus/StrongPNTPrefix.lean",
            "Zeta23/WeilEF/GammaRBracket.lean",
            "Zeta23/Analytic/RectangleLogDeriv.lean",
            "Zeta23/CCM/DictionaryArchDiagonal.lean",
            "Zeta23/WeilEF/Landau.lean",
        })
        landau = next(f for f in data["files"] if f["path"] == "Zeta23/WeilEF/Landau.lean")
        self.assertEqual(landau["source_git_blob"], "5b6d356d64a6e7a1bf6bc0e98406d3dfe5a7f4d6")
        self.assertEqual(landau["patched_git_blob"], "1692d85e2f7a65103ed89f2febde155c6121c62c")
        self.assertEqual(len(landau["replacements"]), 3)
        self.assertTrue(all(f["source_git_blob"] != f["patched_git_blob"] for f in data["files"]))
        for f in data["files"]:
            for replacement in f["replacements"]:
                self.assertNotIn("sorry", replacement["after"])
                self.assertNotIn("axiom", replacement["after"])

    def test_link_routing_and_idempotence_and_pristine_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            original = (root / ".bridge/vendor/zeta23/Zeta23/CCM/Patched.lean").read_bytes()
            e = prepare_overlay(root, LOCK)
            self.assertEqual(len(e["files"]), 1)
            modified = root / OVERLAY / "Zeta23/CCM/Patched.lean"
            unchanged = root / OVERLAY / "Zeta23/CCM/Unchanged.lean"
            self.assertFalse(modified.is_symlink())
            self.assertTrue(unchanged.is_symlink())
            self.assertIn(b"exact True.intro", modified.read_bytes())
            self.assertEqual(original, (root / ".bridge/vendor/zeta23/Zeta23/CCM/Patched.lean").read_bytes())
            self.assertEqual(e, prepare_overlay(root, LOCK))

    def test_modifying_overlay_file_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            prepare_overlay(root, LOCK)
            (root / OVERLAY / "Zeta23/CCM/Patched.lean").write_text("changed")
            with self.assertRaisesRegex(RuntimeError, "tampered"):
                prepare_overlay(root, LOCK)

    def test_replaced_original_link_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            prepare_overlay(root, LOCK)
            p = root / OVERLAY / "Zeta23/CCM/Unchanged.lean"
            p.unlink()
            p.write_text("not a source link\n")
            with self.assertRaisesRegex(RuntimeError, "tampered"):
                prepare_overlay(root, LOCK)

    def test_extra_overlay_path_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            prepare_overlay(root, LOCK)
            (root / OVERLAY / "Zeta23/Surprise.lean").write_text("-- extra\n")
            with self.assertRaisesRegex(RuntimeError, "Unexpected paths"):
                prepare_overlay(root, LOCK)

    def test_modified_original_hash_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            source = root / ".bridge/vendor/zeta23/Zeta23/CCM/Patched.lean"
            source.write_text("changed before prepare\n")
            with self.assertRaisesRegex(ValueError, "Source blob mismatch"):
                prepare_overlay(root, LOCK)

    def test_manifest_tampering_and_escape_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = fixture(root)
            data["files"][0]["path"] = "Zeta23/../../Mathlib/Injected.lean"
            (root / MANIFEST).write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                prepare_overlay(root, LOCK)
            data["files"][0]["path"] = "Zeta23/CCM/Patched.lean"
            data["files"][0]["replacements"][0]["after"] = "by sorry"
            (root / MANIFEST).write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Unapproved"):
                prepare_overlay(root, LOCK)

    def test_replacement_count_and_output_hash_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = fixture(root)
            data["files"][0]["replacements"][0]["count"] = 2
            (root / MANIFEST).write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Review anchor mismatch"):
                prepare_overlay(root, LOCK)
            data["files"][0]["replacements"][0]["count"] = 1
            data["files"][0]["patched_git_blob"] = "f" * 40
            (root / MANIFEST).write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Patched Git blob mismatch"):
                prepare_overlay(root, LOCK)

    def test_unexpected_existing_overlay_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root)
            (root / OVERLAY).mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "missing its evidence"):
                prepare_overlay(root, LOCK)

    def test_refuses_untrusted_path_forms(self):
        for value in ("/Zeta23/CCM/A.lean", "Zeta23/../A.lean", "Zeta23\\CCM\\A.lean",
                      "Zeta23/./A.lean", "Zeta23/A.txt", "Other/A.lean"):
            with self.assertRaises(ValueError):
                validate_relpath(value)


if __name__ == "__main__":
    unittest.main()
