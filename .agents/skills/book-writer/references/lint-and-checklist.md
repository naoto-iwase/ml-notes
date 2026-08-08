# Phase 7 Reference: Lint and Final Review Checklist

This document contains the complete automation commands and final-review checklist for Phase 7. The details have been separated from `SKILL.md`.

## Automation Scripts

Run these three scripts in order. Each takes the `{lang}/{book}` directory path as its argument.

### 7.1: Fix Blank Lines Before Lists and Blockquotes

```bash
python3 .agents/skills/book-writer/scripts/fix_spacing.py {lang}/{book}
```

This script:

- Detects unordered lists (`-`, `*`, and `+`) and ordered lists (`1.`, `2.`, and so on) that lack a preceding blank line.
- Detects blockquotes, which begin with `>`, that lack a preceding blank line.
- Inserts the blank lines automatically.
- Overwrites only files that require changes.

### 7.2: Fix Blank Lines Inside Subfigure Panels

```bash
python3 .agents/skills/book-writer/scripts/fix_subfigures.py {lang}/{book}
```

This script:

- Detects `![...](...)` lines inside `::: {... layout-ncol=...}` blocks.
- Automatically inserts missing blank lines between images.
- Also ensures a blank line before caption text.

In a Quarto subfigure panel, a `::: {#fig-... layout-ncol=N}` block, blank lines are required before and after every `![...](...)`. Without them, only the first image renders.

### 7.2.5: Auto-Trim Image Whitespace

```bash
uv run .agents/skills/book-writer/scripts/trim_whitespace.py {lang}/{book}
```

This script automatically trims white-background margins from PNG and JPG files under `{lang}/{book}/images/`. PNGs converted from PDF, especially with `pdftoppm -r 200 -png`, often retain large white margins. Leaving those margins causes figures to appear extremely tall during Quarto rendering or makes the actual diagram look small inside its container.

This script:

- Uses Pillow's `ImageChops.difference` to find and crop to the smallest bounding box whose difference from white exceeds the threshold.
- Retains 12 px of padding so axis labels are not cut off.
- Performs a no-op on images that have no margins, making the script idempotent and safe to rerun.
- Supports both PNG and JPG.

Past example: 24 of 31 images required trimming. The maximum area reduction was 40%, and total area fell by 7% on average. Phase 4 already instructs each chapter-writer subagent to trim images after placement, but a single Phase 7 sweep over the whole book catches omissions.

### 7.3: Validate Bibliography Integrity and Internal-Implementation Leakage

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py {lang}/{book}
```

It detects:

- `[DANGLING]` — a body citation `[@key]` undefined in `references.bib`.
- `[BACKTICK]` — citations or cross-references such as `` `[@key]` `` and `` `@tbl-name` `` wrapped in backticks and therefore rendered raw.
- `[META]` — meta-level references in prose, including the Japanese fixtures `引用キー` ("citation key") and `bib エントリ` ("bib entry").
- `[QMD_LEAK]` — a `*.qmd` filename exposed in prose outside a Markdown link or include.
- `[SLUG_LEAK]` — a file slug, for example, `survey-li2025`, exposed in `(slug)` / `（slug）` syntax.
- `[INDEX_CITE]` — a bibliography citation appears in `index.qmd`; move the evidence-bearing claim and citation to `overview.qmd`.
- `[INDEX_HEADING]` — a body heading appears in `index.qmd`.
- `[INDEX_LAYOUT]` — an index uses a list, table, callout, more than two prose paragraphs, or multiple resource-link blocks. One compact line of direct primary-resource links is allowed.
- `[DUP]` — duplicate keys in `references.bib`.
- `[NOTE_LEAK]` — internal information such as an OpenReview ID exposed in a bibliography `note` field.
- `[ANON_AUTHOR]` — `author = {Anonymous}` in a bibliography entry, suggesting an OpenReview double-blind submission was imported. Retrieve the actual authors from the latest arXiv version.
- `[CHAPTER_NUM]` — numeric chapter references such as the Japanese `第 N 章` or English `Chapter N`. Replace them with a chapter name plus a `.qmd` link.
- `[FIG_SRC]` — a figure caption using the Japanese source label without citation brackets, `出典: @key` ("Source: `@key`"). Standardize it as `出典: [@key]`.

### Patterns Pandoc Mistakes for Citations: `@<number>` and `@<English word>`

Lint does not catch this known trap, but Quarto preview reports it as a **Citeproc warning**:

- In method labels such as `NCV@3`, `Pass@8`, `Greedy@K`, `Gittins@cost`, and `Gittins@linear`, Pandoc parses `@X` as `[@X]`, a citation key.
- It then reports a warning such as `Citeproc: citation 3 not found`, because keys such as `3`, `8`, `K`, `cost`, and `linear` are undefined in the bibliography.

Ways to fix it:

- Escape it: `NCV\@3`, where the backslash makes `@` literal.
- Rename it: `Gittins@cost` → `Gittins-cost`.
- Use backticks: `` `NCV@3` ``, appropriate for a method name that should be code.

Bulk escaping script:

```bash
uv run python3 -c "
import re
from pathlib import Path
for p in Path('{book}').glob('*.qmd'):
    t = p.read_text()
    t2 = re.sub(r'(?<!\\\\)@(\d)', r'\\\\@\1', t)
    if t != t2:
        p.write_text(t2)
        print(p.name, 'escaped')
