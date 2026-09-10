# kestrel-catalog listing schema

This repo is the public source of truth for Kestrel App Manager listings,
Explore shelves, staff picks, trending snapshots, and the curated category
taxonomy. Community submits listings via pull request. Kestrel Labs reviews
and merges.

By submitting a pull request you dedicate this listing metadata to the
public domain under CC0-1.0.

Do **not** include `promote`, `sponsored`, or `disclosure`. Paid placement
fields are retired.

`verified: true` is **maintainer-only**. Community pull requests must leave
it unset (or `false`). Kestrel sets it after publisher verification.

---

## `listings/vendor_apps.json`

Shape: `{ "version": 1, "apps": [ … ] }`.

Each app is an object:

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Display name. Unique in the file. |
| `category` | yes | One of the curated Explore categories (see below). |
| `kind` | yes | `repo`, `deb`, `ppa`, `link` (website / download page), `appimage` |
| `summary` | yes | Short description |
| `homepage` | yes | `http(s)` URL |
| `description` | no | Longer about text |
| `icon` | no | `http(s)` image URL |
| `screenshots` | no | List of `http(s)` image URLs |
| `package` / `flatpak` / `snap` | no | Distro / Flathub / Snap ids |
| `also_categories` | no | Extra curated category names |
| `unofficial` | no | Community-maintained channel, not the original vendor |
| `verified` | no | Publisher verified by Kestrel. Maintainers only. |
| `age_rating` | no | When known: `everyone`, `everyone-10`, `teen`, `mature`, `adult`. Not required on existing rows. |

### Kind-specific fields

**`repo`** — vendor apt repository.

| Field | Required | Notes |
|---|---|---|
| `package` | yes | Apt package name |
| `repo` | yes | Object with `key_url`, `keyring`, `deb_line`, `list_file`; optional `dearmor` (bool) |

**`deb`** — a `.deb` URL (optionally a repo-setup package).

| Field | Required | Notes |
|---|---|---|
| `package` | yes | Apt package name |
| `deb_url` | yes | Stable “latest” URL — never a versioned link if you can avoid it |
| `deb_is_setup` | no | The `.deb` only registers the vendor repo; the app package is installed from it afterwards |

**`ppa`**

| Field | Required | Notes |
|---|---|---|
| `package` | yes | Apt package name |
| `ppa` | yes | `ppa:<team>/<archive>` |

**`link`** — vendor website / download page. The library shows the card and
opens this URL (Install Instructions). Users can sideload an AppImage they
download there. Not a managed install.

| Field | Required | Notes |
|---|---|---|
| `link_url` | no | Install-instructions or download page (defaults to `homepage`) |

Must **not** claim `package`, `flatpak`, `snap`, `deb_url`, or `ppa`. Optional
extra AppImage fields (`github` / `url`+`watch`) add a managed AppImage tab
on the same card.

**`appimage`** — portable binary.

Provide **either**:

- `github` (`owner/repo`) and optional `asset` glob (`{arch}` / `{x64}` / `{amd64}`), or
- `url` (download URL, may include `{arch}` / `{x64}`) **and** `watch` (stable id Kestrel owns)

Optional: `self_update` (app updates itself), `apparmor` (needs a userns profile on Ubuntu 24.04+), `deb_asset` (`.deb` on the same GitHub release).

### Curated category names

`Browsers`, `Communication`, `Media & Entertainment`, `Gaming`,
`Productivity & Office`, `Cloud Storage & Sync`, `Creative & Design`,
`Utilities & Tools`, `Development`, `AI`, `Security`.

---

## `listings/explore.json`

Predetermined hero and shelf **names**. Not a paid placement product.

| Field | Required | Notes |
|---|---|---|
| `version` | yes | Integer, currently `1` |
| `explore` | yes | List of display names for the hero strip |
| `curated` | no | Map of category name → `{ "apps": [names], "subs": { … } }` |
| `categories` | no | FreeDesktop-style shelves of display names |

Names do not have to exist in `vendor_apps.json`. Explore mixes vendor
listings with distro/archive apps the client already knows.

---

## `listings/staff_picks.json`

Hand-curated Explore shelf. The client resolves `app_key` / `name` against
the local catalog (same as Explore).

```json
{
  "version": 1,
  "picks": [
    {
      "id": "firefox",
      "app_key": "Firefox",
      "note": "Why this is picked",
      "sort_order": 0,
      "name": "Firefox",
      "icon": "",
      "summary": "Independent web browser from Mozilla",
      "category": "Browsers"
    }
  ]
}
```

| Field | Required |
|---|---|
| `id` | yes (unique) |
| `app_key` | yes — display name the client resolves |
| `note` | yes |
| `sort_order` | yes (integer) |
| `name` | yes |
| `icon` | no (`http(s)` URL or empty) |
| `summary` | yes |
| `category` | yes — curated category name |

---

## `listings/trending.json`

A **snapshot**, not live telemetry. Seeded for launch so GitHub-only clients
are not empty. Kestrel Labs Cloud may later commit updated rankings from
anonymous install signals.

```json
{
  "version": 1,
  "window": "7d",
  "updated_at": "2026-09-09T00:00:00Z",
  "items": [
    {
      "id": "Firefox",
      "name": "Firefox",
      "icon": "",
      "summary": "Independent web browser from Mozilla",
      "category": "Browsers",
      "installs": 0,
      "uninstalls": 0,
      "flathub_downloads": 0,
      "apt_downloads": 0,
      "score": 12
    }
  ]
}
```

`window` is `7d` or `30d`. `id` is unique. `score` is a non-negative number.
Count fields are non-negative integers. `id` / `name` are display names the
client resolves; they need not exist in `vendor_apps.json`.

---

## `listings/categories.json`

Taxonomy the App Manager uses for Explore shelves. Tokens are AppStream /
FreeDesktop category strings. Keywords match name/summary/package when
tokens are empty or insufficient (AI has no AppStream token).

```json
{
  "version": 1,
  "categories": [
    {
      "name": "AI",
      "tokens": [],
      "exclude": [],
      "keywords": ["qwen", "llm", "language model"],
      "strong_keywords": ["qwen", "llm"]
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `version` | yes | Integer, currently `1` |
| `categories` | yes | Exactly the 11 curated names, in display order |
| `name` | yes | Curated category name |
| `tokens` | no | AppStream tokens that land an app on this shelf |
| `exclude` | no | AppStream tokens that must not land here |
| `keywords` | no | Name/summary phrases (AI and similar) |
| `strong_keywords` | no | Product-level signals; a lone generic token is not enough to recategorize a browser or game |

Do **not** list vendor apps here. Vendor `category` lives on each
`vendor_apps.json` row.

---

## `listings/category_map.json`

Overrides for **non-vendor** apps (Snap / Flatpak / apt group keys the client
already syncs — the same Key shown on the Cloud Catalog mirror). Not a full
app listing. Vendor apps keep using `vendor_apps.json` `category` /
`also_categories`.

```json
{
  "version": 1,
  "apps": [
    { "id": "qwen-3.6", "category": "AI", "also_categories": [] }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Catalog group key (unique in this file) |
| `category` | yes | Curated category name |
| `also_categories` | no | Extra curated names |
