#!/usr/bin/env python3
"""book-writer: lint a book directory.

Accept a book directory ({lang}/{book}) and detect bibliography inconsistencies
and leaks of internal implementation details:

[DANGLING]      A body citation [@key] is undefined in the bibliography
[BACKTICK]      `[@key]` is wrapped in backticks and renders literally
[META]          Body text contains Japanese or English meta-references to
                citation keys or bibliography entries
[QMD_LEAK]      A *.qmd file name appears outside a Markdown link or include
[DUP]           A key is duplicated in the bibliography
[NOTE_LEAK]     A bibliography note field exposes an OpenReview ID or similar
                internal detail; for example, note = {OpenReview 4smJ6zY7vy}
                is inappropriate for public output
[ANON_AUTHOR]   A bibliography entry has author = {Anonymous}, suggesting that
                a double-blind OpenReview submission was copied directly;
                retrieve the real authors from the latest arXiv version
[CHAPTER_NUM]   Body text contains a numbered chapter reference in Japanese or
                English; sidebar order can change, so fixed numbers break
[FIG_SRC]       A figure caption uses an unbracketed source marker, which is
                treated as an in-text rather than parenthetical citation
[TITLE_SYNC]    H1, pagetitle, and sidebar `text:` are out of sync
                - ja chapters require exact H1 ≡ pagetitle ≡ sidebar text,
                  except overview/index; bilingual H1 forms are deprecated
                - en chapters require only pagetitle ≡ sidebar text; H1 may use
                  the full title with a subtitle while pagetitle stays short
[TITLE_XLANG]   ja and en sidebar text differ when both use English wording;
                skip the check when the ja sidebar is localized into Japanese
[H2_CASE]       An H2 in en/ is not in Chicago Title Case (sentence case), for
                example, `## Chapter summary` or `## Adaptive compute allocation`
[H3_CASE]       An H3 in en/ is not in Chicago Title Case; headings under ja/
                and private/ are outside this convention and are skipped
[TITLE_MISMATCH] Optional: a bibliography title differs from a reference
                bibliography supplied with --cross-check=PATH

Exit code: 1 when issues are found, otherwise 0.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# ---------- helpers ----------

CJK_RE = re.compile(r'[぀-ヿ一-鿿]')


def line_no(text: str, pos: int) -> int:
    """1-indexed line number of position `pos` in `text`."""
    return text[:pos].count('\n') + 1


def preserve_newlines(match):
    """For re.sub: replace match with the same number of newlines (keeps line numbers)."""
    return '\n' * match.group(0).count('\n')


def find_qmd_files(book_dir: Path):
    return sorted(p for p in book_dir.glob('*.qmd') if not p.name.startswith('_'))


# ---------- .bib parsing ----------

BIB_ENTRY_HEAD_RE = re.compile(r'@(\w+)\{([^,]+),')
ARXIV_ID_RE = re.compile(r'(\d{4}\.\d{4,5})')


def _extract_field(raw: str, field: str) -> str:
    """Extract a bibtex field value (brace-balanced). Returns '' if not found."""
    m = re.search(rf'\b{field}\s*=\s*', raw, re.IGNORECASE)
    if not m:
        return ""
    i = m.end()
    if i >= len(raw):
        return ""
    delim = raw[i]
    if delim == '{':
        depth, i = 1, i + 1
        start = i
        while i < len(raw) and depth > 0:
            if raw[i] == '{':
                depth += 1
            elif raw[i] == '}':
                depth -= 1
            i += 1
        return raw[start:i - 1]
    if delim == '"':
        i += 1
        start = i
        while i < len(raw) and raw[i] != '"':
            i += 1
        return raw[start:i]
    start = i
    while i < len(raw) and raw[i] not in ',\n':
        i += 1
    return raw[start:i]


def parse_bib(bib_text: str):
    """Single-walk bib parser. Returns list of dicts:
        {'key': str, 'line': int, 'raw': str, 'title': str, 'arxiv': str|None}
    """
    entries = []
    i = 0
    while i < len(bib_text):
        if bib_text[i] != '@':
            i += 1
            continue
        m = BIB_ENTRY_HEAD_RE.match(bib_text, i)
        if not m:
            i += 1
            continue
        # Find matching closing brace
        j = m.end()
        depth = 1
        while j < len(bib_text) and depth > 0:
            if bib_text[j] == '{':
                depth += 1
            elif bib_text[j] == '}':
                depth -= 1
            j += 1
        raw = bib_text[i:j]
        title = re.sub(r'\s+', ' ', re.sub(r'[{}]', '', _extract_field(raw, 'title'))).strip()
        arxiv_m = ARXIV_ID_RE.search(raw)
        entries.append({
            'key': m.group(2).strip(),
            'line': line_no(bib_text, i),
            'raw': raw,
            'title': title,
            'arxiv': arxiv_m.group(1) if arxiv_m else None,
        })
        i = j
    return entries


# ---------- qmd parsing ----------

H1_ATTR_TAIL_RE = re.compile(r'\s*\{[^}]*\}\s*$')
PAGETITLE_RE = re.compile(r'^pagetitle:\s*["\']?(.+?)["\']?\s*$')
FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)


def extract_h1(text: str):
    for line in text.split('\n'):
        if line.startswith('# '):
            return H1_ATTR_TAIL_RE.sub('', line[2:].strip()).strip()
    return None


def extract_pagetitle(text: str):
    fm = FRONTMATTER_RE.match(text)
    if not fm:
        return None
    for line in fm.group(1).split('\n'):
        m = PAGETITLE_RE.match(line.strip())
        if m:
            return m.group(1).strip()
    return None


# ---------- sidebar parsing ----------

SIDEBAR_TEXT_RE = re.compile(r'^\s*-?\s*(?:text|section):\s*["\']?(.+?)["\']?\s*$')
SIDEBAR_HREF_RE = re.compile(r'^\s*href:\s*(\S+\.qmd)\s*$')


def parse_sidebar_text_map(yaml_text: str, sidebar_id: str):
    """Parse a Quarto sidebar block by id and return {href: text}.

    Pairs the most recent `text:` / `section:` value with the next `href: X.qmd`.
    """
    start = re.search(rf'^\s*-\s+id:\s*{re.escape(sidebar_id)}\s*$',
                      yaml_text, re.MULTILINE)
    if not start:
        return {}
    block_start = start.end()
    next_id = re.search(r'^\s*-\s+id:\s', yaml_text[block_start:], re.MULTILINE)
    block_end = block_start + next_id.start() if next_id else len(yaml_text)
    block = yaml_text[block_start:block_end]

    pairs = {}
    pending = None
    for line in block.split('\n'):
        if not line.strip():
            continue
        m = SIDEBAR_TEXT_RE.match(line)
        if m:
            pending = m.group(1).strip().strip('"\'')
            continue
        m = SIDEBAR_HREF_RE.match(line)
        if m and pending is not None:
            pairs[m.group(1).strip()] = pending
            pending = None
    return pairs


def detect_sidebar_yaml(book_dir: Path):
    repo_root = book_dir.parent.parent
    lang = book_dir.parent.name
    cand = (repo_root / 'private' / '_quarto-private.yml') if lang == 'private' \
        else (repo_root / '_quarto-public.yml')
    return cand if cand.exists() else None


# ---------- Chicago Title Case (for [H2_CASE] / [H3_CASE]) ----------

LOWERCASE_WORDS = {
    # Articles
    'a', 'an', 'the',
    # Coordinating conjunctions (FANBOYS)
    'and', 'but', 'or', 'nor', 'for', 'so', 'yet',
    # Prepositions (Chicago: lowercase regardless of length)
    'as', 'at', 'by', 'from', 'in', 'into', 'of', 'off', 'on', 'onto',
    'out', 'over', 'per', 'to', 'upon', 'via', 'vs', 'with',
    # Note: 'is', 'are', 'be' are VERBS and should be capitalized in Chicago style.
}

# Markdown / quote / paren / bracket chars that wrap a word but aren't part of it
STRIP_CHARS = '*_`"\'()[]{}<>“”‘’「」『』'


def _word_is_title_case(word: str, must_cap: bool) -> bool:
    """Check a single token for Chicago Title Case.

    Handles: markdown stripping, hyphenated compounds (recursive: first part always
    capitalized; later parts may be lowercase if short word), digit-bearing tokens
    (treated as proper names / version numbers — skipped), camelCase brand names
    (e.g. fastText, iPhone — skipped).
    """
    word = word.strip(STRIP_CHARS)
    if not word or not any(c.isalpha() for c in word):
        return True

    if '-' in word:
        # First sub-part: must cap; later sub-parts: cap unless short word.
        return all(_word_is_title_case(p, must_cap=(i == 0))
                   for i, p in enumerate(word.split('-')) if p)

    if any(c.isdigit() for c in word):
        return True  # proper name / version (e.g. GPT-4o sub-part "4o", "256x256")

    # word has at least one alpha (checked above), so the default '' is never used;
    # specifying it keeps the static type as str rather than Optional[str].
    first_alpha = next((c for c in word if c.isalpha()), '')
    if first_alpha.isupper():
        return True
    if any(c.isupper() for c in word[1:]):
        return True  # camelCase brand (lowercase first, then upper later)

    return not must_cap and word.lower() in LOWERCASE_WORDS


def is_chicago_title_case(heading: str) -> bool:
    """Return True if heading follows Chicago Title Case.

    - First word capitalized; first word after `:` or `—` also capitalized
    - Subsequent words capitalized unless in LOWERCASE_WORDS
    - Non-alpha tokens (numbers, symbols) don't affect "first-ness"
    """
    heading = H1_ATTR_TAIL_RE.sub('', heading).strip()
    if not heading:
        return True

    saw_first = False
    next_must_cap = True
    for tok in heading.split():
        stripped = tok.strip(STRIP_CHARS)
        if not any(c.isalpha() for c in stripped):
            if stripped.endswith((':', '—')):
                next_must_cap = True
            continue
        must_cap = next_must_cap or not saw_first
        if not _word_is_title_case(tok, must_cap):
            return False
        saw_first = True
        next_must_cap = stripped.endswith((':', '—'))
    return True


def check_heading_case(book_dir: Path, rel) -> int:
    """[H2_CASE] / [H3_CASE]: en/ chapters' H2 and H3 must be Chicago Title Case."""
    if book_dir.parent.name != 'en':
        return 0  # ja/private headings exempt
    issues = 0
    for qmd in find_qmd_files(book_dir):
        for ln, line in enumerate(qmd.read_text().split('\n'), 1):
            if line.startswith('### '):
                level, heading = 3, line[4:].strip()
            elif line.startswith('## ') and not line.startswith('### '):
                level, heading = 2, line[3:].strip()
            else:
                continue
            if heading and not is_chicago_title_case(heading):
                print(f"[H{level}_CASE] {rel(qmd)}:{ln}: '{heading}' is not in Chicago Title Case")
                issues += 1
    return issues


