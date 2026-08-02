#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Package a book from the Quarto site into a self-contained distributable zip.

Usage:
    uv run .agents/skills/book-packager/scripts/package_book.py <book-path> [--dark-default] [--output PATH]

Examples:
    uv run .agents/skills/book-packager/scripts/package_book.py private/murphy1
    uv run .agents/skills/book-packager/scripts/package_book.py ja/olmo-3 --dark-default
    uv run .agents/skills/book-packager/scripts/package_book.py private/pdlt --output ~/Desktop/pdlt-dist.zip

Mirrors the site's visual style (darkly/cosmo + IBM Plex + lightbox + citations-hover)
but drops site-only features (chat, lang-switch, settings popover, cite.js).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import yaml  # type: ignore[import-untyped]


def find_project_root() -> Path:
    p = Path.cwd()
    while p != p.parent:
        if (p / "_quarto.yml").exists():
            return p
        p = p.parent
    sys.exit("Error: Could not find _quarto.yml in any parent directory.")


def find_sidebar_config(root: Path, book_path: str) -> tuple[str | None, list | None]:
    candidates = [
        root / "private" / "_quarto-private.yml",
        root / "_quarto-public.yml",
    ]
    for cfg_path in candidates:
        if not cfg_path.exists():
            continue
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        sidebars = cfg.get("website", {}).get("sidebar", [])
        for sb in sidebars:
            contents = sb.get("contents", [])
            if _sidebar_matches_book(contents, book_path):
                return sb.get("title", "Book"), contents
    return None, None


def _sidebar_matches_book(contents: list, book_path: str) -> bool:
    for item in contents:
        href = item.get("href", "")
        if book_path in href:
            return True
        sub = item.get("contents", [])
        if _sidebar_matches_book(sub, book_path):
            return True
    return False


def rewrite_sidebar_contents(contents: list, book_path: str) -> list:
    result = []
    for item in contents:
        new_item = {}
        for k, v in item.items():
            if k == "href" and isinstance(v, str):
                new_item[k] = v.replace(f"{book_path}/", "")
            elif k == "contents":
                new_item[k] = rewrite_sidebar_contents(v, book_path)
            else:
                new_item[k] = v
        result.append(new_item)
    return result


def detect_lang(book_dir: Path) -> str:
    meta_path = book_dir / "_metadata.yml"
    if meta_path.exists():
        with open(meta_path) as f:
            meta = yaml.safe_load(f) or {}
        if "lang" in meta:
            return meta["lang"]
    parts = str(book_dir).split(os.sep)
    if "ja" in parts:
        return "ja"
    return "en"


def has_bibliography(book_dir: Path) -> bool:
    """Detect bib by file presence OR _metadata.yml declaration."""
    if (book_dir / "references.bib").exists():
        return True
    meta = book_dir / "_metadata.yml"
    if meta.exists():
        with open(meta) as f:
            data = yaml.safe_load(f) or {}
        return "bibliography" in data
    return False


def strip_author_from_qmd(qmd_path: Path):
    """Remove author field from YAML frontmatter, including multi-line blocks.

    Handles both:
        author: "Author Name"
    and:
        author:
          name: "Author Name"
          url: "https://..."
    """
    content = qmd_path.read_text()
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return
    fm_text = m.group(1)
    # author: + same-line value + zero-or-more indented continuation lines
    new_fm = re.sub(
        r"^author:[^\n]*(?:\n[ \t]+[^\n]*)*\n?",
        "",
        fm_text,
        flags=re.MULTILINE,
    )
    if new_fm != fm_text:
        new_content = f"---\n{new_fm}\n---{content[m.end():]}"
        qmd_path.write_text(new_content)


# Header HTML mirrors the site's _quarto.yml include-in-header block, minus
# site-only chrome (chat-panel, settings, cite.js, lang-switch). KaTeX +
# highlight.js + IBM Plex fonts are kept so math, code, and typography match.
HEADER_HTML = """\
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Sans+JP:wght@400;500;700&family=IBM+Plex+Serif:wght@600&family=IBM+Plex+Mono&family=Noto+Serif+JP:wght@600&display=swap">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js"></script>"""


def generate_quarto_yml(
    title: str,
    contents: list,
    lang: str,
    dark_default: bool,
    bibliography: bool,
) -> dict:
    """Generate a standalone _quarto.yml that mirrors the site's visual style."""
    # Theme stack matches site: darkly/cosmo + fonts.scss + dark-overrides.scss
    theme = {
        "light": ["cosmo", "css/fonts.scss"],
        "dark": ["darkly", "css/fonts.scss", "css/dark-overrides.scss"],
    }
    # Reorder when dark_default so Quarto picks dark as initial theme.
    if dark_default:
        theme = {
            "dark": ["darkly", "css/fonts.scss", "css/dark-overrides.scss"],
            "light": ["cosmo", "css/fonts.scss"],
        }

    footer_text = "Generated from ML Notes" if lang == "en" else "ML Notes より生成"

    cfg = {
        "project": {"type": "website", "output-dir": "_site"},
        "website": {
            "title": title,
            "sidebar": [
                {
                    "id": "main",
                    "title": title,
                    "style": "docked",
                    "collapse-level": 3,
                    "contents": contents,
                }
            ],
            "page-footer": {"center": footer_text},
        },
        "format": {
            "html": {
                "theme": theme,
                "css": ["css/styles.css"],
                "toc": True,
                "toc-depth": 3,
                "code-fold": False,
                "code-copy": True,
                "page-navigation": True,
                "highlight-style": "github",
                "lightbox": "auto",
                "citations-hover": True,
                "crossrefs-hover": True,
                "include-in-header": [{"text": HEADER_HTML}],
            }
        },
        "lang": lang,
    }

    # Surface bibliography so Quarto auto-renders the references section.
    # csl mirrors the site's chicago-author-date setup.
    if bibliography:
        cfg["bibliography"] = "references.bib"
        cfg["csl"] = "https://www.zotero.org/styles/chicago-author-date"
        cfg["link-citations"] = True

    return cfg


