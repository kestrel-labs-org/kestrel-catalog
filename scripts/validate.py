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
TREND_WINDOWS = {"7d", "30d"}
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


def validate_explore() -> None:
    data = json.loads((ROOT / "listings" / "explore.json").read_text(encoding="utf-8"))
    explore = data.get("explore")
    if not isinstance(explore, list) or not explore:
        fail("explore.json missing explore list")
    if any(not str(name or "").strip() for name in explore):
        fail("explore.json has an empty hero name")
    curated = data.get("curated")
    if curated is not None:
        if not isinstance(curated, dict):
            fail("explore.json curated must be an object")
        for cat, block in curated.items():
            if cat != "All" and cat not in CATEGORIES:
                fail(f"explore.json curated unknown category {cat!r}")
            if not isinstance(block, dict) or not isinstance(block.get("apps"), list):
                fail(f"explore.json curated.{cat} must have an apps list")


def validate_staff_picks() -> int:
    data = json.loads((ROOT / "listings" / "staff_picks.json").read_text(encoding="utf-8"))
    picks = data.get("picks")
    if not isinstance(picks, list) or not picks:
        fail("staff_picks.json must have a non-empty picks array")
    ids: set[str] = set()
    for i, pick in enumerate(picks):
        if not isinstance(pick, dict):
            fail(f"staff pick {i} is not an object")
        check_banned(pick, str(pick.get("id") or f"pick {i}"))
        pid = str(pick.get("id") or "").strip()
        if not pid:
            fail(f"staff pick {i} missing id")
        if pid in ids:
            fail(f"duplicate staff pick id {pid}")
        ids.add(pid)
        if not str(pick.get("app_key") or "").strip():
            fail(f"{pid}: missing app_key")
        if not str(pick.get("note") or "").strip():
            fail(f"{pid}: missing note")
        if not str(pick.get("name") or "").strip():
            fail(f"{pid}: missing name")
        if not str(pick.get("summary") or "").strip():
            fail(f"{pid}: missing summary")
        if pick.get("category") not in CATEGORIES:
            fail(f"{pid}: unknown category {pick.get('category')!r}")
        try:
            int(pick.get("sort_order"))
        except (TypeError, ValueError):
            fail(f"{pid}: sort_order must be an integer")
        if pick.get("icon") and not http_url(pick.get("icon"), allow_empty=True):
            fail(f"{pid}: icon must be an http(s) URL")
    return len(picks)


def validate_trending() -> int:
    data = json.loads((ROOT / "listings" / "trending.json").read_text(encoding="utf-8"))
    if data.get("window") not in TREND_WINDOWS:
        fail("trending.json window must be 7d or 30d")
    if not str(data.get("updated_at") or "").strip():
        fail("trending.json missing updated_at")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        fail("trending.json must have a non-empty items array")
    ids: set[str] = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"trending item {i} is not an object")
        check_banned(item, str(item.get("id") or f"item {i}"))
        tid = str(item.get("id") or "").strip()
        if not tid:
            fail(f"trending item {i} missing id")
        if tid in ids:
            fail(f"duplicate trending id {tid}")
        ids.add(tid)
        if not str(item.get("name") or "").strip():
            fail(f"{tid}: missing name")
        if not str(item.get("summary") or "").strip():
            fail(f"{tid}: missing summary")
        if item.get("category") not in CATEGORIES:
            fail(f"{tid}: unknown category {item.get('category')!r}")
        if item.get("icon") and not http_url(item.get("icon"), allow_empty=True):
            fail(f"{tid}: icon must be an http(s) URL")
        for field in ("installs", "uninstalls", "flathub_downloads", "apt_downloads"):
            try:
                n = int(item.get(field))
            except (TypeError, ValueError):
                fail(f"{tid}: {field} must be an integer")
            if n < 0:
                fail(f"{tid}: {field} must be >= 0")
        try:
            score = float(item.get("score"))
        except (TypeError, ValueError):
            fail(f"{tid}: score must be a number")
        if score < 0:
            fail(f"{tid}: score must be >= 0")
    return len(items)


def _as_str_list(value: object, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        fail(f"{label} must be a list of strings")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            fail(f"{label} must be a list of strings")
        out.append(item.strip())
    return out


def validate_categories() -> int:
    path = ROOT / "listings" / "categories.json"
    if not path.is_file():
        fail("listings/categories.json is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        fail("listings/categories.json must have version 1")
    rows = data.get("categories")
    if not isinstance(rows, list) or not rows:
        fail("listings/categories.json must have a non-empty categories array")
    names: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            fail(f"categories[{i}] is not an object")
        name = str(row.get("name") or "").strip()
        if name not in CATEGORIES:
            fail(f"categories[{i}]: unknown name {name!r}")
        if name in names:
            fail(f"duplicate category {name}")
        names.append(name)
        _as_str_list(row.get("tokens"), f"{name}.tokens")
        _as_str_list(row.get("exclude"), f"{name}.exclude")
        _as_str_list(row.get("keywords"), f"{name}.keywords")
        _as_str_list(row.get("strong_keywords"), f"{name}.strong_keywords")
    missing = CATEGORIES - set(names)
    if missing:
        fail(f"listings/categories.json missing {sorted(missing)}")
    extra = set(names) - CATEGORIES
    if extra:
        fail(f"listings/categories.json extra names {sorted(extra)}")
    return len(names)


def validate_category_map() -> int:
    path = ROOT / "listings" / "category_map.json"
    if not path.is_file():
        fail("listings/category_map.json is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        fail("listings/category_map.json must have version 1")
    apps = data.get("apps")
    if not isinstance(apps, list):
        fail("listings/category_map.json must have an apps array")
    ids: set[str] = set()
    for i, app in enumerate(apps):
        if not isinstance(app, dict):
            fail(f"category_map[{i}] is not an object")
        key = str(app.get("id") or "").strip()
        if not key:
            fail(f"category_map[{i}] missing id")
        if key in ids:
            fail(f"duplicate category_map id {key}")
        ids.add(key)
        cat = app.get("category")
        if cat not in CATEGORIES:
            fail(f"{key}: unknown category {cat!r}")
        also = app.get("also_categories")
        if also is not None:
            if not isinstance(also, list):
                fail(f"{key}: also_categories must be a list")
            for extra in also:
                if extra not in CATEGORIES:
                    fail(f"{key}: unknown also_category {extra!r}")
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
    validate_explore()
    n_picks = validate_staff_picks()
    n_trend = validate_trending()
    n_cats = validate_categories()
    n_map = validate_category_map()
    print(
        f"ok: {n_apps} listings, {n_picks} staff picks, {n_trend} trending, "
        f"{n_cats} categories, {n_map} category map"
    )


if __name__ == "__main__":
    main()
