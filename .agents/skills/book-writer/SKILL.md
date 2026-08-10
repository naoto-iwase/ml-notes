---
name: book-writer
description: |
  Technical-document authoring workflow for the books repository.
  Converts papers, technical documents, surveys, and similar sources into structured `.qmd` documents.
  Uses subagents to generate supplementary documents in parallel, adds figures (obtained from arXiv e-prints)
  and supplementary information through Quarto callouts. For books with many citations, running Phase 2 to
  build `references.bib` in one place beforehand prevents scattered bibliography files and hallucinations.
  Use when: (1) creating paper summaries, (2) documenting technical material,
  (3) creating a book from a survey, or (4) handling requests such as “summarize X.”
---

# Book Writer

A technical-document authoring workflow for the books repository. It efficiently converts papers, technical documents, surveys, and similar sources into structured `.qmd` documents.

## Privacy-Safe Examples

- Do not use the repository owner, their acquaintances, collaborators, affiliations, or other identifiable real people as illustrative or negative examples.
- Prefer role-based descriptions, explicit placeholders, or synthetic names in reusable examples and fixtures. When documenting a failure mode, describe the error class without naming the affected person.
- Use real names only when they are necessary to cite or accurately discuss a source.

## Workflow Overview

```
Phase 1: Prepare to write (confirm language and book; create directories)
    ↓
Phase 2: Prebuild bibliography + figures (survey-heavy books only)
    ↓
Phase 3: Create the main document (overview.qmd)
    ↓
Phase 4: Generate chapters in parallel — each assignment covers prose + citations + figures as one unit
    ↓
Phase 5: Add supplementary callouts
    ↓
Phase 6: Configure index.qmd and _quarto.yml
    ↓
Phase 7: Lint and perform final checks
```

For details about each phase, read the corresponding section in this file and, as needed, the dedicated documents under `references/`.

## Reference Dispatch

### Documentation Specific to This Skill

| Goal | Reference file |
|------|----------------|
| Create a book from a survey (add chapters to an existing book / create a new survey book) | [references/survey-workflow.md](references/survey-workflow.md) |
| Convert an existing language edition into another language (ja → en or en → ja) | [references/translation-workflow.md](references/translation-workflow.md) |
| Prebuild the bibliography + figures in one place (Phase 2) | [references/bib-and-figures.md](references/bib-and-figures.md) |
| Configure index.qmd / the sidebar in detail (Phase 6) | [references/index-and-sidebar.md](references/index-and-sidebar.md) |
| Run linting and the final checklist (Phase 7) | [references/lint-and-checklist.md](references/lint-and-checklist.md) |
| Check consistency during later augmentation (extended Phase 7) | [references/augmentation-consistency.md](references/augmentation-consistency.md) |
| Maintain style consistency (terminology, naming, and metaphor checks) | [references/style-consistency.md](references/style-consistency.md) |
| Rewrite a technically correct but difficult chapter for first-time readers | [references/reader-first-revision.md](references/reader-first-revision.md) |

### Subagent Prompt Templates

| Purpose | Template |
|---------|----------|
| Chapter-writing subagent | [assets/subagent-prompts/chapter-writer.md](assets/subagent-prompts/chapter-writer.md) |
| Chapter-translation subagent (ja → en or en → ja) | [assets/subagent-prompts/chapter-translator.md](assets/subagent-prompts/chapter-translator.md) |
| Subagent that builds the bibliography in one place | [assets/subagent-prompts/bib-prebuild.md](assets/subagent-prompts/bib-prebuild.md) |
| Subagent that fetches figure e-prints in one batch | [assets/subagent-prompts/figure-prefetch.md](assets/subagent-prompts/figure-prefetch.md) |

### Quarto Feature References