# ---------- TITLE_SYNC / TITLE_XLANG ----------

def check_titles(book_dir: Path, sidebar_yaml: Optional[Path], rel) -> int:
    book_slug = book_dir.name
    lang = book_dir.parent.name
    if lang not in ('ja', 'en', 'private'):
        return 0

    # Read sidebar yaml once; build maps for both this lang and the sibling lang.
    sidebar_map, sibling_sidebar_map = {}, {}
    sibling_lang = {'ja': 'en', 'en': 'ja'}.get(lang)
    if sidebar_yaml and sidebar_yaml.exists():
        yaml_text = sidebar_yaml.read_text()
        sidebar_id = f"{book_slug}-{lang}" if lang in ('ja', 'en') else book_slug
        sidebar_map = parse_sidebar_text_map(yaml_text, sidebar_id)
        # private books often lack the -ja/-en suffix; fall back to plain id
        if not sidebar_map and lang == 'private':
            sidebar_map = parse_sidebar_text_map(yaml_text, book_slug)
        if sibling_lang:
            sibling_sidebar_map = parse_sidebar_text_map(yaml_text, f"{book_slug}-{sibling_lang}")

    issues = 0
    for qmd in find_qmd_files(book_dir):
        text = qmd.read_text()
        h1 = extract_h1(text)
        pagetitle = extract_pagetitle(text)
        is_overview_or_index = qmd.name in ('overview.qmd', 'index.qmd')

        # ja H1 ≡ pagetitle (ja H1 follows sidebar/pagetitle exactly: the same short
        # label, with no bilingual `English: Japanese` form). Skip overview/index.
        if lang in ('ja', 'private') and not is_overview_or_index and h1 and pagetitle:
            if h1 != pagetitle:
                print(f"[TITLE_SYNC] {rel(qmd)}: H1 '{h1}' != pagetitle '{pagetitle}' (ja H1 must exactly match sidebar text)")
                issues += 1

        # en H1 can carry a subtitle (no H1≡pagetitle requirement for en).

        # pagetitle ↔ sidebar text (applies to overview/index too).
        if sidebar_map and pagetitle:
            sb_text = sidebar_map.get(f"{lang}/{book_slug}/{qmd.name}")
            if sb_text and sb_text != pagetitle:
                print(f"[TITLE_SYNC] {rel(qmd)}: sidebar text '{sb_text}' != pagetitle '{pagetitle}'")
                issues += 1

        # Cross-lang sidebar-text consistency. Skip overview/index, and skip when
        # either side is localized to its own language (contains CJK).
        if sidebar_map and sibling_sidebar_map and not is_overview_or_index:
            my_sb = sidebar_map.get(f"{lang}/{book_slug}/{qmd.name}")
            sib_sb = sibling_sidebar_map.get(f"{sibling_lang}/{book_slug}/{qmd.name}")
            if (my_sb and sib_sb
                    and not CJK_RE.search(my_sb)
                    and not CJK_RE.search(sib_sb)
                    and my_sb != sib_sb):
                print(f"[TITLE_XLANG] {rel(qmd)}: sidebar text '{my_sb}' != {sibling_lang} sidebar text '{sib_sb}'")
                issues += 1

    return issues


