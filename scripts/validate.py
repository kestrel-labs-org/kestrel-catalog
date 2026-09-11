#!/usr/bin/env python3
"""Lint kestrel-catalog listing files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "Browsers",
    "Communication",
    "Media & Entertainment",
    "Gaming",
    "Productivity & Office",
    "Cloud Storage & Sync",
    "Creative & Design",
    "Utilities & Tools",
    "Development",
    "AI",
    "Security",
}
KINDS = {"repo", "deb", "ppa", "link", "appimage"}
BANNED = {"promote", "sponsored", "disclosure"}
AGE_RATINGS = {"everyone", "everyone-10", "teen", "mature", "adult"}
REPO_REQUIRED = ("key_url", "keyring", "deb_line", "list_file")


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def http_url(value: object, *, allow_empty: bool = False) -> bool:
    text = str(value or "").strip()
    if not text:
        return allow_empty
    parsed = urlparse(text)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def check_banned(obj: dict, label: str) -> None:
    for key in BANNED:
        if key in obj:
            fail(f"{label}: banned field {key}")


def validate_vendor(allow_verified: bool) -> int:
    path = ROOT / "listings" / "vendor_apps.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    apps = data.get("apps")
    if not isinstance(apps, list) or not apps:
        fail("listings/vendor_apps.json must have a non-empty apps array")
    names: set[str] = set()
    for i, app in enumerate(apps):
        if not isinstance(app, dict):
            fail(f"app {i} is not an object")
        check_banned(app, str(app.get("name") or f"app {i}"))
        name = str(app.get("name") or "").strip()
        if not name:
            fail(f"app {i} missing name")
        if name in names:
            fail(f"duplicate name {name}")
        names.add(name)
        if app.get("category") not in CATEGORIES:
            fail(f"{name}: unknown category {app.get('category')!r}")
        also = app.get("also_categories")
        if also is not None:
            if not isinstance(also, list):
                fail(f"{name}: also_categories must be a list")
            for extra in also:
                if extra not in CATEGORIES:
                    fail(f"{name}: unknown also_category {extra!r}")
        kind = app.get("kind")
        if kind not in KINDS:
            fail(f"{name}: unknown kind {kind!r}")
        if not str(app.get("summary") or "").strip():
            fail(f"{name}: missing summary")
        if not http_url(app.get("homepage")):
            fail(f"{name}: homepage must be an http(s) URL")
        if app.get("icon") and not http_url(app.get("icon")):
            fail(f"{name}: icon must be an http(s) URL")
        shots = app.get("screenshots")
        if shots is not None:
            if not isinstance(shots, list):
                fail(f"{name}: screenshots must be a list")
            for url in shots:
                if not http_url(url):
                    fail(f"{name}: screenshot must be an http(s) URL")
        if app.get("verified") is True and not allow_verified:
            fail(f"{name}: verified: true is maintainer-only")
        rating = app.get("age_rating")
        if rating is not None and rating not in AGE_RATINGS:
            fail(f"{name}: unknown age_rating {rating!r}")

        if kind == "link":
            if any(app.get(k) for k in ("package", "flatpak", "snap", "deb_url", "ppa")):
                fail(f"{name}: link-kind listings must not claim an installable package")
            if app.get("link_url") and not http_url(app.get("link_url")):
                fail(f"{name}: link_url must be an http(s) URL")
        elif kind == "deb":
            if not str(app.get("package") or "").strip():
                fail(f"{name}: deb listings require package")
            if not http_url(app.get("deb_url")):
                fail(f"{name}: deb listings require an http(s) deb_url")
        elif kind == "repo":
            if not str(app.get("package") or "").strip():
                fail(f"{name}: repo listings require package")
            repo = app.get("repo")
            if not isinstance(repo, dict):
                fail(f"{name}: repo listings require a repo object")
            for field in REPO_REQUIRED:
                if not str(repo.get(field) or "").strip():
                    fail(f"{name}: repo.{field} is required")
            if not http_url(repo.get("key_url")):
                fail(f"{name}: repo.key_url must be an http(s) URL")
        elif kind == "ppa":
            if not str(app.get("package") or "").strip():
                fail(f"{name}: ppa listings require package")
            ppa = str(app.get("ppa") or "").strip()
            if not ppa.startswith("ppa:"):
                fail(f"{name}: ppa must look like ppa:team/archive")
        elif kind == "appimage":
            github = str(app.get("github") or "").strip()
            url = str(app.get("url") or "").strip()
            if github:
                if github.count("/") != 1:
                    fail(f"{name}: github must be owner/repo")
            elif url:
                if not http_url(url):
                    fail(f"{name}: url must be an http(s) URL")
                if not str(app.get("watch") or "").strip():
                    fail(f"{name}: url AppImages require watch")
            else:
                fail(f"{name}: appimage listings require github or url")
    return len(apps)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-verified",
        action="store_true",
        help="Allow verified: true (same-repo maintainers and main).",
    )
    args = parser.parse_args()
    n_apps = validate_vendor(args.allow_verified)
    print(f"ok: {n_apps} vendor listings")


if __name__ == "__main__":
    main()
