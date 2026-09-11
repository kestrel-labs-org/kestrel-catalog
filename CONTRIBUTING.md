# Contributing to kestrel-catalog

Listings are open data under CC0-1.0. There is no CLA. By opening a pull
request you dedicate the submitted metadata to the public domain, as stated
in the PR template.

## What to send

- New or updated app objects in `listings/vendor_apps.json`
- Follow [SCHEMA.md](SCHEMA.md) and [CONTENT_POLICY.md](CONTENT_POLICY.md)
- One app (or a tight group of related apps) per pull request when you can

Staff picks, trending snapshots, and category taxonomy are not part of
this repo. Suggest a listing in the PR description; do not add extra JSON
files.

## Checks

```bash
python3 scripts/validate.py
```

`verified: true` is rejected on community pull requests.

## Review

Kestrel Labs reviews every listing before merge. Being listed is not a
warranty of the software.
