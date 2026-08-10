---
name: book-writer
description: |
  Use when writing or revising Quarto technical books from papers, surveys, or technical sources.
  Covers new books, chapter augmentation, bilingual synchronization, translation, figures, citations,
  navigation, and publication checks while keeping shared state under one parent agent.
---

# Book Writer

Produce reader-first technical books whose claims, citations, figures, navigation, and language editions remain consistent. `SKILL.md` is the orchestration contract; detailed rules live in the linked references and prompt templates.

## Core Contract

- Inspect the source, nearest existing books, and current repository state before designing or editing.
- Use primary sources for technical claims. Keep bibliography metadata, shared notation, navigation, and the book-wide glossary under parent-agent ownership.
- Give every page one reader question. Do not turn a survey taxonomy or method inventory into the book structure without a reader-facing reason.
- Keep Japanese and English editions synchronized in page set, information structure, claims, citations, and figure placement unless an intentional language-specific difference is documented.
- Choose figures by information value, never by quota. Prefer primary-paper figures to decorative diagrams.
- Use named chapter links, not chapter numbers. Preserve existing URLs unless the user explicitly approves a rename.
- Use privacy-safe synthetic or role-based examples. Real people appear only when source attribution requires them.
- Run the smallest checks that prove the changed scope is valid. Do not use a repository-root preview for a single-book or single-page change.

## Route the Task Before Loading Details

Load only the references required by the task:

| Task | Required reference |
|---|---|
| New book or ordinary chapter writing | [references/writing-workflow.md](references/writing-workflow.md) |
| Survey-derived book or multi-paper augmentation | [references/survey-workflow.md](references/survey-workflow.md) |
| Translate an existing language edition | [references/translation-workflow.md](references/translation-workflow.md) |
| Prebuild bibliography and source figures | [references/bib-and-figures.md](references/bib-and-figures.md) |
| Create `index.qmd` and configure the sidebar | [references/index-and-sidebar.md](references/index-and-sidebar.md) |
| Rewrite a dense but technically correct chapter | [references/reader-first-revision.md](references/reader-first-revision.md) |
| Standardize terminology, titles, and style | [references/style-consistency.md](references/style-consistency.md) |
| Validate a new edition or ordinary change | [references/lint-and-checklist.md](references/lint-and-checklist.md) |
| Validate later chapter augmentation | [references/augmentation-consistency.md](references/augmentation-consistency.md) plus the normal lint checklist |

Every writing or translation subagent must read [assets/formatting-rules.md](assets/formatting-rules.md). For exact Quarto syntax, open only the relevant file under `references/quarto/`.

## Workflow and Gates

### Phase 1 — Scope and Set Up

Use [writing-workflow.md](references/writing-workflow.md) to determine language, public/private boundary, source material, book role, page roles, directory, metadata, titles, and slugs.

**Gate:** the book root and shared-file ownership are explicit; an existing book's sidebar, bibliography, links, and language counterpart have been inspected.

### Phase 2 — Prebuild Bibliography and Figures When Needed

For survey-heavy or citation-heavy work, normally around 30 or more references, centralize `references.bib` and inspect available primary-source figures before drafting. Use [bib-and-figures.md](references/bib-and-figures.md) and its prompt templates.

For a small single-paper guide, skip this phase and add verified citations while writing.

**Gate:** bibliography ownership is singular, metadata is validated, and the figure manifest or explicit source-figure review exists. A zero-figure book is valid after inspection, not before it.

### Phase 3 — Define the Overview and Chapter Plan

Write the problem, scope, unit of comparison, notation, and page responsibilities before parallel chapter work. Use the reader-first order and resolve overlap in the plan rather than after drafting.

**Gate:** every planned page has a distinct reader question, named links replace numeric chapter references, and bilingual page structure is decided.

### Phase 4 — Write Independent Chapters

Dispatch independent chapters with [assets/subagent-prompts/chapter-writer.md](assets/subagent-prompts/chapter-writer.md). A chapter assignment owns prose, citations, and figure placement together; do not write prose first and retrofit evidence later.

The parent owns `references.bib`, shared notation, the sidebar, index, glossary, and cross-chapter review. Each subagent owns a disjoint file set and uniquely named images.

**Gate:** chapter claims are grounded in primary sources; the chapter adds a distinct reader decision; figures, citations, links, and local lint are valid.

### Phase 5 — Add Callouts Only When They Protect the Main Thread

Use headed callouts for useful comparisons, advanced extensions, warnings, or compact reference material that would interrupt the argument. Callouts are optional and must not hide essential definitions.

### Phase 6 — Create the Landing Page and Navigation

Use [index-and-sidebar.md](references/index-and-sidebar.md). `index.qmd` is the short cover; `overview.qmd` owns longer problem formulation and scope. Register every page in the correct public/private sidebar.

**Gate:** H1, `pagetitle`, and sidebar labels satisfy the language-specific synchronization rules, and all relative links resolve.

### Phase 7 — Validate the Changed Scope

Use [lint-and-checklist.md](references/lint-and-checklist.md). Start with:

```bash
python3 .agents/skills/book-writer/scripts/fix_spacing.py {lang}/{book}
python3 .agents/skills/book-writer/scripts/fix_subfigures.py {lang}/{book}
python3 .agents/skills/book-writer/scripts/lint_chapters.py {lang}/{book}
```

Then render only the changed pages or book. Check the console for missing citations and inspect the generated pages that exercise changed figures, tables, equations, or navigation. Use a clean checkout/worktree only when the whole public build is the actual target.

For survey-heavy books, verify bibliography titles and authors against current primary records; a structurally valid BibTeX file can still contain plausible hallucinations. For augmentation, also run [augmentation-consistency.md](references/augmentation-consistency.md).

**Gate:** lint and targeted render pass; source links, citations, figures, titles, and bilingual parity are correct; intermediate `bib_entries/`, stray HTML/log files, and other confirmed generated artifacts are removed.

## Prompt Templates

| Ownership | Template |
|---|---|
| Chapter writing | [assets/subagent-prompts/chapter-writer.md](assets/subagent-prompts/chapter-writer.md) |
| Chapter translation | [assets/subagent-prompts/chapter-translator.md](assets/subagent-prompts/chapter-translator.md) |
| Central bibliography prebuild | [assets/subagent-prompts/bib-prebuild.md](assets/subagent-prompts/bib-prebuild.md) |
| Batch source-figure prefetch | [assets/subagent-prompts/figure-prefetch.md](assets/subagent-prompts/figure-prefetch.md) |

Fill every placeholder. Add the exact source, owned files, neighboring context, prohibited material, overlap boundaries, small canonical glossary, permitted figure names, and verification command. Do not let a subagent infer shared-file ownership.

## Non-Negotiable Writing Rules

- Japanese uses である調; English uses concise prose and repository-standard heading capitalization.
- Expand standard abbreviations at first use in each independently readable chapter.
- Add Japanese-English glosses only for important, non-obvious, or figure/source-aligned terms; do not make every technical noun bilingual.
- Prefer question → definition → example → structure → formalization → evidence → limits for first-time-reader chapters.
- Keep paper titles and proper nouns in their original forms.
- Never expose citation keys, `.qmd` filenames, slugs, internal audit notes, or private material in reader-facing prose.
- Do not manually add a references section when Quarto bibliography metadata already owns it.
- Do not add Mermaid, callouts, compatibility paths, or shared includes merely for symmetry.
