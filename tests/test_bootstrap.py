"""Network-free tests of the builder's provenance and refusal paths."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_workspace import (  # noqa: E402
    REQUIRED_MARKERS, assert_git_checkout, prepare, render_lakefile
)
from verify_lock import read_and_validate, validate_lock  # noqa: E402
from check_axioms import check  # noqa: E402
from write_gate_receipt import validate_manifest, VALID_STAGES  # noqa: E402
from verify_resolution import check_resolution  # noqa: E402

MATHLIB = "d13f23b723b8a846827a245b89c10fc7d3f11612"
FAKE_LAKE = f'''import Lake
open Lake DSL
package OAI where
  version := v!"0.1.0"
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "{MATHLIB}"
@[default_target] lean_lib OAI
private def preResolutionPatchNames : Array Lean.Name := #[]
post_update pkg do
  pure ()
'''


def run(*args: str, cwd: Path) -> str:
    p = subprocess.run(args, cwd=cwd, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    return p.stdout.strip()


def git_fixture(where: Path, files: dict[str, str]) -> tuple[str, str, dict[str, str]]:
    where.mkdir(parents=True)
    run("git", "init", "-q", cwd=where)
    for name, content in files.items():
        path = where / name
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(content, encoding="utf-8")
    run("git", "add", ".", cwd=where)
    run("git", "-c", "user.email=tests@example.invalid", "-c", "user.name=Test", "commit", "-qm", "fixture", cwd=where)
    sha = run("git", "rev-parse", "HEAD", cwd=where)
    hashes = {name: run("git", "hash-object", name, cwd=where) for name in files}
    return sha, str(where), hashes


class BuildReceiptTests(unittest.TestCase):
    def test_manifest_lock(self):
        rev = MATHLIB
        validate_manifest({"packages": [
            {"name": "mathlib", "type": "git", "rev": rev},
            {"name": "example", "type": "git", "rev": "a" * 40},
        ]}, rev)
        with self.assertRaises(ValueError):
            validate_manifest({"packages": [{"name": "mathlib", "rev": "b" * 40}]}, rev)
        with self.assertRaises(ValueError):
            validate_manifest({"packages": [{"name": "mathlib", "rev": rev, "type": "git"},
                                             {"name": "bad", "type": "git"}]}, rev)
        with self.assertRaises(ValueError):
            validate_manifest({"packages": []}, rev)

    def test_stages_and_boot_order(self):
        self.assertEqual(VALID_STAGES, {"oai", "zeta", "smoke", "axioms", "full"})
        workflow = (ROOT / ".github/workflows/integration-manual.yml").read_text()
        self.assertIn("lake-package-directory: .bridge/vendor/oai/lean", workflow)
        self.assertIn("use-github-cache: false", workflow)
        self.assertIn("use-mathlib-cache: false", workflow)
        self.assertIn(".bridge/gates/*.json", workflow)
        self.assertIn(".bridge/logs/*.log", workflow)


class StagedResolutionTests(unittest.TestCase):
    def test_ci_has_separate_resolution_cache_build_steps(self):
        workflow = (ROOT / ".github/workflows/integration-manual.yml").read_text()
        self.assertIn("scripts/build.sh resolve", workflow)
        self.assertIn("scripts/build.sh cache", workflow)
        self.assertIn("BRIDGE_PRE_RESOLVED: '1'", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn(".bridge/resolution-report.json", workflow)

    def test_missing_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source-lock.json").write_bytes((ROOT / "source-lock.json").read_bytes())
            (root / "lean-toolchain").write_bytes((ROOT / "lean-toolchain").read_bytes())
            with self.assertRaises(FileNotFoundError):
                check_resolution(root=root, verify_git=False)

    def test_resolution_fingerprint_and_mathlib(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("source-lock.json", "lean-toolchain"):
                (root / name).write_bytes((ROOT / name).read_bytes())
            lake_path = root / "lakefile.lean"
            lake_path.write_text("-- pinned generated lake config\n")
            prep = root / ".bridge/prepare-evidence.json"
            prep.parent.mkdir(parents=True)
            lock = read_and_validate(root)
            prep.write_text(json.dumps({
                "schema": "OPICA_OAI_PREPARE_EVIDENCE_V1",
                "oai_head": lock["oai"]["commit"],
                "zeta23_head": lock["zeta23"]["commit"],
                "mathlib_target": MATHLIB,
                "generated_lake_sha256": hashlib.sha256(lake_path.read_bytes()).hexdigest(),
            }))
            manifest = root / "lake-manifest.json"
            manifest.write_text(json.dumps({"packages": [
                {"name": "mathlib", "type": "git", "rev": MATHLIB},
                {"name": "another", "type": "git", "rev": "a" * 40},
            ]}))
            result = check_resolution(root=root, verify_git=False)
            self.assertEqual(result["stage"], "DEPENDENCY_RESOLVED_NOT_COMPILED")
            self.assertFalse(result["native_proof_compiled"])
            lake_path.write_text("-- tampered\n")
            with self.assertRaisesRegex(ValueError, "changed after preparation"):
                check_resolution(root=root, verify_git=False)
            lake_path.write_text("-- pinned generated lake config\n")
            manifest.write_text(json.dumps({"packages": [
                {"name": "mathlib", "type": "git", "rev": "b" * 40},
            ]}))
            with self.assertRaisesRegex(ValueError, "Mathlib"):
                check_resolution(root=root, verify_git=False)

class LockTests(unittest.TestCase):
    def test_unchanged_lock(self):
        d = read_and_validate(ROOT)
        self.assertEqual(d["workspace_mathlib"], MATHLIB)

    def test_rejects_unsafe_pin(self):
        data = read_and_validate(ROOT)
        data["oai"]["commit"] = "main"
        with self.assertRaises(ValueError):
            validate_lock(data, "leanprover/lean4:v4.34.1")

    def test_rejects_axiom_permission_changes(self):
        data = read_and_validate(ROOT)
        data["allowed_proof_axioms"].append("sorryAx")
        with self.assertRaises(ValueError):
            validate_lock(data, "leanprover/lean4:v4.34.1")


class ComposeTests(unittest.TestCase):
    def test_preserves_upstream_patch_hooks(self):
        s = render_lakefile(FAKE_LAKE, MATHLIB)
        self.assertIn("private def preResolutionPatchNames", s)
        self.assertIn("post_update pkg do", s)
        self.assertIn("package OPICAOAI where", s)
        self.assertIn("lean_lib Zeta23", s)
        self.assertIn("@[default_target] lean_lib OPICAOAI", s)
        self.assertNotIn("@[default_target] lean_lib OAI", s)
        self.assertEqual(s.count("require mathlib from git"), 1)

    def test_drift_fails_closed(self):
        with self.assertRaises(ValueError):
            render_lakefile(FAKE_LAKE.replace("post_update pkg do", ""), MATHLIB)
        with self.assertRaises(ValueError):
            render_lakefile(FAKE_LAKE, "0" * 40)

    def test_local_complete_vendor_and_repeatability(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            sources = base / "fixtures"
            oai_sha, oai_url, oai_hash = git_fixture(sources / "oai", {
                "lean/lakefile.lean": FAKE_LAKE,
                "lean/OAI.lean": "-- OAI fixture\n",
                "lean/OAI/NumberTheory/DirichletL/Nonvanishing.lean": "-- OAI fixture\n",
                "lean/ComparatorChallenges/README.md": "fixture\n",
                "lean/patches/README.md": "fixture\n",
            })
            zeta_sha, zeta_url, zeta_hash = git_fixture(sources / "zeta", {
                "lakefile.toml": "name = \"Zeta23\"\n",
                "Zeta23.lean": "-- Zeta fixture\n",
                "Zeta23/OPICARound4/PrimeDiscrepancyIntegral.lean": "-- Zeta fixture\n",
            })
            root = base / "bridge"
            root.mkdir()
            (root / "compat/zeta23").mkdir(parents=True)
            vendor = root / ".bridge/vendor"
            vendor.mkdir(parents=True)
            run("git", "clone", "-q", oai_url, str(vendor / "oai"), cwd=base)
            run("git", "clone", "-q", zeta_url, str(vendor / "zeta23"), cwd=base)
            data = {"oai": {"repo": oai_url, "commit": oai_sha, "lakefile_blob": oai_hash["lean/lakefile.lean"]},
                    "zeta23": {"repo": zeta_url, "commit": zeta_sha, "lakefile_blob": zeta_hash["lakefile.toml"]},
                    "workspace_mathlib": MATHLIB}
            a = prepare(root, data, offline=True)
            b = prepare(root, data, offline=True)
            self.assertEqual(a, b)
            self.assertEqual((root / "OAI").resolve(), (vendor / "oai/lean/OAI").resolve())
            self.assertTrue((root / "lakefile.lean").exists())
            self.assertFalse(a["lean_compiled"])
            (root / "lakefile.lean").write_text("tampered!", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "drift"):
                prepare(root, data, offline=True)
            # The source checkout and commit itself must be verified.
            with self.assertRaises(RuntimeError):
                assert_git_checkout(vendor / "oai", zeta_sha, oai_url)


class AxiomTests(unittest.TestCase):
    def test_allowed(self):
        check("'OPICAOAI.riemannZeta_ne_zero_above_seven_eighths' depends on axioms: [propext, Classical.choice, Quot.sound]")

    def test_rejects_sorry(self):
        with self.assertRaises(ValueError):
            check("'OPICAOAI.riemannZeta_ne_zero_above_seven_eighths' depends on axioms: [sorryAx]")

    def test_missing_log_fails_closed(self):
        with self.assertRaises(ValueError):
            check("some unrelated output")

    def test_independent_source_theorem_audit(self):
        from check_axioms import ALL_THEOREMS
        self.assertEqual(len(ALL_THEOREMS), 3)
        log = "\\n".join(
            f"'{name}' depends on axioms: [propext, Classical.choice, Quot.sound]"
            for name in ALL_THEOREMS
        ).replace("\\n", "\n")
        check(log, all_sources=True)
        # A wrapper alone must NOT be mistaken for independently audited sources.
        with self.assertRaises(ValueError):
            check(log.splitlines()[-1], all_sources=True)
        with self.assertRaises(ValueError):
            check(log + "\n" + log.splitlines()[0], all_sources=True)
        with self.assertRaises(ValueError):
            check(log.replace("Quot.sound", "sorryAx"), all_sources=True)
        with self.assertRaises(ValueError):
            check(log.replace("Classical.choice", "new_untrusted_axiom"), all_sources=True)
        # The Lean kernel can also report declarations with no axiom dependencies.
        no_axioms = log.replace(
            "'OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re' depends on axioms: "
            "[propext, Classical.choice, Quot.sound]",
            "'OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re' does not depend on any axioms",
        )
        check(no_axioms, all_sources=True)

    def test_axiom_gate_uses_all_sources_and_drops_stale_receipt(self):
        script = (ROOT / "scripts/build.sh").read_text(encoding="utf-8")
        self.assertIn("--all-sources", script)
        self.assertIn('rm -f ".bridge/gates/${mode}.json"', script)
        lean_file = (ROOT / "OPICAOAI/PrintAxioms.lean").read_text()
        for theorem in (
            "OAI.riemannZeta_ne_zero_of_seven_eighths_lt_re",
            "Zeta23.OPICARound4.prime_log_abel",
            "OPICAOAI.riemannZeta_ne_zero_above_seven_eighths",
        ):
            self.assertIn(f"#print axioms {theorem}", lean_file)


if __name__ == "__main__":
    unittest.main()
