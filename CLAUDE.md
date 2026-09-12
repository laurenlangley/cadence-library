# Cadence Library

A static PWA over Lauren's reading history. No framework, no bundler, no runtime
dependencies. GitHub Pages serves this folder as-is.

## The one rule

`data/cadence-index.csv` is the database. `index.html` is generated from it.

Never hand-edit the `BOOKS` array inside `index.html`. Edit the CSV, then:

    python3 build.py

Commit the CSV and the regenerated `index.html` together. A commit that changes
one without the other is a bug.

## Layout

| Path | Role |
| --- | --- |
| `data/cadence-index.csv` | The database. Source of truth. |
| `build.py` | CSV to `index.html`. Also derives the read/reading/want state. |
| `template.html` | The app. Contains `/*__BOOKS__*/` where data is injected. |
| `index.html` | Generated. Committed because Pages needs it. |
| `sw.js` | Service worker. Network-first shell, cache-first covers. |
| `manifest.webmanifest`, `icon-*.png` | Home-screen install. |

Interface changes go in `template.html`, then rebuild. Editing `index.html`
directly means the next build silently reverts you.

## CSV schema

`title, author, format, status, pct_complete, first_seen, last_seen, events, sources, note_file`

- `title`, `author`, `format`, `status` are required by `build.py`.
- `status` values in use: `owned`, `borrowed`, `finished`, `wishlist`, `uncertain`, `reading`, `leslie`.
- Extra columns pass through untouched. Adding a column does not require a code change.
- Rows are ordered newest `first_seen` first. Keep it that way; nothing depends on it, but it makes diffs readable.

## Known problems, in priority order

1. **The three-state model is broken.** `semantic()` in `build.py` maps everything
   that isn't `finished` or `reading` to `want`, which puts 438 of 490 books in one
   bucket and makes the Read/Reading/Want filter decorative. Fixing this needs
   better source data, not a better function.
2. **227 books have no author**, and 84 titles are truncated mid-word at 76
   characters by the Amazon export ("Tools Of Titans: A Comprehensive Guide To
   High-Performance Tools And Tactics F"). Cover lookup hits Open Library by title
   and author, so these mostly miss.
3. **Non-books in the data**: "MAGCREDIBLE Magnets", "Mighty Bright-Blu-Xflex
   2-Lght", and one row titled "Not Available" with 14 events.
4. **No ISBN column.** The separate Cadence index in Google Drive has ISBNs for
   roughly half its rows, and ISBN lookup on Open Library is far more reliable than
   title-and-author search. Merging that in is the highest-leverage cover fix.

## Two indexes exist. Drive is the inbox.

This repo's CSV (490 rows, bulk export from Amazon, Audible, Kindle, Libby) is not
the same file as `Cadence/cadence-index.csv` in Google Drive (129 rows, curated,
has `isbn`, `link`, `owned`, `location`, `loans`).

**Decided:** Drive stays the capture inbox. Lauren dictates new books into Drive
from her phone, which is the only capture method that survives contact with her
actual life. This repo's CSV is downstream of it.

The sync runs on demand, at the start of a working session, as one command. It
does not exist yet. Building it is the next task:

- Pull `Cadence/cadence-index.csv` from Drive (folder id `1Yb3BgGZG9YNcoibzzYkqqEi8wVY34hNm`).
- Match against `data/cadence-index.csv` on normalized title plus first author.
  Titles from the Amazon export are truncated at 76 characters, so match on prefix,
  and prefer the Drive title when it is longer.
- Carry `isbn` and `link` across. This is the point of the whole exercise: ISBN
  lookup on Open Library beats title-and-author search, which is currently failing
  on 84 truncated titles and 227 missing authors.
- Append Drive rows that have no match here.
- Never write back to Drive. One direction only.
- Report what changed. Do not silently overwrite curated Drive values with export junk.

Then run `python3 build.py` and commit the CSV and `index.html` together.

## Working style

Lauren is a designer with 25 years of experience, technically strong but not a
career software engineer. Be blunt, back claims with specifics, argue with a plan
that has a hole in it before helping execute it. Visual quality is the work, not
decoration. No em dashes.