"
```

After the Phase 7 lint, **start `quarto preview` once and always check the console for `Citeproc: citation ... not found`**. If one appears, escape or rename the offending text.

Optionally, cross-check titles against a reference bibliography such as the source paper's `main.bib`. If two entries share an arXiv ID but their title similarity falls below the threshold, the script reports `[TITLE_MISMATCH]`:

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py {lang}/{book} \
    --cross-check=/tmp/arxiv_figures/<survey_arxiv_id>/main.bib
```

This mechanically catches cases such as confusing a method name with a paper title when importing many entries from a survey.

## Checklist

After running the automatic fixes, confirm the following.

### YAML / Metadata

- [ ] `_metadata.yml` exists and includes `sidebar`. Do not add `lang:` because the parent `_metadata.yml` already sets it.
- [ ] `index.qmd` exists and follows two or three existing repository entries. The default is front matter plus one or two lead paragraphs, with no `##` headings, chapter list, “Structure of This Book” section, or manual link to the first chapter. It has no bibliography citations; claims that require evidence belong in `overview.qmd`. One compact line of direct primary-resource links (paper, code, demo, dataset, or official page) is allowed.
- [ ] The index lead earns attention without hype: it starts from a concrete capability, tension, consequence, or question; defines the subject after establishing relevance; and gives the book one coherent organizing idea rather than a chapter-topic list. Source introductions informed the framing but were not copied in wording or structure.
- [ ] The `index.qmd` front matter includes `date-modified: last-modified`.
- [ ] The `index.qmd` front matter includes `toc: false`, so the landing page does not display the right-hand table-of-contents sidebar.
- [ ] The `_quarto-public.yml` or `_quarto-private.yml` sidebar registers **every chapter**.
- [ ] Sidebar `text:` follows the language rules: English for an English sidebar; localized toward Japanese for a Japanese or private sidebar, while proper nouns remain in English.
- [ ] Chapter titles and slugs were reviewed together across the complete book or Part. Bilingual editions use the same relative slug. If a slug changed, the source path, sidebar `href`, `_metadata.yml` sidebar ID, relative links, generated `_site` output, and old/new URL policy have all been checked.

### Chapter Prose

