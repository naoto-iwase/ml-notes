# Core Writing Workflow: Phases 1, 3, 4, and 5

This reference owns the detailed authoring workflow that does not already belong to bibliography prebuild (Phase 2), navigation (Phase 6), or final validation (Phase 7). Read only the sections needed for the current task.

## Phase 1: Prepare the Book

### Inspect Before Creating

1. Confirm the language, public/private status, source material, and requested scope.
2. Inspect two or three nearby books in the same language and field. Match the repository's current structure and style rather than inventing a parallel convention.
3. For an existing book, inspect its sidebar entry, `_metadata.yml`, bibliography, chapter links, and language counterpart before editing.
4. Decide whether this is new writing, survey augmentation, translation, reader-first revision, or a small chapter edit. Route survey and translation tasks through their dedicated references.

Do not ask for information that is already recoverable from the repository or source document.

### Directory and Metadata

Use the language and publication boundary to choose the root:

| Directory | Purpose | Sidebar configuration |
|---|---|---|
| `ja/{book}/` | Public Japanese | `_quarto-public.yml` |
| `en/{book}/` | Public English | `_quarto-public.yml` |
| `private/{book}/` | Private | `private/_quarto-private.yml` |

Put material that is not cleared for public release, including source material with licensing concerns, under `private/`. A public source URL does not by itself make derived assets safe to publish.

A normal book has this shape:

```text
{base}/{book}/
├── _metadata.yml
├── index.qmd
├── overview.qmd          # Optional when the index would become too long
├── concept-a.qmd
├── references.bib       # When citations exist
└── images/
```

Minimal public metadata:

```yaml
sidebar: book-name-ja
bibliography: references.bib  # Omit when the book has no citations
```

Make `sidebar` match the sidebar `id`. Do not repeat `lang:` in a book-level `_metadata.yml`; the parent language directory already owns it. Create `index.qmd` only after the chapter set is stable in Phase 6.

### Filenames, Slugs, and Titles

- Use `.qmd` files with one-to-three-word kebab-case slugs; do not add numeric prefixes.
- Keep `overview.qmd` and `images/` as the conventional names.
- Choose a functional core noun phrase: `process-reward-model.qmd`, `latent-reasoning.qmd`, or `inference-acceleration.qmd`.
- Avoid opaque slugs such as `map.qmd` and verbose slugs that repeat the whole H1.
- Japanese and English editions use the same relative slug. Translate the visible title, not the filename.
- When a title changes enough that the slug becomes misleading, rename both and update every link and sidebar entry in the same change.
- Check whether the book title collides with an established field. Add a scope-defining modifier only when it resolves a real ambiguity.

Use [style-consistency.md](style-consistency.md) for naming and terminology rules.

## Phase 3: Write the Overview and Chapter Plan

### Give Each Page One Job

- `index.qmd` is the cover: what the book is, its source, and its date. Phase 6 owns it.
- `overview.qmd` defines the problem, scope, notation, unit of comparison, and chapter roadmap when those do not fit in the index.
- Each supplementary chapter answers one distinct reader question. Do not create a chapter merely to hold leftover material.

For a first-time reader, prefer:

> question → plain definition → one concrete example → structure → formalization → evidence → limits

Use [reader-first-revision.md](reader-first-revision.md) when a correct draft is still difficult to enter.

### Plan Before Parallel Writing

1. Read the primary source and identify the claims, mechanisms, evidence, and limitations the book must cover.
2. Define the role of every planned page and check for overlap.
3. Sketch H2/H3 structure before writing prose.
4. Decide which concepts need their own chapter and add named relative links, not chapter-number references.
5. For bilingual books, keep the page set, information structure, citations, and figure placement synchronized unless a language-specific adaptation is intentional.

### Titles and `pagetitle`

- Japanese/private: H1 ≡ `pagetitle` ≡ sidebar text.
- English: `pagetitle` ≡ sidebar text; H1 may be longer when a descriptive subtitle helps.
- `overview.qmd` may use a book-title-style H1 and is exempt from normal chapter-title synchronization.
- `index.qmd` uses `title:` and does not need `pagetitle:`.

Put chapter metadata before the H1:

```yaml
---
pagetitle: "Visible Sidebar Title"
---
```

### Links and Navigation

Use relative named links:

