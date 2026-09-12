# Cadence Library

A static PWA over a reading history of 490 books. No build tooling at runtime, no
dependencies. Covers come from Open Library and are cached per device.

## Run it locally

    python3 -m http.server 8000

Then open <http://localhost:8000>. The service worker needs `localhost` or HTTPS.
Opening `index.html` off the file system renders the grid but skips offline caching.

## Update the data

`data/cadence-index.csv` is the database. `index.html` is generated from it.

1. Edit the CSV.
2. `python3 build.py`
3. Commit both files together.

`build.py` prints the row count and the read/reading/want split, so a bad edit is
visible immediately.

## Push to the existing GitHub repo

From the folder, with the remote already created:

    git init
    git add .
    git commit -m "Cadence Library: CSV-backed build"
    git branch -M main
    git remote add origin git@github.com:<user>/cadence-library.git
    git push -u origin main

If the repo already has commits, `git pull --rebase origin main` before pushing.

## Publish

Settings > Pages > Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.
Wait for the green check, then open `https://<user>.github.io/cadence-library/`.

On iPhone: open that URL in Safari, then Share > Add to Home Screen. The manifest
gives it a standalone window and the warm paper background.

## How covers work

The data has no cover URLs. Each book is looked up on the Open Library search API
by cleaned title and first author, then the cover is pulled from
`covers.openlibrary.org` at medium size. Results, including misses, are cached in
IndexedDB per device, so the second visit is instant.

Lookups fire only for cards scrolling into view, six at a time, one attempt per
book per session. "Refresh covers" clears the cache and retries.

## Files

| Path | Role |
| --- | --- |
| `data/cadence-index.csv` | The database |
| `build.py` | CSV to `index.html` |
| `template.html` | The app source. Edit this, not `index.html` |
| `index.html` | Generated, committed for Pages |
| `sw.js` | Service worker |
| `manifest.webmanifest`, `icon-192.png`, `icon-512.png` | Install metadata |
| `CLAUDE.md` | Project rules and known problems |
