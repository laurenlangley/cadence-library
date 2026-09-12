#!/usr/bin/env python3
"""
Build index.html from data/cadence-index.csv.

The CSV is the database. index.html is generated output that happens to be
committed, because GitHub Pages serves static files and the app has no build
step at runtime.

    python3 build.py

Run it after any change to the CSV, in the same commit.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
CSV = ROOT / "data" / "cadence-index.csv"
TEMPLATE = ROOT / "template.html"
OUT = ROOT / "index.html"

# Columns the app reads. Extra columns in the CSV are carried through untouched
# so the schema can grow without touching this file.
REQUIRED = ["title", "author", "format", "status"]


def semantic(row):
    """Map a detailed status onto the three-state reading model.

    This is the single place that decision lives. Right now it is crude:
    anything not explicitly finished or in progress falls into 'want', which
    puts ~90% of the library in one bucket. Fix it here when the underlying
    data can support a better rule.
    """
    s = (row.get("status") or "").strip().lower()
    if s == "finished":
        return "read"
    if s == "reading":
        return "reading"
    return "want"


def load():
    with CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    missing = [c for c in REQUIRED if c not in (rows[0].keys() if rows else [])]
    if missing:
        sys.exit(f"CSV is missing required columns: {', '.join(missing)}")

    books = []
    for row in rows:
        if not (row.get("title") or "").strip():
            continue
        b = {k: (v if v is not None else "") for k, v in row.items()}
        # numeric-ish fields the app sorts on
        for k in ("pct_complete", "events", "loans"):
            if k in b and b[k] not in ("", None):
                try:
                    b[k] = float(b[k]) if k == "pct_complete" else int(b[k])
                except ValueError:
                    pass
        b["_semantic"] = semantic(row)
        books.append(b)
    return books


def main():
    books = load()
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(books, ensure_ascii=False, separators=(", ", ": "))
    start = template.index("/*__BOOKS__*/")
    end = template.index("/*__END__*/") + len("/*__END__*/")
    out = template[:start] + payload + template[end:]
    OUT.write_text(out, encoding="utf-8")

    counts = {}
    for b in books:
        counts[b["_semantic"]] = counts.get(b["_semantic"], 0) + 1
    print(f"{len(books)} books -> {OUT.name} ({len(out):,} bytes)")
    print("  " + "  ".join(f"{k}: {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
