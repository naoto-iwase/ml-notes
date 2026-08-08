# Pre-Build the Bibliography and Figures (Phase 2)

For a citation-heavy book, especially a survey with an expected 30 or more references, build `references.bib` and `/tmp/arxiv_figures/` **in one place** before entering Phase 3, overview writing. This is Phase 2 and is a required gate unless the user explicitly waives source-figure inspection.

## Why Pre-Build Them

Lessons from past failures:

- **Inventing bibliography keys per chapter**: when chapter subagents independently create bibliography keys, the same paper can receive different keys or the wrong first author. The keys then require merging or renaming, and citations in `overview.qmd` must be rewritten afterward.
- **Hallucinated titles and authors**: when a subagent builds a bibliography from survey secondary sources alone, it may confuse a method name with a paper title or invent authors.
- **Figures deferred until later**: telling chapter subagents to "write prose only" drops the figure-acquisition phase. Figure usage then becomes extremely uneven across chapters, such as eight figures in one chapter and none in the others.
- **Duplicate retrieval of one arXiv ID**: several chapter subagents independently fetch the same paper's e-print and waste time.

Building the bibliography and figures first in Phase 2 prevents all of these problems structurally.

## When to Run Phase 2

- The book is expected to cite at least 30 works, as in a survey or multi-paper synthesis.
- The same papers are likely to be cited again in several chapters.
- A known bibliography, such as a survey's `main.bib`, can serve as the primary source.

For a book with few citations, such as a guide to a single paper, skip this phase and add citations as needed while writing the overview and chapters.

## Procedure

### Step 1: Start a Bibliography Pre-Build Subagent

Prompt template: `assets/subagent-prompts/bib-prebuild.md`

Key points:

- Have it read every primary source, such as survey Markdown and paper lists, and name bibliography keys in `{lastname}{year}{shortname}` format.
- Fetch each arXiv abstract page with WebFetch to establish the title and authors; do not rely on survey secondary sources.
- Create `{book}/references.bib`.
- At the same time, create `{book}/chapter-bib/_paper_index.md` as a mapping from key to arXiv ID, first author, and intended chapter.

### Step 2: Fetch Figures in One Batch

Run `fetch_arxiv_figures_batch.py`:

```bash
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures_batch.py \
    --bib {book}/references.bib \
    --out /tmp/arxiv_figures \
    --parallel 8
```

- Automatically extract arXiv IDs from `url = {https://arxiv.org/abs/XXXX.XXXXX}` fields in `references.bib`.
- Download in parallel and skip existing downloads.
- Continue after failures; a few failed papers must not stop the batch.
- With `--bib`, generate `{book}/chapter-bib/_figure_manifest.md` automatically. The manifest inventories image assets even for sources that were already downloaded.

For 100 or more papers, log tracking is easier if the parent runs the script directly rather than delegating it to a subagent.

Delegating this step is optional. If you do, use the prompt template `assets/subagent-prompts/figure-prefetch.md`.

### Step 2.5: Triage Figures Before and During Drafting

Do not treat a successful batch download as completion. The writer must inspect the manifest, then inspect the caption and surrounding source text for candidate figures relevant to each chapter.

Record decisions in the parent-owned `{book}/chapter-bib/_figure_triage.md`:

```markdown
| Chapter | Paper | Source figure | Decision | Reason |
|---|---|---|---|---|
| evaluation | `paper-key` | Figure 3 | keep | Shows the held-out protocol more clearly than prose |
| evaluation | `other-key` | Figure 1 | reject | Generic overview that duplicates the chapter table |
```

- A chapter may retain zero figures, but only after its relevant source figures have been inspected.
- “No figure-count quota” controls selection; it does not permit skipping inspection.
- Inspect captions and the claims supported by the figure, not only filenames or thumbnails.
- Chapter subagents report their decisions to the parent rather than racing to edit the shared triage file.
- Before publication, every chapter must have a recorded figure decision, including an explicit “no useful figure” decision when appropriate.

### Step 3: Validate the Bibliography

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py {book}
# If the survey provides main.bib
python3 .agents/skills/book-writer/scripts/lint_chapters.py {book} \
    --cross-check=/tmp/arxiv_figures/<survey_arxiv_id>/main.bib
