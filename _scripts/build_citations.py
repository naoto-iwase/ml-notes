#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Build assets/citations.json: {"<lang>/<note>": {formatted, bibtex}} lookup
read by js/cite.js. Source of truth is each <lang>/<note>/index.qmd frontmatter.

Bibkey: `iwase<year><topic>` for en, `iwase<year><topic><lang>` otherwise.
Topic = directory name with non-alphanumerics stripped.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://notes.iwase.dev"
CONTAINER = "ML Notes"


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    return yaml.safe_load(m.group(1)) if m else {}


def last_modified(rel_path: str, fallback: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel_path],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or fallback
    except (subprocess.CalledProcessError, FileNotFoundError):
        return fallback


def build_entry(lang: str, dirname: str, fm: dict) -> dict:
    full_name = fm["author"]["name"]
    family = full_name.split()[-1]
    date_str = str(fm["date"])
    year = int(date_str[:4])
    modified_str = last_modified(f"{lang}/{dirname}/", date_str)
    topic = re.sub(r"[^a-z0-9]", "", dirname.lower())
    bibkey = f"{family.lower()}{year}{topic}" + ("" if lang == "en" else lang)
    url = f"{SITE_URL}/{lang}/{dirname}/"
    title = fm["title"]
    # {accessed} is substituted by js/cite.js at popover open (ISO yyyy-mm-dd).
    formatted = (
        f"{full_name}. {title}. {CONTAINER}, {year}. "
        f"Published {date_str}; "
        f"last updated {modified_str}; "
        f"accessed {{accessed}}; {url}"
    )
    return {
        "published": date_str,
        "modified": modified_str,
        "formatted": formatted,
        "bibtex": (
            f"@misc{{{bibkey},\n"
            f"  title        = {{{{{title}}}}},\n"
            f"  author       = {{{full_name}}},\n"
            f"  year         = {{{year}}},\n"
            f"  howpublished = {{Blog post}},\n"
            f"  url          = {{{url}}},\n"
            f"  urldate      = {{{{accessed}}}},\n"
            "}"
        ),
    }


def rewrite_frontmatter_dates() -> None:
    # CI-only: replace `date-modified: last-modified` in each index.qmd with the
    # directory's latest git commit date. Quarto's listing aggregates frontmatter
    # before Lua filters run, so the file's literal value must already be correct.
    # Locally we leave the directive alone (Quarto resolves it from file mtime).
    pattern = re.compile(r"^date-modified:\s*last-modified\s*$", re.MULTILINE)
    for index in (*ROOT.glob("ja/*/index.qmd"), *ROOT.glob("en/*/index.qmd")):
        date = last_modified(index.parent.relative_to(ROOT).as_posix() + "/", "")
        if not date:
            continue
        text = index.read_text(encoding="utf-8")
        new_text, n = pattern.subn(f'date-modified: "{date}"', text, count=1)
        if n and new_text != text:
            index.write_text(new_text, encoding="utf-8")


def main() -> None:
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        rewrite_frontmatter_dates()

    notes: dict[str, dict] = {}
    for lang in ("ja", "en"):
        for index in sorted((ROOT / lang).glob("*/index.qmd")):
            dirname = index.parent.name
            notes[f"{lang}/{dirname}"] = build_entry(lang, dirname, parse_frontmatter(index))

    out = ROOT / "assets" / "citations.json"
    content = json.dumps({"notes": notes}, ensure_ascii=False, indent=2) + "\n"
    # Skip write when content unchanged so Quarto preview's watcher stays quiet.
    if out.exists() and out.read_text(encoding="utf-8") == content:
        print(f"Citations up to date ({len(notes)} entries)")
        return
    out.write_text(content, encoding="utf-8")
    print(f"Wrote {len(notes)} citations → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
