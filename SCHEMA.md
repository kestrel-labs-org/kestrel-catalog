# kestrel-catalog listing schema

This is the public source of truth for Kestrel App Manager listings.
Community submits listings via pull request. Kestrel Labs reviews
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
- `url` (download URL, may include `{arch}` / `{x64}`) **and** `watch` (lowercase slug `[a-z0-9-]`, e.g. `lm-studio-linux`; stable id Kestrel owns)

Optional: `self_update` (app updates itself), `apparmor` (needs a userns profile on Ubuntu 24.04+), `deb_asset` (`.deb` on the same GitHub release).

### Curated category names

`Browsers`, `Communication`, `Media & Entertainment`, `Gaming`,
`Productivity & Office`, `Cloud Storage & Sync`, `Creative & Design`,
`Utilities & Tools`, `Development`, `AI`, `Security`.

`category` on a vendor row may be **AI**. The App Manager also maps Flathub
and Snap AI apps from local keywords. Explore Popular, Newest, and ratings
come from Kestrel Labs Cloud at catalog rebuild, not from this repo.