# ---------- per-qmd content patterns ----------

# Citation pattern (allow hyphens so cross-refs like @fig-name are captured as a
# single key, then filtered via XREF_PREFIXES).
CITE_RE = re.compile(r'\[@([a-zA-Z][\w-]*)(?:[,;\s][^]]*)?\]|(?<!`)@([a-zA-Z][\w-]+)(?!`)')
BACKTICK_BIBKEY_RE = re.compile(r'`\[@[a-zA-Z][\w-]*\]`|`@[a-zA-Z][\w-]+`')
XREF_PREFIXES = ('fig-', 'tbl-', 'sec-', 'eq-', 'thm-', 'lem-', 'cor-', 'prp-',
                 'def-', 'exm-', 'exr-')

META_PATTERNS = [
    (re.compile(r'引用キー'), "Japanese citation-key meta-reference"),
    (re.compile(r'Citation key', re.IGNORECASE), "meta-reference: 'Citation key'"),
    (re.compile(r'bib エントリ'), "Japanese bib-entry meta-reference"),
    (re.compile(r'bib entry', re.IGNORECASE), "meta-reference: 'bib entry'"),
    (re.compile(r'bibtex エントリ'), "Japanese BibTeX-entry meta-reference"),
]

CHAPTER_NUM_RE = re.compile(r'第\s*\d+\s*章|\bChapter\s+\d+\b', re.IGNORECASE)
FIG_IMAGE_RE = re.compile(r'!\[([^\n]*?)\]\([^)\n]+\)')
FIG_SRC_BARE_RE = re.compile(r'(出典|Source):\s*@[a-zA-Z][\w-]*')