- [ ] Japanese chapters under `ja/` use the formal **de aru** style.
- [ ] Every Japanese or private chapter H1 matches its `pagetitle` and sidebar text exactly. The bilingual `# English: 日本語` form, where `日本語` means "Japanese," has been retired.
- [ ] An English chapter may use an H1 with a subtitle, but `pagetitle` ≡ sidebar text remains mandatory.
- [ ] Every chapter front matter includes `pagetitle:`, matching sidebar `text:` for the browser tab.
- [ ] Links from the main document to supplementary documents use the correct `.qmd` extension.
- [ ] Supplementary-document filenames have no numeric prefix; the sidebar controls chapter order.
- [ ] Structured data uses Quarto tables, and flow diagrams use Mermaid.
- [ ] **Every abbreviation and technical term is expanded at first use in each chapter.** In Japanese, use the literal pattern `日本語訳（English, ACRONYM）`, meaning "Japanese translation (English, ACRONYM)."
- [ ] **A chapter whose H1 contains an abbreviation expands it in the first prose paragraph.** Do not put the parenthetical expansion in H1 itself.
- [ ] Detail links use the Japanese literal syntax `[→ 詳細:]{.detail-link}` ("Details") or its corresponding target-language form, not the old `> 詳細:` blockquote.
- [ ] There is no trailing navigation blockquote such as the Japanese literals `> 次章:` ("Next chapter:"), `> 関連文書:` ("Related document:"), or `> 概要に戻る:` ("Back to overview:"); the sidebar handles navigation.
- [ ] A chapter with citations does not add a literal Japanese `## 参考文献` ("References") heading or a `::: {#refs}` block; Pandoc inserts the bibliography automatically.
- [ ] **Inter-chapter references do not use `第 N 章` ("Chapter N") or `Chapter N`.** Link a chapter name to its `.qmd` file, and use the Japanese `本章` ("this chapter") for self-reference. `lint_chapters.py` checks this with `[CHAPTER_NUM]`.
- [ ] **Every callout has a `## Header`.** A headerless callout breaks consistency within the book.
- [ ] A first-time reader encounters the chapter's question and a plain definition before a method taxonomy or paper list. Equations come after intuition unless the equation itself is the chapter's subject.
- [ ] At least one concrete example explains the chapter's organizing categories when their boundary would otherwise be abstract.
- [ ] Terms used as headings, table rows, or organizing axes are established source terms, repository conventions, or explicitly defined book-specific labels. Newly coined umbrella terms are not attributed to papers that do not use them.

### Bibliography, Citations, and Figures

- [ ] **No bibliography key or cross-reference appears raw in prose.** Do not wrap it in backticks, add a Japanese `引用キー` ("citation key") table column, or mention a `bib エントリ` ("bib entry") at the meta level. `lint_chapters.py` checks these mechanically.
- [ ] **Every new bibliography entry's title and authors match the source paper.** Confirm the method name was not mistaken for the paper title. For a survey-derived book, run `lint_chapters.py --cross-check=survey/main.bib`.
- [ ] **No `.qmd` filename or slug is exposed in prose.** Inter-chapter references must use a Markdown link such as `[Chapter Name](X.qmd)`. `lint_chapters.py` checks this with `[QMD_LEAK]` / `[SLUG_LEAK]`.
- [ ] **No OpenReview ID or similar information is exposed in a bibliography `note` field.** `lint_chapters.py` checks this with `[NOTE_LEAK]`.
- [ ] **No bibliography entry contains `author = {Anonymous}`.** This indicates an OpenReview double-blind import error; retrieve the actual authors from the latest arXiv version. `lint_chapters.py` checks this with `[ANON_AUTHOR]`.
- [ ] **Confirm whether the title changed in the latest arXiv version.** Titles can change substantially between v1 and the latest version. Treat the `<title>` on the arXiv abstract page, not an older title quoted by a survey, as authoritative.
- [ ] Blank lines appear before every unordered list, ordered list, and checklist.
- [ ] A quotation block nested in a list item also has a preceding blank line.
- [ ] Every image in a subfigure panel is separated by blank lines; `fix_subfigures.py` should already have fixed them.
- [ ] Every Quarto callout closes correctly, with matching `:::` delimiters.
- [ ] Images are placed in the `images/` directory.
- [ ] **Figure-caption sources use the Japanese literal form `出典: [@key]` ("Source: `[@key]`"), including citation brackets.** `lint_chapters.py` checks this with `[FIG_SRC]`.
- [ ] There is no figure-count quota. Every retained figure adds information that prose or a table would convey less clearly; Mermaid was not added merely to fill space.
- [ ] For a survey-heavy book, `/tmp/book-writer/{book_slug}/_figure_manifest.md` exists and `_figure_triage.md` records a keep/reject decision for every chapter. A zero-figure decision identifies what was inspected and why it was rejected. No `chapter-bib/` or other internal audit directory is tracked or present in the publish artifact.
- [ ] Every custom SVG parses as XML and has been inspected at the rendered article width for clipping, overlap, baselines, arrowheads, `viewBox`, aspect ratio, and panel alignment.
- [ ] Mathematical labels inside custom SVGs match the page's rendered math style. SVGs embedded through `<img>` do not rely on inheriting page fonts or fetching an unverified external font.

