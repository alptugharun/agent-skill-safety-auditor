"""Validate GitHub metadata of an immutable historical release, not its bytes."""

import json
import re
import sys
from collections.abc import Mapping

TAG = "v0.1.0a1"
# Baseline: GitHub API metadata read on 2026-11-07; NOT independently verified bytes.
RELEASE_ID = 402532112
# GitHub tag-ref snapshot read on 2026-11-08; not trusted signed provenance.
TAG_REF = "refs/tags/v0.1.0a1"
TAG_COMMIT_SHA = "bfdd79cc3c66669de21df1056503ccf6a100909c"
EXPECTED = {
    "agent_skill_safety_auditor-0.1.0a1-py3-none-any.whl": {"id": 631804714, "size": 9165, "digest": "sha256:5caef93fe1380832a3f236897146b4d78bcae077ba9993035162e6dbfda21e08"},
    "agent_skill_safety_auditor-0.1.0a1-py3-none-any.whl.sigstore.json": {"id": 631804718, "size": 11714, "digest": "sha256:a10f2e51a305c9b56aa34dea741fc7373d265cc18ee0a8eaaf5934960dcc95d3"},
    "SHA256SUMS.txt": {"id": 631804716, "size": 118, "digest": "sha256:5be1ba8a18f53f243033a746f63bc8430502f927b940448130e6bc0ec3ea8db3"},
    "SHA256SUMS.txt.sigstore.json": {"id": 631804717, "size": 11671, "digest": "sha256:7de1f13f7d7aab387affcf693af312cfcbcc4fc19f0c69147128fb9178e19f2b"},
}
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


def validate(payload):
    if not isinstance(payload, Mapping) or payload.get("tag_name") != TAG:
        raise ValueError("wrong release or invalid response")
    if payload.get("id") != RELEASE_ID:
        raise ValueError("release identity changed")
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
    for name, expected in EXPECTED.items():
        if name not in found:
            raise ValueError("required asset absent: " + name)
        asset = found[name]
        if asset.get("id") != expected["id"]:
            raise ValueError("asset identity changed: " + name)
        if asset.get("state") != "uploaded":
            raise ValueError("asset is not uploaded: " + name)
        size = asset.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError("invalid asset size: " + name)
        if size != expected["size"]:
            raise ValueError("asset size changed: " + name)
        digest = asset.get("digest")
        if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            raise ValueError("invalid digest metadata: " + name)
        if digest != expected["digest"]:
            raise ValueError("asset digest metadata changed: " + name)
    for name in found:
        if name not in EXPECTED:
            raise ValueError("unexpected asset added: " + name)
    return len(assets)


def validate_tag_ref(payload):
    """Detect drift of the lightweight historical tag reference, not authenticity."""
    if not isinstance(payload, Mapping) or payload.get("ref") != TAG_REF:
        raise ValueError("wrong tag ref or invalid response")
    obj = payload.get("object")
    if not isinstance(obj, Mapping) or obj.get("type") != "commit":
        raise ValueError("unexpected historical tag object type")
    if obj.get("sha") != TAG_COMMIT_SHA:
        raise ValueError("historical tag target changed")
    return obj["sha"]


def main():
    tag_mode = len(sys.argv) == 2 and sys.argv[1] == "--tag-ref"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not tag_mode):
        print("Usage: verifier [--tag-ref]", file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
        if tag_mode:
            target_sha = validate_tag_ref(payload)
        else:
            count = validate(payload)
    except (json.JSONDecodeError, ValueError) as error:
        print("Release metadata FAILED: " + str(error), file=sys.stderr)
        return 1
    if tag_mode:
        print(f"{TAG}: tag ref points to {target_sha} (snapshot comparison only).")
    else:
        print(f"{TAG}: {count} assets listed; four expected assets have metadata.")
    print("Metadata only; tag history, downloaded bytes, checksums, signatures, provenance and runtime NOT verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
