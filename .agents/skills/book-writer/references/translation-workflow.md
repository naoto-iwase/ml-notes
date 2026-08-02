# Translation Workflow Reference: Converting an Existing Language Edition into Another Language

Use this lightweight workflow when `ja/<book>/` is nearly final and an English edition is needed, or for the reverse direction, `en/<book>/` to `ja/<book>/`. Because this is translation rather than new writing, run **parallel translation subagents** instead of Phase 2 (bibliography pre-build), Phase 3 (overview creation), or Phase 4 (prose and figure generation).

## Three Ways Translation Fundamentally Differs from New Writing

1. **The bibliography and images are language-independent** — copy and reuse `references.bib` and `images/` unchanged. There is no need to build a new bibliography in Phase 2 or fetch figures again.
2. **No content generation is needed** — translate only. Do not reread papers, reselect figures, or redesign the chapter structure.
3. **Plan for `TITLE_XLANG` cross-language synchronization from the beginning** — when both the Japanese and English sidebar text are English, meaning non-CJK, they must match exactly. This can require changes to the Japanese-side text too.

As with any new English chapter, **Chicago Title Case applies through H2 and H3**. **If it is not enforced during translation, the later heading cleanup will explode in scope**; one observed session required manual correction of more than 40 headings. To prevent this, require every translation subagent to read `formatting-rules.md`. An ad hoc translation prompt leaves the subagent unaware of this rule and typically produces sentence-case headings.

## Procedure

### 1. Prepare the Target Directory and Shared Assets

```bash
mkdir -p {target_lang}/{book}
cp -r {source_lang}/{book}/images {target_lang}/{book}/
cp {source_lang}/{book}/references.bib {target_lang}/{book}/
```

Rewrite only `_metadata.yml` for the target language:

```yaml
# en/{book}/_metadata.yml
sidebar: {book}-en
bibliography: references.bib
```

Do not copy `lang:` from the Japanese `_metadata.yml`; the parent `en/_metadata.yml` already sets the language.

### 2. Translate index.qmd and overview.qmd

These files are the book's "cover" and "big picture," so establish them before translating the chapters. Translate `{source_lang}/{book}/index.qmd` and `overview.qmd` directly.

- `index.qmd` has `title:`, so it does not need `pagetitle:`.
- Set `overview.qmd`'s `pagetitle:` to the target-language label, for example, `"Overview"` in English or the literal Japanese label `"概要"` ("Overview") in Japanese.
- Write visible inter-chapter link text in the target-language title form, matching each translated chapter's `pagetitle` / H1.

Because these files define the book's direction, quality is usually more consistent when the parent agent translates them directly rather than delegating them to subagents.

### 3. Translate Chapters in Parallel (Chapter-Translator Subagents)

Process each chapter with a translation subagent. The prompt template is [`assets/subagent-prompts/chapter-translator.md`](../assets/subagent-prompts/chapter-translator.md).

Recommended concurrency: dispatch 5–7 chapters together; for more chapters, use batches of 3–4.

Before translation, the parent should decide the **complete list of chapter `pagetitle` / sidebar text values** and pass it to every subagent. This keeps visible inter-chapter link text synchronized. A subagent does not know the new titles of other chapters on its own and will otherwise tend to leave visible text in the source language.

### 4. Update the Sidebar

Add a `{book}-{target_lang}` sidebar entry to `_quarto-public.yml` for a public book or `_quarto-private.yml` for a private book. Use the same book's sibling-language sidebar as the template, translate only `text:`, and change each `href:` path to `{target_lang}/`.

### 5. Resolve `TITLE_XLANG` Mismatches

If `lint_chapters.py` reports `[TITLE_XLANG]`, the two editions use inconsistent English labels. Ask the user which wording should be canonical, then make both sides match.

Observed example: the Japanese sidebar used sentence case (`"Depth scaling vs Token scaling"`) while the English sidebar used title case (`"Depth Scaling vs Token Scaling"`), causing a `TITLE_XLANG` error. Both were standardized to the more natural `"Depth vs Token Scaling"`, including Japanese and English sidebar text, `pagetitle`, H1, and every visible `[...](scaling.qmd)` link label in the prose.

### 6. Synchronize Visible Inter-Chapter Link Text

When a chapter title is translated or renamed, replace `[<old title>](<slug>.qmd)` in **every `.qmd` file in both languages**. Synchronization rule 6 in `formatting-rules.md`, visible inter-chapter link text ≡ the destination chapter's `pagetitle` / sidebar text, is checked manually for this reason.

```bash
# Example: rename the title of scaling.qmd
grep -rn "\[Depth scaling vs Token scaling\]" {ja,en}/<book>/
# Replace every match; with sed, use -i.bak to keep a backup
```

Observed example: changing only the English title while leaving the Japanese side untouched makes a Japanese prose link such as `[old title](scaling.qmd)` disagree with the destination title. Lint does not detect this mechanically, but it violates style consistency.

### 7. Lint and Perform the Final Review

Run lint separately for both languages:

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py {target_lang}/{book}
python3 .agents/skills/book-writer/scripts/lint_chapters.py {source_lang}/{book}  # Cross-sync fixes also changed the source
```

A large number of `[H2_CASE]` / `[H3_CASE]` findings means the translation subagent did not read `formatting-rules.md`. In future runs, always use the `chapter-translator.md` template and list `formatting-rules.md` among the files to read at the very start of the prompt.

See [`lint-and-checklist.md`](lint-and-checklist.md) for the remaining checklist.

## Pitfalls Observed in Past Work

- **Forgetting to make subagents read `formatting-rules.md`**: an ad hoc translation prompt leaves them unaware of Chicago Title Case and `TITLE_XLANG`, so they translate headings in sentence case. **Always use the `chapter-translator.md` template.**
- **A subagent runs Quarto preview/render**: a translation subagent may invoke `quarto preview` as a "verification" step and leave intermediate directories such as `<chapter>_files/`. The template explicitly prohibits `quarto render/preview`.
- **A subagent tries to "translate" bibliography entries**: the bibliography is language-independent and must never be edited; share `references.bib` unchanged.
- **Regenerating image files**: likewise, copy `images/` unchanged.
- **Replacing visible inter-chapter link text on only one side**: after renaming a title, use `grep` across both Japanese and English and replace every visible label.
- **Using the wrong acronym expansion form**: Japanese uses the literal pattern `日本語訳（English Full Form, ACRONYM）` ("Japanese translation (English Full Form, ACRONYM)"), while English uses `English Full Form (ACRONYM)`. Branch on `target_lang` as specified in `chapter-translator.md`.
- **Mechanically mistranslating the Japanese phrases `本章` ("this chapter") and `本書` ("this book")**.
- **Introducing chapter-number references**: if the Japanese source says `第 N 章` ("Chapter N"), do not reproduce it as "Chapter N" in English. Replace it with a named chapter link, following the prohibition on numeric chapter references in `formatting-rules.md`.
- **Restructuring paragraphs without authorization**: translation subagents tend to merge or split paragraphs in pursuit of more natural English. Explicitly require a one-to-one translation.
