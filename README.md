<p align="center">
  <img src="https://raw.githubusercontent.com/kestrel-labs-org/kestrel-brand/main/banners/readme-banner-1200x300.png" alt="Kestrel Labs — Open source tools for Linux" width="100%">
</p>

# kestrel-catalog

Open data for **Kestrel App Manager**: vendor listings (including AI-tagged
apps). Community submits listings via pull request. Kestrel Labs reviews
and merges.

This is metadata, not a warranty of the software. See [CONTENT_POLICY.md](CONTENT_POLICY.md).

License: [CC0-1.0](LICENSE). By submitting a pull request you dedicate the
listing metadata to the public domain.

## Files

| Path | What it is |
|---|---|
| `listings/vendor_apps.json` | Vendor listings (managed install, AppImage, or website) |
| `SCHEMA.md` | Field contract |
| `CONTENT_POLICY.md` | What we accept |

Explore Popular, Newest, store categories, and ratings are built by the
App Manager and Kestrel Labs Cloud. This repo does not ship staff picks,
trending snapshots, or a category taxonomy.

The App Manager ships a copy of `vendor_apps.json` and refreshes it from
this repo on a schedule. The library still works from the bundled copy if
GitHub is unreachable.

## Submit a listing

1. Fork this repository.
2. Add or edit an object in `listings/vendor_apps.json` following [SCHEMA.md](SCHEMA.md).
3. Open a pull request. The checklist in the PR template is the review bar.
4. CI runs `python scripts/validate.py`. Fix any lint errors.

Do not set `verified: true` — that flag is maintainer-only after publisher
verification. Do not add `promote`, `sponsored`, or `disclosure`.

## Validate locally

```bash
python3 scripts/validate.py
```

## Publish updates (maintainers)

This checkout is the GitHub source of truth:
https://github.com/kestrel-labs-org/kestrel-catalog

```bash
git push origin main
```

Confirm Cloud `.env` has `GITHUB_TOKEN` (scopes `contents:write` and
`pull_requests:write`), `GITHUB_CATALOG_REPO=kestrel-labs-org/kestrel-catalog`,
`GITHUB_CATALOG_BRANCH=main`, and `KESTREL_CATALOG_REPO` pointing at this
checkout. Restart Cloud after the token is set.

`.github/CODEOWNERS` is `* @kestrellabsAdmin` — that must match the GitHub username that
should own listing reviews.

`listings/vendor_apps.json` is over 1 MB, so Cloud commits it with `git push`
using the token instead of the Contents API.

Do not click **Ingest catalog repo** to publish admin edits. Ingest pulls this
checkout into Cloud SQLite; Save writes Cloud back to these files (and GitHub).

## Related

- App Manager client: `kestrel-app-manager`
- Optional cloud service: https://kestrellabs.cloud
- Project site: https://kestrellabs.org