CODE_BLOCK_RE = re.compile(r'```[^\n]*\n.*?```', re.DOTALL)
FM_BLOCK_RE = re.compile(r'^---\n.*?\n---\n', re.DOTALL)
INLINE_CODE_RE = re.compile(r'`[^`\n]+`')

# Legitimate .qmd occurrences (stripped before leak check)
MD_LINK_QMD_RE = re.compile(r'\[[^\]]*\]\([^)]*\.qmd[^)]*\)')
INCLUDE_QMD_RE = re.compile(r'\{\{<\s*include\s+[^}]+\.qmd[^}]*>\}\}')
QMD_LEAK_RE = re.compile(r'`?[\w./_-]*\.qmd`?')
# File slug leak: flag only when wrapped (bare kebab-case often appears as
# compound modifier in English, e.g. "inference-acceleration context").
SLUG_LEAK_RE = re.compile(r'[(（\[「『]\s*([a-z][a-z0-9]*(?:-[a-z0-9]+){1,})\s*[)）\]」』]')

# bib note field with OpenReview ID leak (in the pre-publication phase, this is internal)
NOTE_LEAK_RE = re.compile(
    r'note\s*=\s*\{([^}]*\bOpenReview\s+[0-9A-Za-z]{5,}\b[^}]*)\}',
    re.IGNORECASE,
)
ANON_AUTHOR_RE = re.compile(r'author\s*=\s*\{\s*Anonymous\s*\}', re.IGNORECASE)


