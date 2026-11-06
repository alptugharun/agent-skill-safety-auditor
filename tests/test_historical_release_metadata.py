import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_historical_release_metadata.py"
spec = importlib.util.spec_from_file_location("release_metadata", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sample():
    return {"tag_name": "v0.1.0a1", "draft": False, "prerelease": True,
            "assets": [{"name": n, "size": 100, "digest": "sha256:" + "a" * 64}
                       for n in module.EXPECTED]}


class ReleaseMetadataTests(unittest.TestCase):
    def test_complete_synthetic_release(self):
        self.assertEqual(module.validate(sample()), 4)

    def test_missing_or_duplicate_assets_fail(self):
        missing = sample()
        missing["assets"].pop()
        with self.assertRaisesRegex(ValueError, "required asset absent"):
            module.validate(missing)
        duplicate = sample()
        duplicate["assets"].append(copy.deepcopy(duplicate["assets"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate asset"):
            module.validate(duplicate)

    def test_unpublished_or_wrong_tag_fails(self):
        for field, value in (("tag_name", "v0.1.0a2"), ("draft", True),
                             ("prerelease", False)):
            data = sample()
            data[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.validate(data)

    def test_bad_size_and_digest_fails(self):
        for field, value in (("size", 0), ("size", True),
                             ("digest", "sha256:no"), ("digest", None)):
            data = sample()
            data["assets"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.validate(data)

    def test_invalid_response_fails(self):
        for data in (None, [], {"assets": []}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                module.validate(data)

    def test_additional_asset_permitted(self):
        data = sample()
        data["assets"].append({"name": "notes.txt"})
        self.assertEqual(module.validate(data), 5)

    def test_cli_output_states_limitations_and_fails_closed(self):
        good = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(sample()),
                              text=True, capture_output=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("NOT verified", good.stdout)
        bad = subprocess.run([sys.executable, str(SCRIPT)], input="{invalid",
                             text=True, capture_output=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("FAILED", bad.stderr)


if __name__ == "__main__":
    unittest.main()
