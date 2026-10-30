"""Security and ordering tests for M3's source-pinned workflow_run handoff.

These do not establish any Lean theorem and intentionally have no external imports.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class M3ChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = (ROOT / ".github/workflows/combined-smoke.yml").read_text()

    def test_gated_on_successful_main_m2_only(self):
        x = self.content
        self.assertIn('workflows: ["M2 Zeta23 Lean 4.34 compatibility diagnostic"]', x)
        self.assertIn("types: [completed]", x)
        self.assertIn("branches: [main]", x)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", x)
        self.assertIn("github.event.workflow_run.head_branch == 'main'", x)
        self.assertIn("workflow_dispatch:", x)

    def test_downstream_no_privilege_or_untrusted_artifact(self):
        x = self.content
        self.assertRegex(x, r"(?m)^permissions:\n  contents: read$")
        self.assertIn("persist-credentials: false", x)
        self.assertIn("cancel-in-progress: false", x)
        self.assertIn("group: full-bridge-build", x)
        self.assertNotIn("secrets.", x)
        self.assertNotIn("actions/download-artifact", x)
        self.assertNotIn("pull_request_target", x)
        self.assertNotIn("contents: write", x)

    def test_source_pins_before_native_proofs(self):
        x = self.content
        stages = [
            "python3 scripts/verify_lock.py",
            "python3 scripts/prepare_workspace.py",
            "bash scripts/build.sh resolve",
            "bash scripts/build.sh cache",
            "bash scripts/build.sh smoke",
            "bash scripts/build.sh axioms",
        ]
        positions = [x.index(s) for s in stages]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(x.count("BRIDGE_PRE_RESOLVED: '1'"), 2)
        self.assertIn(".bridge/axiom-audit.log", x)
        self.assertIn(".bridge/gates/*.json", x)
        self.assertIn("timeout-minutes: 330", x)

if __name__ == "__main__":
    unittest.main()
