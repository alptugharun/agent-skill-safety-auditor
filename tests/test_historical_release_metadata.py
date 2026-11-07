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
    return {"id": module.RELEASE_ID, "tag_name": "v0.1.0a1",
            "draft": False, "prerelease": True,
            "assets": [{"name": name, "id": metadata["id"], "size": metadata["size"],
                        "state": "uploaded", "digest": metadata["digest"]}
                       for name, metadata in module.EXPECTED.items()]}


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

    def test_unexpected_asset_fails(self):
        data = sample()
        data["assets"].append({"name": "notes.txt", "id": 999, "size": 10,
                               "state": "uploaded", "digest": "sha256:" + "a" * 64})
        with self.assertRaisesRegex(ValueError, "unexpected asset"):
            module.validate(data)

    def test_metadata_drift_fails_even_with_valid_digest_syntax(self):
        for field, value in (("id", 0), ("size", 99999), ("state", "starter"),
                             ("digest", "sha256:" + "b" * 64)):
            data = sample()
            data["assets"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.validate(data)
        data = sample()
        data["id"] = 0
        with self.assertRaisesRegex(ValueError, "release identity"):
            module.validate(data)

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
