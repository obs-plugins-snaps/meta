#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "jsonschema>=4",
#   "pyyaml>=6",
# ]
# ///
"""Policy lint for staging directories (T1 gate; failure blocks the PR).

One staging PR stages one plugin: a record under plugins/ plus a
template-rendered tree under staging/<plugin_name>/. This script enforces
the invariants the flow depends on, with direct error messages:

  - the record exists, matches its filename, and validates against
    plugins/schema.json, with the required .description.md sidecar
  - snapcraft.yaml pins an upstream source: exactly one part carries
    source-tag, pointing at the record's source_url (default-branch HEAD
    is not packageable; the version-drift lesson)
  - source-tag complies with the snap version charset and 32-char cap
    (mirrors the template's copier validator and snapcraft's
    _validate_version_name)
  - version/adopt-info mutual exclusion (they are mutually exclusive;
    part-level adopt-info is invalid)
  - grade: devel (the stable promotion is the human functional gate)
  - base: core24 and the obs-plugins content slot the obs-studio snap
    consumes
  - the rendered scaffold is actually present (snapcraft.yaml, CI
    workflow, .copier-answers.yml), so a record-only PR cannot sneak
    through
  - summary in snapcraft.yaml matches the record (catches hand-edits
    desyncing the two)

Run over every staging/ directory; PRs that only clean up merged staging
trees (none left) pass trivially.

Usage: uv run scripts/staging_lint.py [--root .]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

VERSION_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9:.+~-]{0,30}[a-zA-Z0-9+~])?$")


class Failure(Exception):
    """One lint failure; collected and reported at the end."""


def check_record(root: Path, name: str, schema: dict) -> dict:
    record_path = root / "plugins" / f"{name}-obs-studio.json"
    if not record_path.is_file():
        raise Failure(f"plugins/{name}-obs-studio.json: record missing for staging/{name}")
    record = json.loads(record_path.read_text())
    try:
        jsonschema.validate(record, schema)
    except jsonschema.ValidationError as e:
        raise Failure(f"plugins/{name}-obs-studio.json: schema violation: {e.message}") from e
    sidecar = root / "plugins" / f"{name}-obs-studio.description.md"
    if not sidecar.is_file():
        raise Failure(f"plugins/{name}-obs-studio.description.md: sidecar missing")
    return record


def check_snapcraft(root: Path, name: str, record: dict) -> None:
    path = root / "staging" / name / "snap" / "snapcraft.yaml"
    if not path.is_file():
        raise Failure(f"staging/{name}: snap/snapcraft.yaml missing (template not rendered?)")
    snap = yaml.safe_load(path.read_text())

    # Version/adopt-info mutual exclusion (adopt-info is top-level only).
    has_version = "version" in snap
    has_adopt = "adopt-info" in snap
    if has_version and has_adopt:
        raise Failure(f"staging/{name}: version and adopt-info are mutually exclusive")
    if not has_version and not has_adopt:
        raise Failure(f"staging/{name}: neither version nor adopt-info set")
    if has_adopt:
        adopted = snap["adopt-info"]
        parts = snap.get("parts", {})
        if adopted not in parts:
            raise Failure(
                f"staging/{name}: adopt-info references part '{adopted}', which does not exist"
            )

    # The functional gate is human; staging must ask for devel.
    if snap.get("grade") != "devel":
        raise Failure(f"staging/{name}: grade must be 'devel' (got {snap.get('grade')!r})")

    if snap.get("base") != "core24":
        raise Failure(f"staging/{name}: base must be 'core24' (got {snap.get('base')!r})")

    # The obs-studio snap consumes this slot to mount the plugins.
    slot = snap.get("slots", {}).get("obs-plugins")
    if not slot or slot.get("interface") != "content":
        raise Failure(f"staging/{name}: slots.obs-plugins content slot missing")

    # Exactly one pinned source; it must be the record's source_url.
    tagged = [
        (pname, part)
        for pname, part in snap.get("parts", {}).items()
        if "source-tag" in part
    ]
    if len(tagged) != 1:
        raise Failure(
            f"staging/{name}: expected exactly one part with source-tag, found {len(tagged)}"
        )
    pname, part = tagged[0]
    tag = part["source-tag"]
    if not VERSION_RE.match(str(tag)):
        raise Failure(
            f"staging/{name}: source-tag '{tag}' violates the snap version charset "
            "(alphanumeric start/end; letters, digits and .:+~- inside; max 32 chars)"
        )
    if record.get("source_url"):
        source = str(part.get("source", "")).removesuffix(".git")
        expected = record["source_url"].removesuffix(".git")
        if source != expected:
            raise Failure(
                f"staging/{name}: part '{pname}' source {source!r} does not match "
                f"the record's source_url {expected!r}"
            )

    # The scaffold summary must not drift from the record.
    if snap.get("summary") != record["summary"]:
        raise Failure(
            f"staging/{name}: snapcraft.yaml summary does not match the record "
            "(hand-edit the record, then re-render)"
        )

    # Evidence that the template render actually happened.
    for evidence in (".github/workflows/ci.yaml", ".copier-answers.yml"):
        if not (root / "staging" / name / evidence).is_file():
            raise Failure(f"staging/{name}/{evidence}: missing (template not rendered?)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="meta repository root")
    args = parser.parse_args()
    root = args.root

    schema = json.loads((root / "plugins" / "schema.json").read_text())

    staged = sorted(
        p.name for p in (root / "staging").glob("*") if p.is_dir()
    ) if (root / "staging").is_dir() else []
    if not staged:
        print("No staging directories: nothing to lint (cleanup PR?).")
        return 0

    failures: list[str] = []
    for name in staged:
        try:
            record = check_record(root, name, schema)
            check_snapcraft(root, name, record)
            print(f"staging/{name}: OK")
        except Failure as e:
            failures.append(str(e))

    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(f"\n{len(failures)} staging check(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
