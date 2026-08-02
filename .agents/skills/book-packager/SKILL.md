---
name: book-packager
description: Package a book from the Quarto site into a self-contained distributable HTML zip. Use when the user asks to create a distributable version, share a book, export for offline viewing, or package a book for someone. Triggers on requests like "build for distribution", "create a zip", "package this book", or "make a distributable".
---

# Book Packager

Package any book, public or private, from this Quarto site into a standalone HTML zip that recipients can view locally with `python3 -m http.server`.

## Quick Start

Run the packaging script from the project root:

```bash
cd /path/to/ml-notes
uv run .agents/skills/book-packager/scripts/package_book.py <book-path> [options]
```

### Examples

```bash
# Basic (light mode by default): output to ~/Downloads/murphy1-html.zip
uv run .agents/skills/book-packager/scripts/package_book.py private/murphy1

# Use dark mode by default
uv run .agents/skills/book-packager/scripts/package_book.py private/murphy1 --dark-default

# Use a custom output path
uv run .agents/skills/book-packager/scripts/package_book.py ja/olmo-3 --output ~/Desktop/olmo3.zip
```

### Options

- `--dark-default`: Set dark mode as the default theme; recommended for technical content
- `--output PATH`: Set a custom output zip path; the default is `~/Downloads/<name>-html.zip`

## What the Script Does

1. Locates the sidebar configuration in `_quarto-private.yml` or `_quarto-public.yml`
2. Copies `.qmd` files and `images/` to a temporary directory
3. Generates a standalone `_quarto.yml` with sidebar navigation
4. Removes the `author:` field from all `.qmd` frontmatter for anonymization
5. Runs `quarto render`
6. Adds `README.txt` with local server instructions
7. Zips `_site/` and writes the archive to the book directory

## Manual Adjustments

If the user needs customizations beyond what the script provides:

- **Keep author information**: edit the temporary `.qmd` files before rendering, or modify the script
- **Use a custom theme**: edit the generated `_quarto.yml` before rendering
- **Exclude pages**: remove unwanted `.qmd` files from the temporary directory
- **Add a cover image**: ensure `images/<name>.png` exists; 1200x630 is recommended for OGP

For one-off customizations, run the script steps manually:

1. Copy the book to `/tmp/<name>-project/`
2. Create `_quarto.yml` there
3. Edit it as needed
4. Run `quarto render` in that directory
5. Zip `_site/`

## Recipient Instructions

The generated zip includes a `README.txt` explaining:

- Open the package through `python3 -m http.server`, not `file://`
- Opening through `file://` breaks the table of contents, theme switching, and search