### Markdown Bold Safety (Google Docs Compatibility)

- [ ] Bold text does not end with a symbol such as `(SEP)`, the full-width-parentheses fixture `（Y）`, `5%`, the Japanese full stop `。`, or `:`.
- [ ] If it does, replace the bold markup with a `<strong>` tag or move the entire paired expression outside the bold delimiters.
- See `~/.agents/rules/markdown-bold-safety.md` for details.

### Style Consistency (Manual Sweep)

`lint_chapters.py` cannot detect these style mismatches, which occur frequently with parallel subagents. Sweep for them manually in Phase 7. See `references/style-consistency.md` for details and past examples.

Each item can be found mechanically with `grep`:

- [ ] **There is no italic lede directly below H1** — every chapter begins with an ordinary prose paragraph after H1. Check for an injected one-line abstract styled as `*...*`.
  ```bash
  for f in {lang}/{book}/*.qmd; do
    first=$(awk '/^# /{getline; getline; print; exit}' "$f")
    if [[ "$first" == "*"*"*" ]]; then echo "❌ $(basename $f) has italic lede"; fi
  done
  ```
- [ ] **No em dash (`—`, U+2014) remains in prose, headings, or tables** — fix `## X — Y` headings, `AAA——BBB` insertions, lists such as `**[X]** [@key] — explanation`, and empty table cells written as `| — |`.
  ```bash
  grep -n "—" {lang}/{book}/*.qmd
  ```
  Correction policy: heading `## X — Y` → `## X: Y` with `sed 's/^## \(.*\) — \(.*\)$/## \1: \2/'`; table `—` → `-` with `sed '/^|/s/—/-/g'`, restricted to lines beginning with `|`; edit prose manually with periods or parentheses.
- [ ] **The Japanese terms `ネット` and `ネットワーク` are standardized as `ニューラルネット` ("neural net")** — use Perl for a bulk replacement of spelling variants.
  ```bash
  grep -nP "(?<!ニューラル)(ネット(?!ワーク)|ネットワーク)" {lang}/{book}/*.qmd
  ```
  Fix: `perl -i -pe 's/(?<!ニューラル)ネットワーク/ニューラルネット/g; s/(?<!ニューラル)ネット(?!ワーク)/ニューラルネット/g'`
- [ ] **The Japanese term `巨大` ("huge") is not used in a technical model or data context** — standardize on `大規模` ("large-scale").
  ```bash
  grep -nP "巨大(言語モデル|LLM|モデル|データ|事前学習)" {lang}/{book}/*.qmd
  ```
- [ ] **Casual English terms such as bucket / ballpark / flavor have not leaked into Japanese prose** — confirm they have been localized.
  ```bash
  grep -niE "(bucket|ballpark|flavor)" {lang}/{book}/*.qmd
  ```
