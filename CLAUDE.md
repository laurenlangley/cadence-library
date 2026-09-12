# Cadence Library

A local-first PWA over Lauren's reading history. No framework, no bundler, no
build step. GitHub Pages serves this folder as-is.

## The one rule

`data/cadence-index.csv` is the database. `index.html` reads it at runtime.

There is no build step and no generated file. Edit the CSV and the app picks it
up on the next load. Edit `index.html` and it is live immediately. Nothing is
derived, so nothing can drift.

The app also writes the CSV: edits go to IndexedDB first, then sync pushes them
here as one commit via the GitHub Contents API. A hand edit and an app edit are
the same kind of change to the same file.

## Layout

| Path | Role |
| --- | --- |
| `data/cadence-index.csv` | The database. Read at runtime, written by sync. |
| `index.html` | The whole app. Parser, UI, editing, sync. |
| `notes/*.md` | Per-book notes, fetched on demand when a book is opened. |
| `sw.js` | Service worker. Network-first shell, cache-first covers. |
| `manifest.webmanifest`, `icon-*.png` | Home-screen install. |

The app needs a server. Relative `fetch` is blocked from `file://`, so opening
`index.html` off disk shows a load error by design. Use
`python3 -m http.server 8000`.

## CSV schema

`id, title, author, format, status, read, pct_complete, first_seen, last_seen, events, sources, note_file`

- `id` is a stable slug of title plus author, deduplicated with a numeric suffix.
  **Never renumber or regenerate ids.** The app's edit overlay is keyed on them,
  and changing one orphans any unsynced edit sitting on Lauren's phone.
- `status` is the **acquisition** axis: `owned`, `borrowed`, `wishlist`,
  `uncertain`, `reading`, `finished`, `leslie`.
- `read` is the **reading** axis and is authoritative for it. `yes`/`y`/`true`/`1`
  or a date means read; `no` means explicitly not read; blank falls through to
  `status`. A book can be `owned` and `read: yes` at once. Never edit `status`
  to fix a reading-state display.
- Extra columns pass through untouched, including through sync.

`semantic()` in `index.html` is the single place the read/reading/want rule lives.

## Sync

Owner and repo are derived from the Pages hostname and path, overridable in
Settings. The token is a fine-grained PAT with Contents read and write on this
repo only, stored in IndexedDB on the device. It is never written to the repo,
and there is no server to leak it.

Sync merges the overlay onto the **remote** copy of the CSV, not the local one,
so edits made on another device survive. A 409 means the file moved underneath
it; the fix is reload and retry, never force.

## Known problems, in priority order

1. **436 of 490 books have an unknown reading state.** Vendor exports record
   acquisition, never completion. Only Lauren knows, one book at a time. Triage
   mode exists for exactly this, and the Unknown filter shows what is left.
2. **227 books have no author**, and 79 titles are truncated mid-word at 76
   characters by the Amazon export. Cover lookup hits Open Library by title and
   author, so these mostly miss. An ISBN column would fix much of it; the Drive
   index has ISBNs for some rows.
3. **Non-books in the data**: "MAGCREDIBLE Magnets", "Mighty Bright-Blu-Xflex
   2-Lght", and one row titled "Not Available" with 14 events. Expect more, since
   the Amazon order export cannot tell a book from a book light. Needs an audit.
4. **Notes exist for 6 books.** There is no way to write one from the app yet;
   they are hand-authored markdown in `notes/`.

## Drive is no longer the inbox

Capture happens in the app now, via Add book. The Drive `Cadence` folder still
holds the older curated index and the original note files, and is an archive.
The earlier plan to sync Drive into this repo is superseded. Do not build it
without asking.

## Working style

Lauren is a designer with 25 years of experience, technically strong but not a
career software engineer. Be blunt, back claims with specifics, argue with a plan
that has a hole in it before helping execute it. Visual quality is the work, not
decoration. No em dashes.