def create_readme(dest: Path, lang: str):
    if lang == "ja":
        text = """\
閲覧方法
==============================

このフォルダ内の HTML ファイルをローカルサーバー経由で開いてください。
file:// で直接開くと目次やテーマ切替などの機能が正しく動作しません。

■ 簡単な方法（Python がインストール済みの場合）

  1. ターミナルでこのフォルダに移動（zip 展開後のフォルダ）

  2. ローカルサーバーを起動
     python3 -m http.server 8080

  3. ブラウザで開く
     http://localhost:8080

■ 終了するとき

  ターミナルで Ctrl+C を押してサーバーを停止してください。

ライセンス
==============================

コンテンツ: 元の著作物のライセンスが許す最も寛容な条件で提供されます。
ソースコード: MIT License
"""
    else:
        text = """\
How to View
==============================

Open the HTML files via a local server.
Opening via file:// will break TOC, theme switching, and other features.

■ Quick method (requires Python)

  1. Navigate to this folder in terminal (the unzipped folder)

  2. Start a local server
     python3 -m http.server 8080

  3. Open in browser
     http://localhost:8080

■ To stop

  Press Ctrl+C in terminal.

License
==============================

Content: Provided under the most permissive terms the original work's license permits.
Source code: MIT License
"""
    (dest / "README.txt").write_text(text)


# CSS / SCSS files copied verbatim from the site so the package matches the
# site's typography (IBM Plex) and dark-mode code colors. Listed here as a
# single source of truth — add files as the site grows.
SITE_CSS_FILES = [
    "css/fonts.scss",
    "css/dark-overrides.scss",
    "css/styles.css",
]


def main():
    parser = argparse.ArgumentParser(description="Package a book for distribution")
    parser.add_argument("book_path", help="Relative book path (e.g. private/murphy1)")
    parser.add_argument("--dark-default", action="store_true", help="Use dark mode as default")
    parser.add_argument("--output", help="Output zip path (default: ~/Downloads/<name>-html.zip)")
    args = parser.parse_args()

    root = find_project_root()
    book_path = args.book_path.rstrip("/")
    book_dir = root / book_path
    book_name = book_path.split("/")[-1]

    if not book_dir.exists():
        sys.exit(f"Error: Book directory not found: {book_dir}")

    title, contents = find_sidebar_config(root, book_path)
    if title is None or contents is None:
        sys.exit(f"Error: No sidebar config found for '{book_path}'")

    local_contents = rewrite_sidebar_contents(contents, book_path)
    lang = detect_lang(book_dir)
    bib = has_bibliography(book_dir)

    with tempfile.TemporaryDirectory(prefix="book-pkg-") as tmpdir:
        proj = Path(tmpdir) / "project"
        proj.mkdir()

        # Copy .qmd files
        for qmd in book_dir.glob("*.qmd"):
            shutil.copy2(qmd, proj / qmd.name)

        # Copy images
        img_src = book_dir / "images"
        if img_src.exists():
            shutil.copytree(
                img_src, proj / "images",
                ignore=shutil.ignore_patterns(
                    "manifest.txt", "*.DS_Store", "test_extract",
                ),
            )

        # Copy references.bib so Quarto can resolve [@key] citations
        bib_src = book_dir / "references.bib"
        if bib_src.exists():
            shutil.copy2(bib_src, proj / "references.bib")

        # Copy site CSS/SCSS so theme typography and dark code colors match
        css_dst = proj / "css"
        css_dst.mkdir()
        for rel in SITE_CSS_FILES:
            src = root / rel
            if src.exists():
                shutil.copy2(src, css_dst / Path(rel).name)

        # Anonymize author from all qmd files (handles multi-line YAML blocks)
        for qmd in proj.glob("*.qmd"):
            strip_author_from_qmd(qmd)

        # Generate _quarto.yml
        quarto_cfg = generate_quarto_yml(
            title, local_contents, lang, args.dark_default, bib,
        )
        with open(proj / "_quarto.yml", "w") as f:
            yaml.dump(
                quarto_cfg, f,
                default_flow_style=False, allow_unicode=True, sort_keys=False,
            )

        print(f"Rendering {book_name}...")
        result = subprocess.run(
            ["quarto", "render"],
            cwd=proj,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stderr)
            sys.exit("Error: quarto render failed")

        site_dir = proj / "_site"
        if not site_dir.exists():
            sys.exit("Error: _site directory not created")

        create_readme(site_dir, lang)

        default_out = Path.home() / "Downloads" / f"{book_name}-html.zip"
        output_path = Path(args.output) if args.output else default_out
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(site_dir.rglob("*")):
                if file.is_file() and ".DS_Store" not in str(file):
                    arcname = f"{book_name}-html/{file.relative_to(site_dir)}"
                    zf.write(file, arcname)

        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"Created: {output_path} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
