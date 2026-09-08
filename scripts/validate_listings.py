#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Jason Miller (Kestrel Labs)
# SPDX-License-Identifier: CC0-1.0
"""Validate listing YAML files against the catalog schema."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
LISTINGS = ROOT / "listings"
REQUIRED = ("id", "name", "summary", "description", "categories", "licenses", "homepage", "source")
KNOWN_CATEGORIES = {
    "office",
    "graphics",
    "development",
    "system",
    "games",
    "internet",
    "multimedia",
    "utilities",
}


def main() -> int:
    errors = 0
    warnings = 0
    files = sorted(LISTINGS.glob("*.yml")) + sorted(LISTINGS.glob("*.yaml"))
    files = [p for p in files if p.name.lower() != "readme.md"]
    if not files:
        print("No listing files found under listings/")
        return 1

    for path in files:
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict):
            print(f"ERROR {path.name}: root must be a mapping")
            errors += 1
            continue
        for key in REQUIRED:
            if not data.get(key):
                print(f"ERROR {path.name}: missing required field '{key}'")
                errors += 1
        listing_id = data.get("id")
        stem = path.stem
        if listing_id and listing_id != stem:
            print(f"ERROR {path.name}: id '{listing_id}' must match filename '{stem}'")
            errors += 1
        for url_key in ("homepage", "source", "icon"):
            url = data.get(url_key)
            if url and not str(url).startswith("https://"):
                print(f"ERROR {path.name}: {url_key} must be https://")
                errors += 1
        for url in data.get("screenshots") or []:
            if not str(url).startswith("https://"):
                print(f"ERROR {path.name}: screenshot URL must be https://")
                errors += 1
        for cat in data.get("categories") or []:
            if cat not in KNOWN_CATEGORIES:
                print(f"WARN  {path.name}: unknown category '{cat}'")
                warnings += 1

    print(f"Validated {len(files)} listing(s): {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
