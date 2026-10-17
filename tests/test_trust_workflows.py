from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "openssf-scorecard.yml"


class TrustWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_scorecard_rescans_on_release_and_manual_dispatch(self):
        self.assertIn("release:\n    types: [published]", self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("push:\n    branches: [main]", self.text)

    def test_scorecard_action_is_pinned_and_results_are_published(self):
        self.assertIn(
            "ossf/scorecard-action@fa7117db83c52d787ae5a89f350999701505d78e",
            self.text,
        )
        self.assertIn("publish_results: true", self.text)
        self.assertIn("permissions: read-all", self.text)


if __name__ == "__main__":
    unittest.main()