def _check_qmd(qmd: Path, rel, has_bib: bool, book_slugs: set):
    """Run per-file content checks. Returns (issues, used_keys_set)."""
    text = qmd.read_text()
    # Strip fenced code blocks and frontmatter (preserve newlines for line numbers).
    clean = CODE_BLOCK_RE.sub(preserve_newlines, text)
    clean = FM_BLOCK_RE.sub(preserve_newlines, clean)
    leak_check_text = INCLUDE_QMD_RE.sub(preserve_newlines,
                                          MD_LINK_QMD_RE.sub(preserve_newlines, clean))

    issues = 0
    rp = rel(qmd)

    # [BACKTICK] backtick-wrapped citation/xref key (raw display bug)
    for m in BACKTICK_BIBKEY_RE.finditer(clean):
        matched = m.group(0)
        inner = matched.strip('`').lstrip('[').rstrip(']').lstrip('@')
        kind = "cross-reference" if inner.startswith(XREF_PREFIXES) else "bib key"
        print(f"[BACKTICK] {rp}:{line_no(clean, m.start())}: backtick-wrapped {kind} {matched} renders literally")
        issues += 1

    # [META] meta-mentions
    for pat, label in META_PATTERNS:
        for m in pat.finditer(clean):
            print(f"[META] {rp}:{line_no(clean, m.start())}: {label}")
            issues += 1

    # [QMD_LEAK] .qmd file name leaks (outside markdown links / includes)
    for m in QMD_LEAK_RE.finditer(leak_check_text):
        leaked = m.group(0).strip('`')
        if leaked == '.qmd':
            continue
        print(f"[QMD_LEAK] {rp}:{line_no(leak_check_text, m.start())}: file name '{leaked}' is exposed in body text; use a Markdown link")
        issues += 1

    # [SLUG_LEAK] wrapped file slug
    for m in SLUG_LEAK_RE.finditer(leak_check_text):
        slug = m.group(1)
        if slug not in book_slugs:
            continue
        print(f"[SLUG_LEAK] {rp}:{line_no(leak_check_text, m.start())}: file slug '{slug}' is exposed in body text; use the chapter title or a link")
        issues += 1

    # [CHAPTER_NUM] chapter number references
    for m in CHAPTER_NUM_RE.finditer(clean):
        print(f"[CHAPTER_NUM] {rp}:{line_no(clean, m.start())}: numbered chapter reference '{m.group(0)}'; use a named .qmd link or an unnumbered self-reference")
        issues += 1

    # [FIG_SRC] figure caption with bare-cite source
    for m in FIG_IMAGE_RE.finditer(clean):
        if FIG_SRC_BARE_RE.search(m.group(1)):
            print(f"[FIG_SRC] {rp}:{line_no(clean, m.start())}: figure caption source lacks brackets; use a bracketed citation")
            issues += 1

    # Collect citation keys (only meaningful when bib exists)
    used_keys = set()
    if has_bib:
        no_inline_code = INLINE_CODE_RE.sub('', clean)
        for m in CITE_RE.finditer(no_inline_code):
            key = m.group(1) or m.group(2)
            if key and not key.startswith(XREF_PREFIXES):
                used_keys.add(key)

    return issues, used_keys


# ---------- main orchestration ----------

