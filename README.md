# Cadence Library

A local-first PWA over a reading history of 490 books. No dependencies, no build
step. Covers come from Open Library and are cached per device.

## Run it locally

    python3 -m http.server 8000

Open <http://localhost:8000>. A server is required: the app fetches
`data/cadence-index.csv` at runtime, and browsers block that from `file://`.

## How editing works

1. Tap a book, or use **Triage unknown**, and set its reading state.
2. The change saves to IndexedDB on that device immediately. It works offline.
3. The header shows how many changes are unsynced.
4. **Sync** writes them all to `data/cadence-index.csv` as a single commit.

Batching is deliberate. Committing on every tap would mean hundreds of commits
at a few seconds each; batched, a triage session is one readable diff.

## One-time setup for syncing

1. GitHub > Settings > Developer settings > Personal access tokens >
   **Fine-grained tokens** > Generate new token.
2. Repository access: **Only select repositories**, pick `cadence-library`.
3. Permissions > Repository permissions > **Contents: Read and write**.
4. Copy the token, open **Settings** in the app, paste it, Save.

The token is stored in IndexedDB on that device only. It is never committed.
Clearing site data removes it. Revoke it on GitHub at any time.

## Adding books

**+ Add book** takes a title and author. On iOS, tap the mic key on the keyboard
and dictate; any dictation tool that types into a text field works. The book
appears immediately, flagged `new`, and goes up with the next sync.

## Editing the CSV by hand

Still fine. Edit `data/cadence-index.csv`, commit, done. No build to run.

Three columns carry state, and they are different axes:

- `status` is how you got it: `owned`, `borrowed`, `wishlist`, `uncertain`.
- `read` is whether you read it: `yes`, `no`, a date, or blank for unknown.
- `deleted` is a date if you removed the book on purpose, blank otherwise.

To fix a book showing as Want to read that you have actually read, set `read`
to `yes`. Leave `status` alone.

## Deleting a book

Open the book, scroll to the bottom, Remove, then confirm. It disappears from
every view immediately and commits on the next sync.

Deletion leaves a tombstone: the row stays in the CSV with just the id, title
and author, everything else blanked, and a date in `deleted`. That is what stops
a future re-import from Amazon or Audible quietly putting the book back. The
note file, if there is one, is deleted outright.

Adding a book you previously deleted revives the same row rather than creating
a duplicate.

## Publish

Settings > Pages > Source: *Deploy from a branch*, branch `main`, folder
`/ (root)`. Then open `https://<user>.github.io/cadence-library/`.

On iPhone: open that URL in Safari, then Share > Add to Home Screen.

## How covers work

The data has no cover URLs. Each book is looked up on the Open Library search
API by cleaned title and first author, then pulled from `covers.openlibrary.org`.
Results, including misses, are cached in IndexedDB per device.

Lookups fire only for cards scrolling into view, six at a time, one attempt per
book per session. **Refresh covers** clears the cache and retries.