```

- Confirm there are no `[DUP]` findings.
- Confirm there are no `[NOTE_LEAK]` findings, including exposed OpenReview IDs.
- Confirm there are no `[TITLE_MISMATCH]` findings, so titles agree with the primary source.

### Step 4: Explicitly Tell Chapter Subagents Not to Touch the Bibliography

When starting chapter subagents in Phase 4, include this explicit instruction in the prompt:

> Cite only entries already present in `{book}/references.bib`. Do not add new bibliography entries. If a paper you want to cite is absent from the bibliography, report that fact to the parent and stop.

This structurally prevents bibliography divergence between chapters.

### Step 4.5: The Per-Chapter `bib_entries/` Pattern (Avoid Parallel-Write Race Conditions)

If Phase 2 cannot complete the entire bibliography and chapter subagents must add entries individually, for example, when each chapter discovers new papers during its own research, require each subagent to write to a per-chapter file at **`{book}/bib_entries/<slug>.bib`**.

```
{book}/
├── references.bib              # Pre-built in Phase 2; edited directly by the parent
├── bib_entries/                # Parallel writes during Phase 4
│   ├── chapter-a.bib
│   ├── chapter-b.bib
│   └── ...
└── ...
```

Agent prompt:

> If you need to add a new bibliography entry, do not write to `{book}/references.bib`. Write only to **`{book}/bib_entries/<slug>.bib`**. The parent will merge it later.

After completion, the parent merges the files:

```bash
cat {book}/bib_entries/*.bib >> {book}/references.bib
rm -rf {book}/bib_entries  # Remove intermediate files during Phase 7.6 cleanup
```

This structurally prevents parallel agents from racing to write the same `references.bib`.

## Bibliography Verification Pass (Phase 7.5)

Even after all Phase 7 lint checks pass, bibliography-entry **authors and titles can disagree with the actual arXiv records**. Observed hallucinations include:

- A plausible but incorrect author identity.
- Missing initials or mishandled compound names.
- An omitted, added, or reordered coauthor in a later revision.
- A stale title retained after a later revision changed or extended it.
- A submission venue or status mistaken for the final publication venue or status.

Even `lint_chapters.py --cross-check` cannot detect these errors if the source bibliography contains the same mistake. **The final check must compare every bibliography entry individually against its arXiv abstract page in a verification pass.**

### Parallel Verification Procedure

For at least 30 bibliography entries, verify them in parallel with subagents, using four or five entries per batch:

```
Assigned bibliography keys (5):
- key1
- key2
- ...

Procedure:
1. Read the corresponding entries in references.bib.
2. Fetch each URL's arXiv abstract page with WebFetch.
3. Compare the record with the bibliography by author / title / year / venue / arXiv ID.
4. If an item is wrong, edit references.bib to correct it.
5. Apply the same correction to the source-information table in every relevant chapter qmd.

IMPORTANT: verify by fetching the arXiv abstract page directly. Preserve {X} braces that protect title capitalization.
Correct only definite errors.
```

Agent output format:

```
key1: ✅ OK
key2: ❌ Added one author (details)
key3: ⚠ Venue unknown (not listed on the arXiv abstract page)
```

### Beware of arXiv Version Drift

Papers are updated on arXiv from v1 to v2, v3, and later. A bibliography based on an old v1 record can diverge from current facts:

- Authors may be added, removed, or reordered.
- A later version may add, remove, or substantially change a title phrase.
- Venue and acceptance-status information may change after the initial submission.

During the verification pass, inspect the arXiv abstract page's "latest version." Do not pin a version by appending `vN` to the URL; use `https://arxiv.org/abs/XXXX.XXXXX` so the current version is always resolved.

### Beware of Venue Confusion

The bibliography's `booktitle` / `journal` fields are especially prone to hallucination:

- An arXiv preprint mentions `International Conference on Learning Representations`, but it was not actually accepted or was accepted at a different conference.
- Confusing `submission`, `accepted`, `Spotlight`, and `poster` statuses.
- Recording a submission venue as the final venue after the paper was accepted elsewhere.

Sources to verify:

1. The "Comments" field on the arXiv abstract page, for example, `Accepted to ICLR 2026 Spotlight`.
2. The decision tag on OpenReview.
3. Official proceedings, such as NeurIPS, ICLR, or ACL Anthology.
4. Venue information in the GitHub README.

If a venue cannot be confirmed, fall back to `arxiv preprint`. It is safer to write `@article{key, journal = {arXiv preprint arXiv:XXXX.XXXXX}, ...}` than to claim the wrong venue.

## File Layout

Book directory after completing Phase 2:

```
{book}/
├── _metadata.yml
├── references.bib              # Completed in Phase 2
├── chapter-bib/
│   ├── _paper_index.md         # Mapping from bib key to intended chapter
│   ├── _figure_manifest.md      # Generated inventory of extracted figure assets
│   ├── _figure_triage.md        # Parent-owned keep/reject decisions with reasons
│   └── (empty or per-chapter stash)
└── images/                     # Filled by chapter subagents in Phase 4
```

Every paper's e-print is then extracted under `/tmp/arxiv_figures/<id>/`. Chapter subagents inspect candidate figures there and report keep/reject decisions. Selected figures are converted to PNG with `pdftoppm` and copied into `{book}/images/`.

## Rebuilding an Existing Book

Use the same workflow when reviewing an existing book's `references.bib`, typically to unify keys that subagents invented independently:

1. Give the old `references.bib` to the bibliography pre-build subagent and use it as a primary source for a new unified version.
2. Generate a replacement map from old bibliography keys to new keys.
3. Replace `[@old_key]` with `[@new_key]` in every chapter qmd using `sed` or Edit.
4. Run lint to confirm consistency.