```markdown
See [Process Reward Models](process-reward-model.qmd).
```

Do not refer to another page as “Chapter N”; sidebar order can change. For Japanese self-reference, use `本章`. A styled detail link may be written as:

```markdown
[→ 詳細:]{.detail-link} [Process Reward Models](process-reward-model.qmd)
```

Do not add trailing “next chapter,” “related document,” or “back to overview” blockquotes; the sidebar owns navigation.

### Figures, Tables, Diagrams, and Equations

Choose media by information need:

| Information | Preferred form |
|---|---|
| Primary-paper mechanism or result | Original figure from the paper |
| Comparisons or structured values | Quarto table |
| A cross-paper relation not available in a source | Minimal Mermaid/Graphviz diagram |
| Formal statement or derivation | Equation or theorem environment |

There is no figure quota. Inspect available primary-source figures, but retain only those that communicate more clearly than prose or a table. Mermaid is off by default; do not draw a chapter map or boxed list merely to add a visual.

Fetch primary-source figures with:

```bash
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures.py <arxiv-id>
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures_batch.py \
  --bib {book}/references.bib --parallel 8
```

Place selected assets under `{book}/images/` with meaningful names. A figure caption must cite its source with `[@key]`, and the body must refer to the figure by its `@fig-...` identifier.

Use the focused Quarto references under `references/quarto/` for exact syntax. Do not copy large syntax manuals into a chapter prompt.

### Citations and Shared Notation

- Keep bibliography data in `{book}/references.bib` and cite it with `[@key]`.
- Do not add a manual references heading or `#refs` block; Quarto inserts the bibliography.
- Never expose citation keys, `.qmd` filenames, slugs, internal notes, or OpenReview IDs as prose.
- For notation genuinely shared across chapters, place the canonical definition under `_shared/` and include it with Quarto's include shortcode. Do not introduce `_shared/` for one short repeated sentence.

### Site Defaults Already Enabled

Do not repeat these in chapter YAML: image lightbox, citation hover, cross-reference hover, language-specific labels, the global Chicago author-date CSL, and linked citations. Book metadata usually needs only the sidebar ID and bibliography path.

## Phase 4: Generate or Revise Chapters

### Ownership

The parent agent owns shared state:

- book plan and chapter boundaries
- `references.bib`
- shared notation
- sidebar and index
- terminology glossary
- final cross-chapter and bilingual review

A chapter subagent owns one explicit set of `.qmd` files and uniquely named images. Do not allow multiple subagents to edit `references.bib`, the sidebar, or the same chapter concurrently.

### Dispatch

Use [the chapter-writer template](../assets/subagent-prompts/chapter-writer.md). It requires the subagent to read:

1. `assets/formatting-rules.md`
2. `references/style-consistency.md`
3. `references/reader-first-revision.md`
4. the assigned primary source and neighboring chapter context

Fill every placeholder and add book-specific requirements: prohibited material, exact scope, required sources, overlap boundaries, the small canonical glossary, and permitted image names.

Parallelize only independent chapters. Use batches sized to available ownership and compute, not a fixed quota. Serialize pages with content dependencies. Give each subagent only the source sections and neighboring context it needs.

### Chapter Acceptance

Before accepting a chapter:

- confirm that every section advances the chapter's reader question
- verify claims against primary sources
- inspect figure relevance and caption attribution
- check that links, citations, equations, and identifiers render rather than leak as raw syntax
- remove repeated overview material, method inventories without a reader decision, and unsupported generalization
- run the chapter-level checks requested by the prompt; the parent still performs the book-level Phase 7 checks

## Phase 5: Add Supplementary Callouts Only When Needed

A callout is optional. Use one only for material that is useful but would interrupt the main argument: a comparison, advanced extension, operational warning, or compact reference note.

Every callout must have a descriptive `##` heading. Use the smallest appropriate type (`note`, `tip`, `important`, `warning`, or `caution`) and collapse long supplementary material when helpful. Do not use callouts as decorative summaries or to hide essential definitions.

See `references/quarto/callouts.md` for syntax.

## Canonical Style Rules

Do not duplicate the shared style specification in task prompts or book-local notes. The canonical details are in [formatting-rules.md](../assets/formatting-rules.md) and [style-consistency.md](style-consistency.md); the mandatory subset remains in `SKILL.md`.