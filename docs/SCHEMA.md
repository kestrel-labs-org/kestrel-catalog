# Listing schema

Each app is a single YAML file in `listings/`, named `{id}.yml` where `id` is a stable lowercase slug (`[a-z0-9-]+`).

## Required fields

| Field | Type | Notes |
|---|---|---|
| `id` | string | Must match the filename (without `.yml`) |
| `name` | string | Display name |
| `summary` | string | One-line description (≤120 chars recommended) |
| `description` | string | Longer markdown-friendly description |
| `categories` | string[] | e.g. `office`, `graphics`, `development`, `system`, `games`, `internet`, `multimedia`, `utilities` |
| `licenses` | string[] | SPDX ids where possible (e.g. `GPL-3.0-or-later`) |
| `homepage` | URL | Project homepage |
| `source` | URL | Source repository or upstream project page |

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `icon` | URL | HTTPS URL to an icon (prefer SVG/PNG) |
| `screenshots` | URL[] | HTTPS image URLs |
| `version` | string | Latest known upstream version (informational) |
| `flatpak_id` | string | If also distributed as Flatpak |
| `deb` | object | `{ "url": "...", "sha256": "..." }` for a direct `.deb` |
| `tags` | string[] | Freeform search tags |
| `maintainer` | object | `{ "name": "...", "email": "..." }` for the listing, not necessarily upstream |

## Example

```yaml
id: example-app
name: Example App
summary: A short one-liner for the store grid.
description: |
  Longer description shown on the detail page.

  Supports multiple paragraphs.
categories:
  - utilities
licenses:
  - GPL-3.0-or-later
homepage: https://example.org
source: https://github.com/example/example-app
tags:
  - linux
  - example
```

## Validation rules (CI)

- Filename is `{id}.yml` and `id` matches the file field
- All required fields present and non-empty
- URLs use `https://`
- `categories` values are from the known set (unknown values warn, not fail, until the taxonomy freezes)
- YAML parses cleanly
