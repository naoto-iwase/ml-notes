# Bibliography Pre-build subagent prompt template

Use this template to have one subagent build the entire `references.bib` at once in Phase 2. It is especially effective for survey-heavy books with 30 or more citations. It serves two purposes: preventing chapter subagents from inventing conflicting bib keys, and centralizing hallucination checks for paper titles and authors in **one place**.

---

```
You are a subagent using the book-writer skill. Work in Japanese.

## Role

Create a **single consolidated** `references.bib` for the book at `{book_dir}` from scratch. Chapter subagents will refer to it later, so bib keys, titles, and authors must be extremely accurate.

## Files You Must Read First

1. `{skill_root}/references/quarto/citations.md` — formatting specification for bib entries
2. `{source_files}` — primary sources (survey Markdown, paper lists, or notes); read all of them if there are multiple files
3. `{book_dir}/references.bib`, if it already exists, for reference (even when rebuilding rather than appending)

## Bib Key Naming Convention

- Format: `{firstauthor_lastname_lowercase}{year}{shortname_lowercase}`
- Examples: `doe2025method`, `roe2024benchmark`, `smith2023survey`
- For `shortname`, use the method abbreviation when one exists; otherwise, use one short topic word
- **Do not use the `anon...` form.** If an arXiv preprint exists, the real names are available. Even when the OpenReview submission remains double-blind, the arXiv version usually lists the authors

## Entry Structure

```bibtex
@article{doe2025method,
  title   = {A {V}erified {P}aper {T}itle},
  author  = {Jane Doe and John Roe},
  journal = {arXiv preprint arXiv:XXXX.XXXXX},
  year    = {2025},
  note    = {Spotlight},
  url     = {https://arxiv.org/abs/XXXX.XXXXX},
}
```

- **title**: protect capitalization with braces (use `{T}` to protect an initial)
- **author**: full names separated by `and` (list every author; `others` may be used to abbreviate). **`Anonymous` is prohibited.** Always confirm the real names from the latest arXiv version
- **type / journal / booktitle**: for an arXiv preprint, use `@article` + `journal = {arXiv preprint arXiv:XXXX.XXXXX}`; for an accepted paper, use `@inproceedings` + `booktitle = {...}`. These forms are mutually exclusive; do not leave `journal` inside an `@inproceedings` entry
- **note**: include only supplemental information such as Oral, Spotlight, or Poster. The venue belongs in `booktitle`. **Never write an OpenReview short ID** (for example, `OpenReview 4smJ6zY7vy`) because it will be exposed in the published output
- **url**: for accepted papers, prefer the **venue URL** from OpenReview or ACL Anthology; for preprints only, use `https://arxiv.org/abs/XXXX.XXXXX`
- **year**: use the acceptance year for accepted papers (for example, 2026 for ICLR 2026); otherwise, use the year of the first arXiv version

Standard `booktitle` values by venue:

| venue | booktitle |
|-------|-----------|
| ICLR | `International Conference on Learning Representations` |
| NeurIPS | `Advances in Neural Information Processing Systems` |
| ICML | `International Conference on Machine Learning` |
| ACL (Main) | `Proceedings of the {N}th Annual Meeting of the Association for Computational Linguistics` |
| ACL Findings | `Findings of the Association for Computational Linguistics: ACL {YEAR}` |
| EMNLP Findings | `Findings of the Association for Computational Linguistics: EMNLP {YEAR}` |
| AAAI | `Proceedings of the AAAI Conference on Artificial Intelligence` |
| COLM | `Proceedings of the Conference on Language Modeling` |
| TMLR | `Transactions on Machine Learning Research` (keep `@article`) |

## Hallucination Safeguards

1. **Establish the arXiv ID first**: obtain the arXiv ID from a primary source, then use `WebFetch` on `https://arxiv.org/abs/{id}` and retrieve the title and authors from the latest version of the abstract page. Do not rely on a secondary survey
2. **Treat the latest arXiv version as authoritative**: papers progress through revisions such as v1, v2, and v3, and the **title can change substantially**. Use the abstract page's `<title>` tag rather than an outdated title in the survey
3. **Do not confuse a method name with a paper title**: retrieve the complete title from the primary record instead of expanding a method abbreviation into a plausible title
4. **Identify the first author's last name correctly**: trust the author order and name formatting on the arXiv abstract page rather than inferring surname boundaries
5. **Never write `author = {Anonymous}`**: do not copy Anonymous from a double-blind OpenReview submission page. An arXiv preprint publishes the authors, so always verify it and enter their real names. There are no exceptions. If a paper is truly anonymous even on arXiv, which is extremely rare, reconsider whether to cite it
6. **Use OpenReview or ACL Anthology URLs for accepted papers**: a venue page is more stable than a bare arXiv preprint URL and communicates venue information to readers. Examples: `https://openreview.net/forum?id=XXXXX`, `https://aclanthology.org/YYYY.findings-acl.NNNN/`
7. **Do not put DOI or internal OpenReview IDs in `note`**: a public URL such as `https://openreview.net/forum?id=XXXXX` is acceptable, but a short ID such as `note = {OpenReview XXXXX}` is exposed at publication time and must not be included. `lint_chapters.py` detects this as `[NOTE_LEAK]`

## Output

1. Create or overwrite `{book_dir}/references.bib`
2. Create `{audit_dir}/_paper_index.md`, a lookup table for chapter subagents. `{audit_dir}` is `/tmp/book-writer/{book_slug}` and must not be placed under the public book tree:

```markdown
# Paper Index

List each paper's bib key, arXiv ID, first author, and planned chapter. Chapter subagents use this table to identify the keys for their chapters.

| bib key | arxiv ID | first author | title (abbrev) | planned chapter |
|---------|----------|--------------|----------------|-----------------|
| doe2025method | XXXX.XXXXX | Jane Doe | Verified Paper Title | ch1 |
| roe2024benchmark | YYYY.YYYYY | John Roe | Benchmark Paper Title | ch1 |
| ...
```

## Completion Checks

1. Run `python3 {skill_root}/scripts/lint_chapters.py {book_dir}` and confirm there are zero `[DUP]`, `[META]`, `[ANON_AUTHOR]`, and `[NOTE_LEAK]` findings
2. If the survey has a `main.bib`, run `python3 {skill_root}/scripts/lint_chapters.py {book_dir} --cross-check={survey_main_bib}` and confirm there are zero `[TITLE_MISMATCH]` findings

## Completion Report

Briefly report: "Bib entries: N," "Breakdown by planned chapter: ch1=X, ch2=Y...," and "Title/author verification: N papers checked with WebFetch."
```

---

## Notes for Using This Template

- Include multiple survey Markdown files in `{source_files}`, such as the result files produced by parallel survey subagents
- Set `{audit_dir}` to `/tmp/book-writer/{book_slug}`. It is internal scratch and must not be committed or deployed
- If `{survey_main_bib}` exists, always require the cross-check
- For a large bibliography with more than 80 citations, if one bib pre-build subagent cannot finish the work, split it across two or three domain-specific subagents and have the parent merge their results. One subagent may still be sufficient when the number of chapters matches the number of domains
- Start chapter subagents only after this phase finishes. Their contract prohibits creating new bib entries
