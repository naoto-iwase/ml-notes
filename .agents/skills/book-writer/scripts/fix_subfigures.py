#!/usr/bin/env python3
"""Fix missing blank lines between images in Quarto subfigure panels.

Quarto requires blank lines between each image inside a subfigure panel
(::: {#fig-... layout-ncol=N} blocks). Without blank lines, only the
first image is rendered.

This script detects such blocks and inserts blank lines where needed.

Usage:
    python fix_subfigures.py <directory>

    Processes all .qmd files in the specified directory.
"""

import re
import sys
from pathlib import Path


def fix_subfigure_spacing(content: str) -> str:
    """Ensure blank lines between images in ::: subfigure blocks.

    Args:
        content: String containing markdown content

    Returns:
        str: Content with fixed subfigure spacing
    """
    lines = content.split('\n')
    result = []
    in_panel = False

    for line in lines:
        # Detect start of a subfigure panel
        if re.match(r'^:{3,}\s*\{.*layout-ncol.*\}', line.strip()):
            in_panel = True
            result.append(line)
            continue

        # Detect end of panel
        if in_panel and re.match(r'^:{3,}\s*$', line.strip()):
            in_panel = False
            result.append(line)
            continue

        if in_panel and re.match(r'^!\[', line.strip()):
            # Image line: ensure blank line before (unless prev is blank or opening :::)
            if result and result[-1].strip() != '' and not re.match(r'^:{3,}', result[-1].strip()):
                result.append('')
            result.append(line)
            continue

        if in_panel and line.strip() == '':
            result.append(line)
            continue

        # Caption text in panel: ensure blank line after preceding image
        if in_panel and line.strip() and not re.match(r'^!\[', line.strip()) and not re.match(r'^:{3,}', line.strip()):
            if result and result[-1].strip() != '' and re.match(r'^!\[', result[-1].strip()):
                result.append('')
            result.append(line)
            continue

        result.append(line)

    return '\n'.join(result)


def process_file(file_path):
    """Process a single qmd file to fix subfigure spacing.

    Args:
        file_path: Path to the qmd file

    Returns:
        bool: True if file was modified, False otherwise
    """
    print(f"Processing {file_path}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed_content = fix_subfigure_spacing(content)

    if content != fixed_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  ✓ Fixed {file_path}")
        return True
    else:
        print(f"  - No changes needed for {file_path}")
        return False


def main():
    """Main function to process qmd files."""
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        print("Usage: python fix_subfigures.py <directory>")
        print("Error: Please specify a directory to process")
        sys.exit(1)

    if not target_dir.exists():
        print(f"Directory {target_dir} not found!")
        sys.exit(1)

    qmd_files = list(target_dir.glob('*.qmd'))
    print(f"Found {len(qmd_files)} qmd files in {target_dir}\n")

    fixed_count = 0
    for qmd_file in sorted(qmd_files):
        if process_file(qmd_file):
            fixed_count += 1

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} file(s)")


if __name__ == '__main__':
    main()
