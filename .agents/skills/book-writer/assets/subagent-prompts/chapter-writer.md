# Chapter Writer subagent prompt template

Use this template for a Phase 4 subagent that writes one chapter (`.qmd`). Fill in `{...}` for the use case. It assumes that the parent has already built `references.bib` and `/tmp/arxiv_figures/` in Phase 2.

---

```
You are a subagent using the book-writer skill. Write one Quarto chapter in Japanese using the **である** style. You are responsible for the prose, citations, and figure/table insertions as one complete unit.

## Files You Must Read First

1. `{skill_root}/assets/formatting-rules.md` — the complete formatting rules
2. `{skill_root}/references/style-consistency.md` — the checklist for consistent terminology, naming, and metaphor use. Read it to maintain consistency within this book and with existing books
3. `{skill_root}/references/reader-first-revision.md` — the chapter-introduction order and terminology-provenance check
4. `{source_file}` — the primary source for this chapter, such as survey Markdown, a paper's `.tex` source, or notes
5. `{book_dir}/references.bib` — the parent has already built this bibliography. Cite only bib keys already present in it. **Do not add entries**
6. `{book_dir}/index.qmd` and the relevant sibling chapters — use them as the source of truth for scope, notation, and terminology. Read `overview.qmd` only if the book actually has one

## Chapter Assignment

- Topic: {chapter_topic}
- Organizing axes, meaning the central questions or classifications that run through the chapter:
  - {axis_1}
  - {axis_2}
  - {axis_3}

## Output Files

- Chapter: `{book_dir}/{chapter_slug}.qmd`
- Images: `{book_dir}/images/{chapter_prefix}-<paper>-<desc>.png`, using assets the parent already fetched under `/tmp/arxiv_figures/<id>/`

## Chapter Structure

```markdown
---
pagetitle: "{Chapter Title}"
---

# {Chapter Title in English}: {Japanese Subtitle}

(Open in the order defined by `reader-first-revision.md`: state the practical question and define the central concept before introducing methods or formalization.)

## {Main Section 1}

(Prose with figures, tables, and callouts where appropriate.)

