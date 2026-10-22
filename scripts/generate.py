#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "jsonschema>=4",
# ]
# ///
"""Project plugin records into the tofu inputs.

The records under plugins/*.json (plus the *.description.md sidecar each
one requires) are the single source of truth, validated against
plugins/schema.json. This script is the single writer of:

  - repos/<snap_name>.tfvars   consumed by `tofu plan/apply` via the `just`
    recipes; committed and freshness-checked in CI

No copier data file is generated: the record itself is valid YAML (JSON is
a YAML subset) and is passed to copier directly. The template owns all
computed fields (snap_name, title, website default, package_url), so the
fill step only supplies what the template cannot know - the plugin_name
derived from the record filename and the description sidecar:

  copier copy --defaults \
    --data-file plugins/<snap_name>.json \
    --data plugin_name=<plugin_name> \
    --data description="$(cat plugins/<snap_name>.description.md)" \
    https://github.com/obs-plugins-snaps/template.git <repo>

Sidecars are authored normalized: one paragraph per line (list items one
per line), blank lines between blocks. The template re-wraps prose with
wordwrap(76) at fill time, so no transformation happens here.

Run `just gen` after editing records or sidecars; CI fails when the
generated tfvars are stale (see the check-generated recipe).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"
REPOS_DIR = ROOT / "repos"
SCHEMA_PATH = PLUGINS_DIR / "schema.json"

GENERATED_MARKER = (
    "# Generated from plugins/{record_name} by scripts/generate.py - DO NOT EDIT.\n"
    "# Run `just gen` after changing the record.\n"
)


def hcl_string(value: str) -> str:
    return (
        '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    )


def write_tfvars(snap_name: str, summary: str, record_name: str) -> None:
    out = REPOS_DIR / f"{snap_name}.tfvars"
    out.write_text(
        GENERATED_MARKER.format(record_name=record_name).rstrip("\n")
        + "\n\n"
        + f"snap_name = {hcl_string(snap_name)}\n"
        + f"summary   = {hcl_string(summary)}\n"
    )


def main() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    records = sorted(p for p in PLUGINS_DIR.glob("*.json") if p.name != "schema.json")
    if not records:
        sys.exit(f"no plugin records found in {PLUGINS_DIR}")

    REPOS_DIR.mkdir(exist_ok=True)

    for path in records:
        record = json.loads(path.read_text())
        jsonschema.validate(record, schema)

        snap_name = path.stem
        if not snap_name.endswith("-obs-studio"):
            sys.exit(f"{path.name}: record file name must be <plugin_name>-obs-studio")

        sidecar = path.with_suffix(".description.md")
        if not sidecar.exists():
            sys.exit(f"{path.name}: missing description sidecar {sidecar.name}")

        write_tfvars(snap_name, record["summary"], path.name)
        print(f"{path.name} -> {snap_name}.tfvars")

    print(f"processed {len(records)} record(s)")


if __name__ == "__main__":
    main()
