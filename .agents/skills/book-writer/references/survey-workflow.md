# Survey Workflow Reference: Building a Book from Surveys

Use this variant of the standard workflow for cases such as: "I found a survey paper that covers areas absent from the existing book, and I want to incorporate them as new chapters," or "I want to combine multiple surveys into one book."

## Procedure

### 1. Retrieve the Survey and Understand the Existing Book Structure

- Fetch the survey's arXiv e-print with `fetch_arxiv_figures.py` (or the batch version) to obtain `main.bib`, `sections/*.tex`, and `figs/*.pdf` together.
- If a book already exists, read `overview.qmd` and its sidebar in `_quarto-public.yml` to understand the current coverage.

### 2. Create a Coverage Comparison Table (Important)

Map the survey taxonomy, such as its chapter organization, Fig. 1 timeline, or Fig. 3 taxonomy, to the existing chapters and present the mapping as a table.

- Rate each topic at one of three levels: **covered by an existing chapter / partially mentioned in an existing chapter / not covered**.
- The same table can be reused in the final `survey-XXX.qmd` chapter as a "mapping between this book and the survey."

### 3. Present the Comparison and Agree on a Plan with the User

Show the comparison table and agree on these two points:

1. The scope of new chapters to add.
2. Whether to include the survey itself as a chapter.

Option 3, "a survey chapter plus new chapters for uncovered areas," is the most generally useful.

### 4. Phase 2: Pre-Build the Bibliography and Figures (Important)

Phase 2, which builds the bibliography and fetches figures in one batch, is particularly valuable for this use case. See [bib-and-figures.md](bib-and-figures.md) for details.

Key points:

- Start a **bibliography pre-build subagent** and create `references.bib` in one place; do not let each chapter subagent invent its own keys.
  - Prompt template: `assets/subagent-prompts/bib-prebuild.md`
- Use **figure pre-fetch** to extract the e-prints for every paper in `references.bib` into `/tmp/arxiv_figures/` in one batch.
  - `fetch_arxiv_figures_batch.py --bib {book}/references.bib --audit-dir /tmp/book-writer/{book_slug} --parallel 8`
- Confirm `/tmp/book-writer/{book_slug}/_figure_manifest.md` was generated before chapter drafting. During drafting, record keep/reject decisions in the parent-owned `/tmp/book-writer/{book_slug}/_figure_triage.md`; selecting no figures is valid, but skipping figure inspection is not. These audit files must not enter the public book tree or Git history.
- **Always use the survey's `main.bib` as the primary source** for bibliography entries; do not rely on descriptions in the survey prose.
- Normalize key names to the book convention, `{lastname}{year}{shortname}`.
- Do not confuse a method name with a paper title. For example, "Elastic-Cache" is a method name, not the paper title.
- Check consistency mechanically with `lint_chapters.py --cross-check=/tmp/arxiv_figures/<id>/main.bib`.

### 5. Incorporate Figures from the Survey

- Convert `figs/*.pdf` to PNG with `pdftoppm -r 200 -png`, then copy each image into the book's `images/` directory under a meaningful filename.
- Decide which chapter will cite each figure before placing it; citing the same figure in multiple chapters feels repetitive.
- Add an explicit connection in the prose, such as "@fig-name shows ..."; do not merely paste in a figure without discussion.

### 6. Generate New Chapters in Parallel (Phase 4: Chapter Subagents)

Include the following in the subagent instructions. The detailed prompt template is `assets/subagent-prompts/chapter-writer.md`.

- The path to the relevant `sections/X_*.tex`, using the corresponding survey section as the primary source.
- The list of permitted bibliography keys. Have the subagent read `references.bib`, and prohibit new bibliography entries.
- Permitted image filenames and recommended placement, sourced from `/tmp/arxiv_figures/<id>/`.
- **Require the subagent to read `formatting-rules.md`**, especially the rule against exposing bibliography keys.
- Instruct it to complement rather than duplicate existing chapters and to link to those chapters.

### 7. Update Existing Chapters (Overview / Open Problems / Index)

- `overview.qmd`: add links to the new chapters in a structural way and align the overview with the survey taxonomy.
- `open-problems.qmd`, if present: upgrade areas now covered by new chapters from "open problem" to "implementation available; see the chapter."
- `index.qmd`: update the description to reflect the expanded coverage.

### 8. Reorganize the Sidebar

- If the chapter count grows, group the `_quarto-public.yml` sidebar by Part. Japanese sidebar label examples include `定式化と基盤` ("Formulation and Foundations"), `スケールと派生` ("Scaling and Extensions"), `推論と介入` ("Inference and Intervention"), `事後学習と応用` ("Post-Training and Applications"), and `俯瞰と展望` ("Overview and Outlook").
- Arrange the existing and new chapters so that the combined structure is immediately clear.

### 9. Synchronize the English Translation

- Translate not only the new chapters but also every updated existing file, including `overview.qmd`, `open-problems.qmd`, and `index.qmd`.
- Use [`translation-workflow.md`](translation-workflow.md) for the full translation workflow and [`chapter-translator.md`](../assets/subagent-prompts/chapter-translator.md) for the subagent prompt. An ad hoc translation prompt tends to violate Chicago Title Case and `TITLE_XLANG` rules, causing extensive lint failures.
- Add these survey-workflow-specific instructions:
  - If the Japanese H1 is a Japanese label, use the corresponding English title in the English version; an English subtitle is allowed. If the Japanese H1 is already an English label, retain the same English wording in the English version; whether to add or remove a subtitle is an English-side decision.
  - Translate the literal Japanese detail label `[→ 詳細:]{.detail-link}` ("Details") to `[→ Detail:]{.detail-link}`.

### 10. Validate

- Run `fix_spacing.py`, `fix_subfigures.py`, and `lint_chapters.py` for both Japanese and English.
- Use `grep` to check cross-file links, image references, `pagetitle`, and H1 formats.
- Confirm that inter-chapter link text has been translated on the English side.

## Pitfalls Observed in Past Work

- **Raw bibliography-key exposure**: subagents tend to write tables or prose such as the Japanese lint fixture `引用キー: [@key]` ("citation key: `[@key]`"). Detect this mechanically with `lint_chapters.py`.
- **Distributed invention of bibliography keys by chapter**: when chapter subagents create keys freely, the same paper often receives different keys or author names. **Centralizing the bibliography in Phase 2** solves the problem at its source.
- **Hallucinated titles**: subagents may turn a survey description containing a method name into the title. Cross-check against the survey's `main.bib`.
- **Figure decisions deferred until later**: a chapter subagent may write prose without inspecting available primary-source figures, forcing a costly retrofit. Require the Phase 2 manifest before drafting and a recorded keep/reject decision during chapter drafting. Do not impose a count, but do not accept “no figure needed” without inspection. Keep only figures that add information; see `assets/subagent-prompts/chapter-writer.md`.
- **Reusing an existing chapter's figure in a new chapter**: inserting one survey figure into several chapters creates repetition. As a rule, assign each figure exclusively to one chapter.
- **End-of-chapter navigation blockquotes**: subagents tend to add literal Japanese navigation such as `> 次章: ...` ("Next chapter: ..."). Remove it because the sidebar provides navigation.
- **Missing English synchronization**: translating only the new chapters leaves updates to existing chapters absent from English. Translate every updated file.
- **OpenReview ID leaked through `note`**: internal IDs can appear in fields such as `note = {ICLR 2026 submission, OpenReview XXXX}`. Detect them with `[NOTE_LEAK]` from `lint_chapters.py`.
