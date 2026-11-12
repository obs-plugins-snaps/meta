#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check that a snap name is still available in the Snap Store (T1 gate).

A required check on staging PRs: the staged plugin's snap name
(<plugin_name>-obs-studio) must be unregistered, so the name cannot be
squat by a third party between staging and graduation, and graduation's
`snapcraft register` cannot collide.

Uses the anonymous store API - no credentials are needed to *check*
availability, and the staging flow must not depend on store state.

Exit 0 when every name is available; exit 1 when a name is taken or the
API answer is inconclusive (fail loudly rather than wave it through).

Usage: uv run scripts/store_name_available.py <snap-name> [...]
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

API = "https://api.snapcraft.io/api/v1/snaps/details/{name}"


def status(name: str) -> tuple[str, str]:
    """Return (verdict, detail) for one snap name."""
    req = urllib.request.Request(
        API.format(name=name),
        headers={
            "Snap-Device-Series": "16",
            "X-Ubuntu-Series": "16",
            "X-Ubuntu-Architecture": "amd64",
            "User-Agent": "obs-plugins-snaps-staging",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            info = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "available", "unregistered in the Snap Store"
        return "inconclusive", f"store API returned HTTP {e.code}"
    except urllib.error.URLError as e:
        return "inconclusive", f"store API unreachable: {e.reason}"
    return "taken", f"registered (revision {info.get('revision')}, '{info.get('title', '')}')"[:120]


def main() -> int:
    names = sys.argv[1:]
    if not names:
        print("usage: store_name_available.py <snap-name> [...]", file=sys.stderr)
        return 2

    failures = []
    for name in names:
        verdict, detail = status(name)
        print(f"{name}: {verdict} ({detail})")
        if verdict != "available":
            failures.append(name)

    if failures:
        print(
            "\nSnap name(s) taken or inconclusive: " + ", ".join(failures),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