![{Caption in Japanese}. 出典: [@bibkey]](images/{chapter_prefix}-<paper>-<desc>.png){#fig-{chapter_prefix}-X width="80%"}

Refer to the figure in the prose with `@fig-{chapter_prefix}-X`.

::: {.callout-note}
## {Callout Heading in Japanese}
(Supplementary explanation.)
:::

## {Main Section 2}

| Comparison | A | B |
|------------|---|---|
| ... | ... | ... |

: {Comparison table caption in Japanese} {#tbl-{chapter_prefix}-X}

## {Other Related Papers Heading in Japanese}

(Mention them briefly in a compact table or bullet list.)

## {Chapter Summary Heading in Japanese}
```

## Inserting Images

1. The parent has already extracted the sources under `/tmp/arxiv_figures/<arxiv_id>/`. Inspect them with `ls /tmp/arxiv_figures/<id>/`
2. Select one or two of the best figures that convey the paper's main message
3. For a PDF, convert it to PNG with `pdftoppm -r 200 -png /tmp/arxiv_figures/<id>/<file>.pdf <output>`. The output gains a `-1.png` suffix, so rename it with `mv`
4. For PNG or JPG input, copy it to `{book_dir}/images/{chapter_prefix}-<shortname>-<desc>.png`
5. **Always auto-trim whitespace after placement**:
   ```bash
   uv run {skill_root}/scripts/trim_whitespace.py {book_dir}/images/{file}.png
   ```
   Converting a PDF with `pdftoppm` often leaves substantial white margins. For an algorithm figure, trimming can reduce h/w from 0.5 to 0.25. The trim is idempotent and safe as a no-op
6. **Check the aspect ratio after trimming** and choose the width accordingly:
   ```bash
   sips -g pixelWidth -g pixelHeight {book_dir}/images/{file}.png
   ```
   - Wide (h/w < 0.7) → width="85%"–"95%"
   - Approximately square (0.7–1.3) → width="70%"–"85%" (default)
   - Tall (1.3–2.0) → width="40%"–"55%"
   - Extremely tall (> 2.0) → width="30%"–"40%"
7. Insert it into the qmd as `![{Caption in Japanese}. 出典: [@bibkey]](images/...){#fig-{chapter_prefix}-X width="..."}`
8. Add prose before and after the figure, and refer to it with `@fig-{chapter_prefix}-X`

**Past example**: assigning `width="78%"` to a tall architecture figure with h/w=1.98 made its height 1.55 times the container height, producing an enormous rendering. Always check the aspect ratio. PDF-derived PNGs commonly lose 30–70% of their area when margins are trimmed, so trimming is mandatory.

## Figure Selection

- Do not target a figure count. A chapter may contain no figure when no figure adds information
- Prioritize major figures from papers directly related to the chapter, such as graphical abstracts, method overviews, and scaling curves
- Keep each figure only if it explains a relationship, result, or mechanism more clearly than prose or a table
- Do not create Mermaid solely because a paper lacks a reusable figure. Mermaid is off by default and must pass the checklist below

## Critical Formatting Rules

- Use the Japanese **である** style; do not use **です/ます**
- Make H1 **exactly match `pagetitle` and the sidebar text**. Japanese chapters do not use a bilingual H1 with a subtitle because it is repetitive. **Resist the temptation to add a descriptive subtitle to H1**. For example, `# MITS: Tree Search Using Pointwise Mutual Information` is **invalid** when `pagetitle` is `"MITS"`; H1 must be only `# MITS`. Put subtitle-like explanation in the lead paragraph. Violating this rule produces one lint error per chapter; a past book had `[TITLE_SYNC]` violations in 23 of 25 chapters
- **Do not place an italic lede, a one-line abstract in `*...*`, directly below H1**. Start a normal prose paragraph immediately after H1. Existing books such as reliable-reasoning and dllm consistently follow this style. An italic lede makes the book inconsistent; in one past case, a refinement agent added them because it considered an abstract-style lede helpful, leaving chapters mixed
- **Do not join a heading and subtitle with an em dash (`—`)**. Use `## X: Y` with an ASCII colon rather than `## X — Y`, or remove a redundant subtitle and use only `## X`
- **Do not use em dashes in prose either**. Split an interruption into sentences or write `AAA (BBB) CCC`. Use the list form `**[X]** [@key]: description`, with a colon
- Always include `pagetitle:` in the frontmatter
- **Do not wrap `[@key]` in backticks**. `` `[@key]` `` is a known bug that renders the citation literally
- In a figure caption, write the source as **`出典: [@key]`** with brackets. `出典: @key` is treated as an in-text citation rather than a parenthetical citation
- **Do not expose bib keys, arXiv IDs, or `.qmd` file names as raw prose**. For cross-chapter references, use a Markdown link such as `[Name](file.qmd)`
- **Do not refer to chapters by number**, including 「第 N 章」 and "Chapter N." Use a named link such as `[Self-Consistency and Weighted Majority Voting](self-consistency.qmd)` for another chapter and 「本章」 for the current chapter. Sidebar order may change, so numbered references become inconsistent
- **Every callout must have a `##` heading**, even a one-sentence callout, to preserve the book's heading-bearing callout convention
- Add blank lines before lists and blockquotes and inside subfigure panels
- Do not add navigation blockquotes such as `> Next chapter:` or `> Related:` at the end; the sidebar handles navigation
- Do not add a References heading; Pandoc inserts it automatically
- **Expand every abbreviation on its first use in the chapter**, using the form `強化学習（Reinforcement Learning, RL）`
- Do not place symbols such as `(SEP)`, `（Y）`, `%`, `。`, or `:` at the end of bold text; this is required for the Google Docs parser. See `formatting-rules.md` for details

## Handling Bibliography Entries

- **Do not create new entries**. Cite only entries already in `references.bib`
- If a paper you need is missing from the bibliography, report it to the parent and stop; do not add it yourself
- Do not write reader-facing prose that treats bib keys as data, such as discussing a "citation key" or "bib entry." The bibliography is an internal implementation detail
- Trust `references.bib` for titles and authors. Do not reconstruct them from a secondary survey

## Terminology Consistency Rules

Parallel subagents choose translations independently, which can create three or four variants for one concept. Follow these rules exactly:

- **Neural networks**: normalize 「ネット」, 「ネットワーク」, and 「ニューラルネットワーク」 to **「ニューラルネット」**. Expand the first use as `ニューラルネット（Neural Network, NN）`. Preserve source wording only in exceptions such as a quotation that says 「人工ニューラルネットワーク」
- **LLM scale**: use **「大規模」**, not 「巨大言語モデル」, 「巨大 LLM」, 「巨大モデル」, 「巨大データ」, or 「巨大事前学習」. Use 「莫大」 only for a metaphor about quantity, such as 「莫大な thinking budget」
- **Model-size adjectives**: use **「小規模モデル」** and **「大規模モデル」**, not the colloquial abbreviations 「小モデル」 and 「大モデル」. For comparative nuance, use 「より小さなモデル」 and 「より大きなモデル」
- **Translate casual English terms into formal Japanese**: `bucket` → 「グループ」 or 「カテゴリ」, `ballpark` → 「概算」 or 「目安」, and `flavor` → 「種類」 or 「バリアント」. Do not carry industry slang directly into Japanese technical writing
- **Avoid fancy or metaphorical wording**: do not use metaphors such as 「地図」, `landscape`, 「俯瞰」, 「見取り図」, or 「橋渡し」 in H1, `pagetitle`, or sidebar text. Prefer direct words such as 「分類」, 「整理」, 「概要」, 「全体像」, 「接続」, or 「対応」
- Follow any additional terminology rules from the parent, such as the ml-notes convention that 「推論」 means only inference

See `{skill_root}/references/style-consistency.md` for the rationale and past examples behind these rules.

## Checklist Before Drawing Mermaid

Past failures include a diagram advertised as a "two-axis map" that merely arranged three levels on one axis, diagrams that added no information beyond the adjacent table, and diagrams that only chained `subgraph A -.-> subgraph B -.-> subgraph C`. Before writing Mermaid, answer:

1. Does the figure express information that cannot be conveyed as well by a table?
2. Are the claimed two or three axes genuinely independent? Highly correlated axes reduce to one ordering
3. Does it duplicate the preceding table?
4. Does it merely connect subgraphs in sequence with `-.->`? Prose would carry more information

Also, a Unicode arrow `→` (U+2192) inside Mermaid causes a syntax error and prevents rendering. Always use ASCII arrows (`-->`, `-.->`, `==>`).

## Completion Checks

1. Run `python3 {skill_root}/scripts/fix_subfigures.py {book_dir}`
2. Run `python3 {skill_root}/scripts/fix_spacing.py {book_dir}`
3. Run `python3 {skill_root}/scripts/lint_chapters.py {book_dir}` and confirm that your chapter produces no errors
4. Confirm that every section advances the chapter's question; remove method details and repeated summaries that do not change the reader's understanding

## Completion Report

Briefly report the output path, lint result, and which figures and citations were used.
```

---

## Notes for Using This Template

- Set `{skill_root}` to the absolute path of the skill directory
- Set `{source_file}` to the relevant survey section or notes, kept short enough for the subagent to read
- Set `{book_dir}` to the absolute path of the book directory
- Set `{chapter_slug}` to the kebab-case file name without its extension
- Set `{chapter_prefix}` to the short prefix used under `images/`, such as `rlvr`, `prm`, or `sc`
- Set `{chapter_topic}` to a one-line description of the chapter topic
- List two to four organizing axes under `{axis_*}`
- Optionally add one explicit sentence listing parent-approved prohibited topics, such as internal lab information or research-direction notes