def check_book(book_dir: Path,
               cross_check_bib: Optional[Path] = None,
               sidebar_yaml: Optional[Path] = None):
    repo_root = book_dir.parent.parent
    rel = lambda p: p.relative_to(repo_root)

    bib_path = book_dir / 'references.bib'
    has_bib = bib_path.exists()
    bib_text = bib_path.read_text() if has_bib else ""
    bib_entries = parse_bib(bib_text) if has_bib else []
    bib_keys = {e['key'] for e in bib_entries}

    issues = 0

    # --- bib-only checks ---
    if has_bib:
        # [DUP] duplicate keys
        seen = {}
        for e in bib_entries:
            if e['key'] in seen:
                print(f"[DUP] {bib_path.name}: key '{e['key']}' duplicated at line {e['line']} (first at line {seen[e['key']]})")
                issues += 1
            else:
                seen[e['key']] = e['line']

        # [NOTE_LEAK] OpenReview IDs in note field
        # [ANON_AUTHOR] Anonymous authors (likely OpenReview double-blind leftover)
        for e in bib_entries:
            note_m = NOTE_LEAK_RE.search(e['raw'])
            if note_m:
                ln = e['line'] + e['raw'][:note_m.start()].count('\n')
                print(f"[NOTE_LEAK] {bib_path.name}:{ln}: note field exposes OpenReview ID '{note_m.group(1).strip()}'")
                issues += 1
            anon_m = ANON_AUTHOR_RE.search(e['raw'])
            if anon_m:
                ln = e['line'] + e['raw'][:anon_m.start()].count('\n')
                print(f"[ANON_AUTHOR] {bib_path.name}:{ln}: author = {{Anonymous}} (key='{e['key']}'); retrieve real authors from the latest arXiv version")
                issues += 1

    # --- per-qmd content checks ---
    qmd_files = find_qmd_files(book_dir)
    book_slugs = {p.stem for p in qmd_files if p.stem != 'index'}
    used_keys = set()
    for qmd in qmd_files:
        n, keys = _check_qmd(qmd, rel, has_bib, book_slugs)
        issues += n
        used_keys |= keys

    # [DANGLING] citations whose key isn't in bib
    if has_bib:
        for key in sorted(used_keys - bib_keys):
            print(f"[DANGLING] {bib_path.name}: body citation [@{key}] is undefined in the bibliography")
            issues += 1

    # [TITLE_MISMATCH] cross-check titles against a reference bib (optional)
    if has_bib and cross_check_bib and cross_check_bib.exists():
        ref_by_arxiv = {}
        for e in parse_bib(cross_check_bib.read_text()):
            if e['arxiv']:
                ref_by_arxiv.setdefault(e['arxiv'], []).append((e['key'], e['title']))

        def title_sim(a, b):
            aw = set(re.findall(r'\w+', a.lower()))
            bw = set(re.findall(r'\w+', b.lower()))
            return len(aw & bw) / max(len(aw), len(bw)) if aw and bw else 0

        for e in bib_entries:
            arxiv = e['arxiv']
            if not arxiv or arxiv not in ref_by_arxiv:
                continue
            best_sim = max((title_sim(e['title'], t) for _, t in ref_by_arxiv[arxiv]), default=0)
            if best_sim < 0.5 and e['title']:
                ref_titles = "; ".join(f"[{k}] {t}" for k, t in ref_by_arxiv[arxiv])
                print(f"[TITLE_MISMATCH] {bib_path.name}: '{e['key']}' (arxiv:{arxiv}) title='{e['title'][:60]}...' vs reference={ref_titles[:120]}")
                issues += 1

    # [TITLE_SYNC] / [TITLE_XLANG] / [H2_CASE] / [H3_CASE]
    issues += check_titles(book_dir, sidebar_yaml or detect_sidebar_yaml(book_dir), rel)
    issues += check_heading_case(book_dir, rel)

    if issues == 0:
        bib_note = f"{len(bib_keys)} bib keys, {len(used_keys)} citations used" if has_bib else "no bib"
        print(f"[OK] {book_dir}: no issues ({len(qmd_files)} qmd files, {bib_note})")

    return issues


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('book_dir', help='Book directory (e.g. ja/dllm)')
    p.add_argument('--cross-check', metavar='BIB',
                   help='Reference bib to cross-check titles against (e.g. survey main.bib)')
    p.add_argument('--sidebar', metavar='YAML',
                   help='Quarto sidebar yaml (default: auto-detect _quarto-public.yml / private/_quarto-private.yml)')
    args = p.parse_args()

    book_dir = Path(args.book_dir).resolve()
    if not book_dir.is_dir():
        print(f"Error: {book_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    cross = Path(args.cross_check).resolve() if args.cross_check else None
    sidebar = Path(args.sidebar).resolve() if args.sidebar else None
    sys.exit(1 if check_book(book_dir, cross, sidebar) else 0)


if __name__ == '__main__':
    main()
