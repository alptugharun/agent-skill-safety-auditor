from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish-v0.1.0a1.yml"


class HistoricalReleaseWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_legacy_publisher_is_read_only(self):
        self.assertIn("permissions:\n  contents: read", self.text)
        self.assertIn("      contents: read", self.text)
        for unsafe in ("contents: write", "id-token: write", "--clobber",
                       "gh release upload", "gh release create", "gh release delete",
                       "gh release edit", "sigstore/", "pip wheel"):
            with self.subTest(unsafe=unsafe):
                self.assertNotIn(unsafe, self.text)

    def test_pinned_actions_and_safe_checkout(self):
        actions = re.findall(r"^\s*uses:\s*([^\s#]+)", self.text, re.MULTILINE)
        self.assertEqual(len(actions), 2)
        for action in actions:
            self.assertRegex(action, r"^[^@\s]+@[0-9a-f]{40}$")
        self.assertIn("persist-credentials: false", self.text)

    def test_metadata_read_and_synthetic_tests(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("set -euo pipefail", self.text)
        self.assertIn("scripts/verify_historical_release_metadata.py", self.text)
        self.assertIn('gh api "repos/${GITHUB_REPOSITORY}/releases/tags/v0.1.0a1"', self.text)
        self.assertIn("test_historical_release_metadata.py", self.text)
        self.assertIn('gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/v0.1.0a1"', self.text)
        self.assertIn("verify_historical_release_metadata.py --tag-ref", self.text)


if __name__ == "__main__":
    unittest.main()