| Goal | Reference file |
|------|----------------|
| Read the complete formatting rules (every subagent must read this) | [assets/formatting-rules.md](assets/formatting-rules.md) |
| Add callouts (supplementary boxes) | [references/quarto/callouts.md](references/quarto/callouts.md) |
| Add cross-references to figures, tables, sections, and equations | [references/quarto/cross-references.md](references/quarto/cross-references.md) |
| Insert, position, and group figures into subfigures | [references/quarto/figures.md](references/quarto/figures.md) |
| Create tables (pipe / list / computed tables) | [references/quarto/tables.md](references/quarto/tables.md) |
| Draw diagrams with Mermaid / Graphviz | [references/quarto/diagrams.md](references/quarto/diagrams.md) |
| Manage citations and reference lists (`.bib`, `[@key]`) | [references/quarto/citations.md](references/quarto/citations.md) |
| Use shortcodes (`{{< include >}}`, `{{< video >}}`, etc.) | [references/quarto/shortcodes.md](references/quarto/shortcodes.md) |
| Use Div / Span syntax (`:::` for theorem environments, `[text]{.class}`, etc.) | [references/quarto/divs-and-spans.md](references/quarto/divs-and-spans.md) |
| Configure page/content width, multiple columns, and margin placement | [references/quarto/layout.md](references/quarto/layout.md) |
| Branch display by output format such as HTML/PDF | [references/quarto/conditional-content.md](references/quarto/conditional-content.md) |
| Configure YAML front matter | [references/quarto/yaml-front-matter.md](references/quarto/yaml-front-matter.md) |
| Apply Markdown lint rules | [references/quarto/markdown-linting.md](references/quarto/markdown-linting.md) |

### Quarto Features Specific to This Site

The following are already enabled in `_quarto.yml` and do not need to be configured again in individual `.qmd` files:

- `lightbox: auto` — every image can be enlarged by clicking it
- `citations-hover: true` — hovering over `[@key]` shows a bibliographic-information pop-up
- `crossrefs-hover: true` — references such as `@fig-name` likewise show a hover preview
- **Language-specific labels**: simply specify `lang:` in `ja/_metadata.yml`, `private/_metadata.yml`, or `en/_metadata.yml`; Quarto automatically translates labels such as theorem, lemma, corollary, proposition, definition, example, figure, and table
- **Citation style**: `csl: https://www.zotero.org/styles/chicago-author-date` (author-year) and `link-citations: true` are configured globally in `_quarto.yml`. A book-specific `_metadata.yml` only needs `bibliography: references.bib`

---

## Phase 1: Prepare to Write

### Procedure

1. **Confirm the writing language**: Japanese (`ja/`) or English (`en/`). Ask the user, “Will this be written in Japanese or English?”
2. **Confirm public/private status**: place source material with licensing concerns under `private/{book}/`
   - `ja/`, `en/` → public (add the sidebar to `_quarto-public.yml`)
   - `private/` → private (add the sidebar to `private/_quarto-private.yml`)
3. **Confirm the book name**: the kebab-case directory name. Examples: `olmo-3`, `deepseek-r1`, `qwen-3`
4. **Confirm the source document**: paper URL, PDF path, text file, etc.
5. **Create directories**: create `{base}/{book}/` and `{base}/{book}/images/`
6. **Create `_metadata.yml`**:

   ```yaml
   # Public Japanese edition: ja/{book}/_metadata.yml
   sidebar: book-name-ja

   # Add this for books that require citations
   bibliography: references.bib
   ```

   - Make `sidebar` match the sidebar configuration's `id` (public sidebars use the `-ja` / `-en` suffix)
   - Do not write `lang:` here; it is already configured in the parent `_metadata.yml`

Create `index.qmd` in Phase 6.

### Directory Structure

```
{base}/{book}/
├── _metadata.yml           # Specifies the sidebar ID
├── index.qmd               # Created in Phase 6
├── overview.qmd            # Main document
├── concept-a.qmd           # Supplementary document / chapter
├── concept-b.qmd
├── references.bib          # When citations exist (recommended to build in Phase 2)
└── images/
    └── figure.png
```

Public/private directory divisions and their corresponding sidebar configuration files:

| Directory | Purpose | Sidebar configuration |
|-----------|---------|-----------------------|
| `ja/{book}/` | Public, Japanese | `_quarto-public.yml` |
| `en/{book}/` | Public, English | `_quarto-public.yml` |
| `private/{book}/` | Private | `private/_quarto-private.yml` |

### File-Naming Rules

