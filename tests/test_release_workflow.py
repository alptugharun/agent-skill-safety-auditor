from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish-v0.1.0a1.yml"


class ReleaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_release_workflow_uses_oidc_and_immutable_actions(self):
        self.assertIn("id-token: write", self.text)
        self.assertIn(
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            self.text,
        )
        self.assertIn(
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
            self.text,
        )
        self.assertIn(
            "sigstore/gh-action-sigstore-python@790bc6befb9d733738f18d8f895854b453640ec9",
            self.text,
        )

    def test_release_builds_and_reinstalls_the_wheel(self):
        self.assertIn("pip wheel", self.text)
        self.assertIn("--no-deps dist/*.whl", self.text)
        self.assertIn("skill-audit --help", self.text)
        self.assertIn("import skill_safety_auditor", self.text)

    def test_release_publishes_checksum_and_sigstore_bundles(self):
        self.assertIn("SHA256SUMS.txt", self.text)
        self.assertIn("\\.whl.sigstore.json$", self.text)
        self.assertIn("v0.1.0a1", self.text)


if __name__ == "__main__":
    unittest.main()