- [ ] **No metaphorical Japanese heading remains in H1, `pagetitle`, or sidebar text** — replace the search fixtures `地図`, `俯瞰`, `見取り図`, and `橋渡し` (map / bird's-eye view / sketch map / bridge) with direct terms such as classification, organization, or overview.
  ```bash
  grep -nE "(地図|俯瞰|見取り図|橋渡し)" {lang}/{book}/*.qmd _quarto-public.yml
  ```
- [ ] **No Unicode arrow `→` remains inside Mermaid** — replace it with `-->`, `-.->`, or `==>` because Unicode arrows cause syntax errors.
  ```bash
  for f in {lang}/{book}/*.qmd; do
    awk '/^```\{mermaid\}/,/^```$/' "$f" | grep -H "→" && echo "  ↑ in $f"
  done
  ```
- [ ] **Every Mermaid diagram has a reason to exist** — visually confirm it is not a claimed two-axis diagram that is actually linear, a set of `subgraph` blocks connected only by `-.->`, or a duplicate of the preceding table.

### Sidebar Section Names

- [ ] Each section name is a **compact functional Japanese label**, such as `中心` (core), `背景` (background), `評価` (evaluation), `訓練側` (training side), `推論側` (inference side), or `構造的アプローチ` (structural approaches). Numbered Parts use `I 基礎`, not `Part I: 基礎` or `第 I 部: 基礎`.
- [ ] It does not use an abstract phrase that merely joins chapter titles with `と` ("and"), such as `系譜と地図` ("Lineage and Map"), `比較と動向` ("Comparison and Trends"), or `位置付けと整理` ("Positioning and Organization").
- [ ] It does not use an excessively abstract or conflicting term such as `文脈` (context), `位置付け` (positioning), or `諸論点` (various issues). See `style-consistency.md`.

## Verify Link Formats

From a main document to a supplementary document; the Japanese label means "Details":

```markdown
[→ 詳細:]{.detail-link} [Sliding Window Attention](sliding-window-attention.qmd)
```

Image reference; the Japanese caption means "Figure caption":

```markdown
![図のキャプション](images/figure.png){#fig-name width="80%"}
```

## Rendering and Local Preview

During interactive prose revision, batch coherent wording changes and run cheap source checks first. Do not render after every small wording edit. Render after structural, path, or asset changes; at user-requested checkpoints; and before publication.

Use a targeted book render in the working tree. Before a public deployment, run the full-site render in a clean checkout or worktree that contains the same files as CI. An ignored private overlay may still enter the default Quarto profile even when `--profile public` is passed, so a root-wide render in a dirty mixed tree is not valid proof of the public build.

Preview locally with Quarto:

```bash
quarto preview
```

Check the preview console for warnings such as `Citeproc: citation X not found`. Such a warning indicates that `@<symbol>` was mistaken for a citation; escape or rename it.

After rendering, inspect the actual page rather than treating a successful command as sufficient. Confirm table wrapping, figure scale, clipping, chapter navigation, and new URLs after any slug rename.

## Clean Up Intermediate Files

Delete intermediate files created during Phase 2 or Phase 4 before publication.

- `{book}/bib_entries/` — temporary directory for parallel writes during Phase 4. It is unnecessary after merging into `references.bib`.
- `{book}/*.html` — stray HTML generated while validating with `quarto preview`.
- `{book}/*.log` — Quarto / Pandoc logs.
- `{book}/chapter-bib/` — legacy internal audit output. Delete it; the current workflow keeps manifests and triage notes under `/tmp/book-writer/{book_slug}/`.

```bash
find {book} -maxdepth 2 \( -name "*.html" -o -name "*.log" \) -delete
[ -d {book}/bib_entries ] && rm -rf {book}/bib_entries
[ -d {book}/chapter-bib ] && rm -rf {book}/chapter-bib
```

A remaining `bib_entries/` directory creates noise when inspecting the book's site structure. Always delete it after the merge.

After an interrupted render, inspect `git status` before cleanup. Remove only confirmed generated files. Do not use a broad recursive cleanup that could delete unrelated untracked work.