- **Use only a kebab-case topic name for each filename. Do not add prefixes such as `01-`** (the sidebar configuration controls chapter order)
- **overview.qmd**: main document
- **images/**: image-only directory
- **Extension**: `.qmd`

### Slug-Naming Guidance

Prior experience: overly short slugs such as `lineage.qmd` and `latent-map.qmd` did not reveal the chapter topic from the URL, so they later had to be renamed to `depth-recurrence.qmd` and `latent-reasoning.qmd`. Conversely, overly long slugs such as `lineage-depth-recurrence.qmd` and `arc-agi-and-small-models.qmd` are verbose. As a rule of thumb, extract a “core noun phrase that describes the function” and use **one to three kebab-case words**.

- Good: `process-reward-model.qmd`, `depth-recurrence.qmd`, `latent-reasoning.qmd`, `inference-acceleration.qmd`
- Bad (too short or lacking context): `lineage.qmd`, `map.qmd`, `latent-map.qmd`
- Bad (too long or verbose): `lineage-depth-recurrence.qmd`, `arc-agi-and-small-models.qmd`

Name the slug by extracting the “core noun phrase that represents the theme” from the H1 title so that H1 and URL correspond naturally (Japanese-title example: H1 = `Depth recurrence の系譜` → slug = `depth-recurrence`).

Review the chapter title and slug together. If the title changes enough that the old slug no longer describes it, rename both in the same change. Bilingual editions use the same relative slug under `ja/` and `en/`; translate the title, not the filename. Audit all chapter titles and slugs as a set after adding Parts so one chapter does not retain a stale naming scheme.

### Naming Book Titles: Avoid Confusion with Existing Genres

When choosing the book name (the `title:` field) and overview H1, **check whether it could be confused with a very well-known existing concept**.

Prior experience: “Recursive Reasoning Models” alone can be confused with the o1/R1 family of “reasoning models” (LLM thinking models). Adding a **scope-defining prefix**, as in `Small Recursive Reasoning Models`, distinguishes the topic and immediately tells first-time readers that it is different from an LLM.

Examples of distinguishing prefixes: `Small` / `Tiny` (scale), `Latent` / `Continuous` (continuous representations), `Symbolic` / `Neuro-Symbolic` (symbolic computation), and `Multimodal` (multimodality).

See [references/style-consistency.md](references/style-consistency.md) for details.

---

## Phase 2: Prebuild the Bibliography + Figures (Survey-Heavy Books Only)

For books with many citations (surveys, multi-paper summaries, and similar works; approximately 30+ references), **create `references.bib` and `/tmp/arxiv_figures/` in one place before entering Phase 3**. Treat this as a required phase gate unless the user explicitly waives source-figure inspection.

Why this matters:

- If each chapter subagent invents bibliography keys, they must later be merged and renamed
- If a subagent sees only a secondary survey source, it may confuse a method name with a paper title or get authors wrong
- If the latest arXiv version is not checked, author-list and title changes from v1 to the latest version can be missed
- A double-blind OpenReview submission may be imported directly with `author = {Anonymous}`; because the actual authors are usually public on the arXiv preprint, always obtain metadata from the arXiv abstract page
- Adding figures afterward can produce an extreme imbalance among chapters (prior example: one chapter had eight figures while the others had none)

For books with few citations, such as a guide to a single paper, skip this phase and add citations as needed while writing the overview and chapters.

### Procedure Summary

1. **Launch a bibliography prebuild subagent** — use the template in `assets/subagent-prompts/bib-prebuild.md`. Have it read primary sources (survey Markdown / paper list), build `references.bib` in one place, and put internal paper-to-chapter notes under `/tmp/book-writer/{book_slug}/`
2. **Fetch all figures in a batch** — run `fetch_arxiv_figures_batch.py --bib {book}/references.bib --audit-dir /tmp/book-writer/{book_slug} --parallel 8` to unpack every paper's e-print under `/tmp/arxiv_figures/<id>/` and generate `/tmp/book-writer/{book_slug}/_figure_manifest.md`
3. **Pass the phase gate** — confirm the batch completed and the manifest exists before drafting chapters. A zero-figure book is valid only after inspecting the available source figures; “no figure quota” never means “skip figure review”
4. **Validate the bibliography** — run `lint_chapters.py {book}` and confirm there are zero `[DUP]`, `[NOTE_LEAK]`, `[ANON_AUTHOR]`, and `[TITLE_MISMATCH]` findings

See [references/bib-and-figures.md](references/bib-and-figures.md) for detailed procedures and pitfalls.

For the full picture of adding chapters from a survey or creating a new survey book, see [references/survey-workflow.md](references/survey-workflow.md).

---

## Phase 3: Create the Main Document (overview.qmd)

### Procedure

1. **Analyze the structure**: understand the source text's chapter organization and major topics
2. **Create the skeleton**: decide the heading structure (`## Section` → `### Subsection`)
3. **Write the body**: describe the key point of each section concisely
4. **Mark supplementary-document candidates**: for concepts and terms that need detailed explanation, temporarily insert `[→ 詳細:]{.detail-link} [Supplementary Document Title](path.qmd)`

For a first-time-reader chapter, prefer **question → plain definition → one concrete example → structure → formalization → paper evidence → limits**. Do not begin with a method taxonomy or equations unless they are themselves the chapter's subject. Use [references/reader-first-revision.md](references/reader-first-revision.md) for revision details and terminology-provenance checks.

### Chapter-Title Format

Chapter-title rules differ by language:

- **ja / private**: H1 ≡ pagetitle ≡ sidebar text must match exactly; do not use bilingual `English: 日本語` titles with subtitles
- **en**: H1 may be fully descriptive and may include a subtitle; only pagetitle ≡ sidebar text is enforced

```markdown
# ja example
---
pagetitle: "Reasoning in Diffusion LLMs"
---

# Reasoning in Diffusion LLMs
```

```markdown
# en example (H1 with subtitle + shortened pagetitle)
---
pagetitle: "Multimodal DLM"
---

# Multimodal Diffusion Language Models
```

`overview.qmd` may use a book-title-style heading such as `# {Book Name} Technical Report Summary` (it is excluded from synchronization checks).

### Browser-Tab Title (`pagetitle`)

Add YAML front matter containing `pagetitle:` at the beginning of each chapter. Its value must exactly match the sidebar `text:` in `_quarto-public.yml` / `_quarto-private.yml`. `pagetitle:` affects only the HTML `<title>`; it does not affect the body H1 or title block. It is unnecessary in `index.qmd`, which already has `title:`.

### Link Syntax

Use relative paths for links from the main document to supplementary documents. Marking the link with a `.detail-link` span applies light styling from `styles.css`:

```markdown
[→ 詳細:]{.detail-link} [Supplementary Document Title](concept-name.qmd)
```

Do not use the old blockquote style `> 詳細: [...](...)`. Also omit trailing navigation blockquotes (`> 次章:` / `> 関連文書:` / `> 概要に戻る:`), which are redundant because the sidebar provides navigation.

### Use Linked Chapter Names for Cross-Chapter References, Not Chapter Numbers

When referring to another chapter, **always use the chapter name + a qmd link**:

```markdown
The prefix consensus discussed in [Self-Consistency and Weighted Majority Voting](self-consistency.qmd) ...
See also [Process Reward Model](process-reward-model.qmd).
```

**Do not refer to chapters by number**, such as “Chapter 4.” Reasons:

- Filenames have no numeric prefixes because the sidebar controls chapter order; merely reordering the sidebar would make numbers in the body incorrect
- Each chapter is intended to be read as an independent supplementary document, so number references premised on linear reading violate that assumption
- A chapter name tells readers immediately what it contains

For self-references within a Japanese chapter, use **`本章`** (“this chapter”). Replace existing “Chapter N” references with a linked chapter name when they refer to another chapter, or with “this chapter” / `本章` when they are self-references.

### Figures, Tables, Diagrams, and Cross-References

Figures and tables have a major effect on information density in technical documents.

- **Insert a figure**: use `![Caption. Source: [@bibkey]](image.png){#fig-name width="80%"}` and refer to it with `@fig-name` (the source citation must **always use brackets: `[@key]`**. Do not write unbracketed `Source: @key`; it does not become a parenthetical citation and produces inconsistent rendering within the book)
- **Create a table**: use a pipe table or list table and refer to it with `@tbl-name`
- **Diagrams**: use Mermaid / Graphviz for flowcharts and classification trees
- **Cross-references**: use the consistent prefixes `@fig-`, `@tbl-`, `@sec-`, `@eq-`, and `@thm-`
- **Equations**: use KaTeX (LaTeX syntax), with `$x^2$` inline and `$$\sum_{i=1}^{n}$$` as display math

See `references/quarto/cross-references.md`, `references/quarto/figures.md`, `references/quarto/tables.md`, and `references/quarto/diagrams.md` for details.

### Importing Figures from Papers (from arXiv E-Prints)

For a book based on papers, **directly citing figures from the original papers** substantially increases visual density. Because arXiv distributes the complete LaTeX sources, the original-resolution images can be obtained directly.

```bash
# One paper
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures.py 2406.07524

# Batch from a bibliography (commonly run in Phase 2)
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures_batch.py \
    --bib {book}/references.bib --parallel 8
```

Procedure:

1. Run the script with an arXiv ID → original images are extracted to `/tmp/arxiv_figures/{id}/`
2. Select the figures to use in the book (typically the graphical abstract, main method figure, and results figures)
3. If a figure is a PDF, convert it to PNG: `pdftoppm -r 200 -png input.pdf output`
4. Copy it to `{book}/images/` using a **meaningful name** (`mdlm-overview.png`, `llada-semi-ar.jpg`, etc.)
5. Insert it in the `.qmd` file as `![Caption. Source: [@bibkey]](images/foo.png){#fig-name}`
6. Mention it in the body with `@fig-name`

Hierarchical fallback:

- **A. arXiv e-print** (this script) — first choice and highest quality
- **B. pdffigures2**, etc. — for PDFs not supported by arXiv (future)
- **C. Crop with a vision LLM** — last resort (future)

### Mermaid Is Off by Default; Use It Only When Effective

Mermaid is useful, but casual use often creates tall diagrams that occupy too much screen space. **If a paper already contains a suitable figure, always prefer that figure**.

Use Mermaid only in a small number of cases:

- A **concept map / genealogy / classification tree spanning papers** (a figure not present in the original papers)
- A **decision or branching flow** (such as “when to use X”)
- A **dependency graph** (an A → B → C structure)

Avoid Mermaid in these cases:

- The paper already has a figure → obtain it from the arXiv e-print
- Structured data → use a Quarto table
- Algorithm flow → pseudocode in a `{python}` block is sufficient
- A list merely enclosed in boxes
- **A chapter-by-axis flowchart used as an “overall map” in the overview** — arrows tend to be ambiguous about whether they mean conceptual connection, dependency, or influence, and duplicating both chapter nodes and the body’s chapter layout repeats the same information. In most cases, the body’s chapter organization and a short introductory paragraph are sufficient

### Use Theorem Environments for Mathematical Propositions

Write theorems, lemmas, corollaries, propositions, definitions, and examples as labeled divs:

```markdown
::: {#thm-mdlm-loss}
## MDLM Objective [@sahoo2024mdlm]

Under a continuous-time absorbing forward process, the negative ELBO of MDLM is ...

$$
\mathcal{L}_\text{MDLM} = \dots
$$ {#eq-mdlm-loss}
:::
```

Available prefixes: `#thm-` theorem, `#lem-` lemma, `#cor-` corollary, `#prp-` proposition, `#def-` definition, `#exm-` example, and `#exr-` exercise. See `references/quarto/divs-and-spans.md` for details.

### Citations and References

Centralize bibliographic information in BibTeX and cite it in the body with `[@key]`:

1. Create `references.bib` directly under the book directory (building it in one place during Phase 2 is recommended)
2. Add `bibliography: references.bib` to `_metadata.yml`
3. Cite sources in the body with syntax such as `[@sahoo2024mdlm]`

Do not add a `## 参考文献` (“References”) heading or a `::: {#refs}` block. Pandoc/Quarto reads `bibliography:` and **automatically inserts the reference list at the end of the document**.

Use the same style for bibliography entries as in normal paper writing (protect title capitalization with braces, include the full author list, and provide detailed fields). See `references/quarto/citations.md` for details.

Do not put internal information such as an OpenReview ID in a bibliography entry's `note` field because it becomes visible when published. `[NOTE_LEAK]` in `lint_chapters.py` detects this mechanically.

### Reuse Notation with Include

Move notation definitions and shared components repeated across chapters into `_shared/` and include them:

```
{lang}/{book}/
├── _shared/
│   └── notation.qmd          # Notation shared across chapters
├── mdlm.qmd                  # Includes {{< include _shared/notation.qmd >}} here
└── llada.qmd                 # Includes the same file here
```

Because `_shared/` starts with an underscore, Quarto automatically excludes it from rendering targets. See `references/quarto/shortcodes.md` for details.

---

## Phase 4: Generate Chapters in Parallel

### Purpose

For each concept or chapter marked in the main document, use subagents (the Task tool) to generate **body text + citations + figure insertion** in parallel as one assignment.

Avoid the antipattern of “write only the text now and retrofit figures later.” Inspect source figures and decide whether each one adds information while drafting the chapter.

### Choose Figures by Information Need, Not by Quota

Inspect paper figures while writing the chapter, but do not impose a per-chapter or per-book figure count. Keep a figure only when it explains a relationship, result, or mechanism more clearly than prose or a table. A chapter may contain no figure when no figure adds information. Never create Mermaid solely to satisfy a count; Mermaid remains off by default.

### Procedure

1. **Extract chapter candidates**: list locations marked with `[→ 詳細:]{.detail-link}` in the main document
2. **Launch subagents**: generate chapters in parallel by calling multiple Task tools at the same time
3. **Check results**: inspect each subagent's output and lint results

### Subagent Prompt

Ready-to-use template: [assets/subagent-prompts/chapter-writer.md](assets/subagent-prompts/chapter-writer.md)

This template includes:

- An instruction requiring the subagent to read `formatting-rules.md`
- The assumption that `references.bib` has already been built (new bibliography entries are prohibited)
- Instructions to select figures from `/tmp/arxiv_figures/<id>/`, convert them to PNG with `pdftoppm`, and place them in `images/`
- A requirement to justify figures by information need rather than count
- The reader-first order and a terminology-provenance check
- Every CRITICAL rule, including no exposed bibliography keys, no exposed `.qmd` slugs, bold-syntax safety, and expansion of abbreviations at first use

Fill in the `{...}` placeholders for each chapter.

### Add Book-Specific Requirements to Each Chapter Prompt

In addition to the template, reinforce the following as appropriate for each book:

- **Prohibited topics** — internal laboratory information, unpublished research directions, or other material that should not be public
- **Handling specific papers** — for example, instruct the subagent to treat the author's own paper evenly rather than making it the “star”
- **Avoiding overlap with other chapters** — specify which chapters should be complementary

---

## Phase 5: Add Supplementary Callouts

### Purpose

Use Quarto callouts to add useful supplementary information that falls outside the main thread.

### When to Use Callouts

- Comparisons with other models or methods
- Advanced material, such as applications not discussed in the paper
- Reference information not required to understand the body
- Mentions of sources and references

### Syntax

```markdown
::: {.callout-note collapse="true"}
## Comparison with Other Models: Qwen3 and DeepSeek

Qwen3 uses full attention rather than SWA ...

**Reference**: [Qwen3 Technical Report](https://arxiv.org/abs/...)
:::
```

**Every callout must have a `## Heading`.** Headed callouts are standard in this book, and mixing in callouts without headings breaks consistency and draws attention. Even a short, one-sentence callout needs a concise heading that describes its content (Japanese example: `## DLLM の理論基盤は別書を参照`).

Callout types:

- `.callout-note` — supplementary information (blue)
- `.callout-tip` — tip (green)
- `.callout-important` — important information (red)
- `.callout-warning` — warning (orange)
- `.callout-caution` — caution (red)

Options:

- `collapse="true"` — collapsible
- `collapse="false"` — expanded by default (also the behavior when omitted)

See `references/quarto/callouts.md` for details.

### Procedure

1. Scan the main and supplementary documents to identify places where comparisons or advanced material can be added
2. Insert callouts

---

## Phase 6: Configure index.qmd and _quarto.yml

Once supplementary documents are finalized, create the book's landing page (`index.qmd`) and integrate it into site-wide navigation.

Complete procedure, templates, and sidebar language rules: [references/index-and-sidebar.md](references/index-and-sidebar.md)

Key points:

- **Inspect two or three existing book entries before writing `index.qmd`**. Follow the repository's landing-page baseline rather than inventing an extra call to action, table of contents, or “Structure of This Book” section
- **index.qmd is the book's “cover”**: what the book is, its source, and its date. The default is front matter plus one or two lead paragraphs, with no `##` headings or bibliography citations. An optional compact line may link directly to the primary paper, code, demo, or official project page. Always include `toc: false`
- **overview.qmd is optional**: when problem formulation, scope, notation, or the unit of comparison would make the index long, move them into `overview.qmd`. Do not duplicate the sidebar's chapter map in either file
- **Register every chapter in the `_quarto-public.yml` sidebar**: because index.qmd has no table of contents, the sidebar is the only entry point for chapter navigation

---

## Phase 7: Lint and Perform Final Checks

Complete procedure and checklist: [references/lint-and-checklist.md](references/lint-and-checklist.md)

Run these three automation scripts in order:

```bash
python3 .agents/skills/book-writer/scripts/fix_spacing.py {lang}/{book}
python3 .agents/skills/book-writer/scripts/fix_subfigures.py {lang}/{book}
python3 .agents/skills/book-writer/scripts/lint_chapters.py {lang}/{book}
```

For a survey-based book, also run a cross-check:

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py {lang}/{book} \
    --cross-check=/tmp/arxiv_figures/<survey_arxiv_id>/main.bib
```

`lint_chapters.py` detects:

- `[DANGLING]` — a body citation `[@key]` not defined in the bibliography
- `[BACKTICK]` — citations/cross-references enclosed in backticks (raw-rendering bug)
- `[META]` — meta references such as “citation key” or “bibliography entry”
- `[QMD_LEAK]` — a `*.qmd` filename exposed in body text
- `[SLUG_LEAK]` — a file slug exposed in parentheses
- `[DUP]` — duplicate keys in the bibliography
- `[NOTE_LEAK]` — an OpenReview ID or similar information in a bibliography `note` field
- `[TITLE_MISMATCH]` — a title mismatch with the reference bibliography (during cross-checking)

See `references/lint-and-checklist.md` for the detailed checklist and remedies.

### Additional Checks for an Augmentation Commit

When adding chapters or strengthening existing chapters after the initial release, semantic inconsistencies not caught by linting can easily appear: stale count expressions, forward/back references that depend on chapter order, forcing a family name derived from the new chapter's central method, excessive bridges to a specific paper, omissions of references to the new chapter, speculative performance predictions, and ja/en synchronization drift. `references/augmentation-consistency.md` documents seven observed review dimensions and grep snippets. **Run those checks before making an augmentation commit.**

### Phase 7.5: Verify Bibliography Entries for Hallucinations (Survey-Heavy Books Only)

In a survey-heavy book, bibliography authors or titles can differ from the real papers even after linting passes. Observed hallucinations include:

- A plausible but incorrect author identity
- Missing initials or other name components
- Authors added, removed, or reordered between arXiv revisions
- A stale title retained after a later revision changed it
- A submission venue or status mistaken for the final publication venue or status

Even `--cross-check` in `lint_chapters.py` cannot detect these when the survey itself contains an old title. As a final check, run a **verification pass that compares every bibliography entry individually against its arXiv abstract page**. See the “bibliography verification pass” section of [references/bib-and-figures.md](references/bib-and-figures.md) for the procedure.

### Phase 7.6: Clean Up Intermediate Files

Delete intermediate files generated during Phases 2 and 4 before publication:

- `{book}/bib_entries/` — temporary directory for parallel writes in Phase 4; delete it after merging
- `{book}/*.html` — stray HTML generated while validating with `quarto preview`
- `{book}/*.log` — Quarto / Pandoc logs
- `{book}/chapter-bib/` — legacy internal audit directory; internal paper/figure inventories belong under `/tmp/book-writer/{book_slug}/` and must never be committed or deployed

```bash
# Sanitize
find {book} -maxdepth 2 \( -name "*.html" -o -name "*.log" \) -delete
[ -d {book}/bib_entries ] && rm -rf {book}/bib_entries
[ -d {book}/chapter-bib ] && rm -rf {book}/chapter-bib
```

Before a public deployment, run the full-site render in a clean checkout or worktree that matches the CI file set. A local ignored private overlay can still be merged through the project's default profile even when `--profile public` is supplied. Use targeted book renders while editing, and do not use a root-wide render in a dirty mixed public/private tree as proof of the public build. After an interrupted render, inspect `git status` and delete only confirmed generated files; never use a broad cleanup command that could remove unrelated untracked work.

---

## Tips

### Context Management

- When the source text is long, extract only the key points in Phase 3 and assign details to individual subagents in Phase 4
- Give each subagent only the required sections rather than the entire source text
- For books with many citations, prebuilding the bibliography + figures in Phase 2 reduces the burden on chapter subagents

### Adjusting Parallelism

- When there are many supplementary documents, generate them in batches of three to five
- Generate them sequentially when dependencies exist (for example, explaining term A requires term B)

### Choosing among Figures, Tables, and Diagrams

| Information type | Recommended method | Example |
|------------------|--------------------|---------|
| Comparisons, lists, and structured data | Quarto table | Method comparison, experimental results, parameter list |
| Processes, flows, and relationships | Mermaid diagram | Pipeline, decision flow, dependencies |
| A paper's main message | Obtain from the arXiv e-print | Graphical abstract, method overview, scaling curve |
| Equations and algorithms | Code block + equations | Pseudocode, equation derivation |

Quarto tables support cross-references (`: Caption {#tbl-name}` → `@tbl-name`). Mermaid diagrams can also be referenced as figures when given captions and labels (`%%| label: fig-name`).

### Language-Specific Notes

Japanese (`ja/`):

- Use **である調** (plain assertive style, including endings such as `〜である`, `〜する`, and `〜となる`). Do not use **ですます調**
- Prefer original-language forms for paper titles and proper nouns
- Write callouts in Japanese as well

English (`en/`):

- Use clear, concise language
- Write callouts in English as well

### Expand Abbreviations and Selected Technical Terms at First Use

**Expand abbreviations and only those technical terms whose Japanese-English mapping is non-obvious or needed to align with figures, source terminology, or a book's central conceptual vocabulary.** Do not add English glosses to every technical noun. Readers may read each chapter independently, so repeat a selected expansion in each chapter where it matters.

Format:

- Japanese (`ja/`, `private/`): `日本語訳（English full form, ACRONYM）`
- English (`en/`): `English full form (ACRONYM)`

```markdown
# ja
強化学習（Reinforcement Learning, RL）を使用して...
変分下限（Evidence Lower Bound, ELBO）の最大化...

# en
Reinforcement Learning (RL) is used to...
Maximizing the evidence lower bound (ELBO)...
```

Core rules:

- **Each chapter is independent**: because every chapter may be read on its own, treat each chapter as a fresh first use
- **Keep selected Japanese terminology canonical**: for a term that genuinely needs an English gloss, introduce it as `日本語（English）`, then use the Japanese form for the rest of the chapter. Ordinary terms such as `モデル`, `プロンプト`, `ツール`, `タスク`, `スコア`, `コスト`, `環境`, `版`, `コンテキスト`, and `シード` normally need no gloss. Precommit the small glossary for parallel writing and audit it in Phase 7. See [references/style-consistency.md](references/style-consistency.md)
- **Expand abbreviations in the H1 in the first body paragraph**: for example, if the title is `# LLaDA: MDLM 定式化を 8B にスケール`, do not put a parenthetical expansion in the H1 itself; expand it in the first body paragraph as `MDLM（Masked Diffusion Language Model）`
- **Use only the abbreviation from its second appearance within the same chapter**
- **Common abbreviations such as PDF / OCR / API / GPU / CPU are allowed without expansion**

Frequently expanded terms in ML books include LLM / VLM / DLLM / AR / RL / SFT / DPO / GRPO / PPO / RLHF / RLVR / MDLM / D3PM / SEDD / DDPM / DDIM / LDM / DSM / SDE / ODE / VAE / GAN / DiT / ViT / KV / RoPE / NTK / SNR / KL / ELBO / VLB / NFE / FID / FLOP / SOTA / CoT / MCTS / MDP / DAG / MLE / MAP / CNN / RNN / MLP / ReLU / SVD / NLL / MSE / EM / GMM / GP / RBF / DNN / BNN / MoE / PRM.
