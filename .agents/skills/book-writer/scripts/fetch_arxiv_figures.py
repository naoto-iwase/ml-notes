#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""
Download an arXiv e-print source and extract its image and figure files.

This produces higher-quality assets than scraping a paper PDF because it keeps
the original resolution and vector formats.

Fallback hierarchy:
  A. Get original images from the arXiv e-print with this script  ← preferred
  B. Extract from the PDF with pdffigures2 or similar tools        (not implemented; for external PDFs)
  C. Crop with a vision LLM                                       (not implemented; last resort)

Usage:
  uv run fetch_arxiv_figures.py 2406.07524
  uv run fetch_arxiv_figures.py 2502.09992 --out /tmp/arxiv_figures

Afterward:
  - Select the figures you want from the displayed list
  - Convert PDFs to PNG with `pdftoppm -r 200 -png input.pdf out`
  - Copy them into {book}/images/ with meaningful names
  - Reference them in a .qmd file as `![Caption](images/foo.png){#fig-name}`
"""

from __future__ import annotations

import argparse
import io
import tarfile
from pathlib import Path

import requests

IMAGE_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg", ".gif"}
# Exclude files such as the paper's main PDF.
SKIP_NAMES = {"main.pdf", "paper.pdf"}


def fetch_eprint(arxiv_id: str, out_dir: Path) -> Path:
    """Fetch the tarball from arxiv.org/e-print/{id} and extract it under out_dir."""
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    print(f"[fetch] {url}")
    r = requests.get(url, timeout=60, headers={"User-Agent": "book-writer/0.1"})
    r.raise_for_status()
    print(f"[fetch] {len(r.content):,} bytes")

    target = out_dir / arxiv_id
    target.mkdir(parents=True, exist_ok=True)

    # arXiv returns either tar.gz or a single gzip file.
    try:
        with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:*") as tar:
            tar.extractall(path=target, filter="data")
        print(f"[extract] tar → {target}")
    except tarfile.ReadError:
        (target / f"{arxiv_id}.tex").write_bytes(r.content)
        print(f"[extract] gzip → {target}")

    return target


def list_figures(root: Path) -> list[Path]:
    """List image files in descending size order."""
    figs = []
    for p in root.rglob("*"):
        if (
            p.is_file()
            and p.suffix.lower() in IMAGE_EXTS
            and p.name.lower() not in SKIP_NAMES
        ):
            figs.append(p)
    figs.sort(key=lambda p: p.stat().st_size, reverse=True)
    return figs


def main() -> None:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("arxiv_id", help="Example: 2406.07524")
    ap.add_argument(
        "--out", type=Path, default=Path("/tmp/arxiv_figures"),
        help="Extraction root (default: /tmp/arxiv_figures)",
    )
    args = ap.parse_args()

    target = fetch_eprint(args.arxiv_id, args.out)
    figs = list_figures(target)

    print()
    print(f"[result] Detected {len(figs)} image files")
    print("-" * 70)
    for f in figs:
        size_kb = f.stat().st_size / 1024
        rel = f.relative_to(target)
        print(f"  {size_kb:>8.1f} KB  {rel}")
    print("-" * 70)
    print(f"Extraction directory: {target}")
    print()
    print("Next steps:")
    print("  1. Select the figures you want from the list above")
    print("  2. Convert PDFs to PNG with pdftoppm: pdftoppm -r 200 -png in.pdf out")
    print("  3. Copy them into {book}/images/ with meaningful names")
    print("  4. Insert them into a .qmd file as ![Caption](images/foo.png){#fig-name}")


if __name__ == "__main__":
    main()
