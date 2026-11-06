"""Validate GitHub metadata of an immutable historical release, not its bytes."""

import json
import re
import sys
from collections.abc import Mapping

TAG = "v0.1.0a1"
WHEEL = "agent_skill_safety_auditor-0.1.0a1-py3-none-any.whl"
EXPECTED = (WHEEL, WHEEL + ".sigstore.json", "SHA256SUMS.txt", "SHA256SUMS.txt.sigstore.json")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


def validate(payload):
    if not isinstance(payload, Mapping) or payload.get("tag_name") != TAG:
        raise ValueError("wrong release or invalid response")
    if payload.get("draft") is not False or payload.get("prerelease") is not True:
        raise ValueError("expected a published prerelease")
    assets = payload.get("assets")
    if not isinstance(assets, list):
        raise ValueError("missing asset listing")
    found = {}
    for asset in assets:
        if not isinstance(asset, Mapping) or not isinstance(asset.get("name"), str):
            raise ValueError("invalid asset name")
        if asset["name"] in found:
            raise ValueError("duplicate asset name")
        found[asset["name"]] = asset
    for name in EXPECTED:
        if name not in found:
            raise ValueError("required asset absent: " + name)
        asset = found[name]
        size = asset.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("invalid asset size: " + name)
        if not isinstance(asset.get("digest"), str) or not DIGEST.fullmatch(asset["digest"]):
            raise ValueError("invalid digest metadata: " + name)
    return len(assets)


def main():
    try:
        count = validate(json.load(sys.stdin))
    except (json.JSONDecodeError, ValueError) as error:
        print("Release metadata FAILED: " + str(error), file=sys.stderr)
        return 1
    print(f"{TAG}: {count} assets listed; four expected assets have metadata.")
    print("Metadata only; downloaded bytes, checksums, signatures, provenance and runtime NOT verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
