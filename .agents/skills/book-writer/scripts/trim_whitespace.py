#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow"]
# ///
"""
Automatically trim white-background margins from PNG/JPG files under
`{book}/images/`.

Converting a paper PDF to PNG with `pdftoppm -r 200 -png` often leaves large
white margins around the figure, whether from page margins or whitespace around
an algorithm diagram. This script uses Pillow's ImageChops to find the smallest
bounding box whose difference from white exceeds a threshold, then crops to it.

The script has limited side effects: figures without margins remain unchanged,
making the operation a no-op for them. The default threshold is 15, and the
script keeps 12 px of padding so labels close to an image edge are unlikely to
be clipped. The original image remains under
`/tmp/arxiv_figures/<arxiv_id>/`, so an over-trimmed image can be restored by
regenerating it.

Usage:
  uv run scripts/trim_whitespace.py {book_dir}      # Trim all images
  uv run scripts/trim_whitespace.py {book_dir}/images/foo.png  # One file
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops


def trim_one(path: Path, threshold: int = 15, pad: int = 12):
    """Return (before_size, after_size) if changed, else None."""
    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    diff = diff.point(lambda v: 255 if v > threshold else 0)
    bbox = diff.getbbox()
    if not bbox:
        return None
    before = img.size
    left = max(0, bbox[0] - pad)
    top = max(0, bbox[1] - pad)
    right = min(img.size[0], bbox[2] + pad)
    bottom = min(img.size[1], bbox[3] + pad)
    cropped = img.crop((left, top, right, bottom))
    if cropped.size == before:
        return None
    cropped.save(path)
    return before, cropped.size


def main():
    if len(sys.argv) < 2:
        print("Usage: trim_whitespace.py <book_dir | image_file>", file=sys.stderr)
        sys.exit(1)
    target = Path(sys.argv[1])
    if target.is_file():
        paths = [target]
    elif (target / "images").is_dir():
        images = target / "images"
        paths = sorted(list(images.glob("*.png")) + list(images.glob("*.jpg")))
    elif target.is_dir():
        paths = sorted(list(target.glob("*.png")) + list(target.glob("*.jpg")))
    else:
        print(f"Not a file or directory: {target}", file=sys.stderr)
        sys.exit(1)

    changed = 0
    unchanged = 0
    total_before_area = 0
    total_after_area = 0
    for p in paths:
        try:
            result = trim_one(p)
        except Exception as e:
            print(f"  {p.name}: ERROR ({e})", file=sys.stderr)
            unchanged += 1
            continue
        if result:
            before, after = result
            pct = 100 - (after[0] * after[1]) * 100 // (before[0] * before[1])
            print(f"  {p.name}: {before[0]}x{before[1]} -> {after[0]}x{after[1]}  (-{pct}%)")
            changed += 1
            total_before_area += before[0] * before[1]
            total_after_area += after[0] * after[1]
        else:
            unchanged += 1

    print(f"\nChanged: {changed}, Unchanged: {unchanged}")
    if total_before_area:
        agg = 100 - total_after_area * 100 // total_before_area
        print(f"Aggregate area reduction (among changed): -{agg}%")


if __name__ == "__main__":
    main()
