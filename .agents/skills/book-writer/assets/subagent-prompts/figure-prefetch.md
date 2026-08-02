# Figure Pre-fetch subagent prompt template

Use this template in Phase 2 to extract the arXiv e-print for every entry in `references.bib` under `/tmp/arxiv_figures/<id>/`. This lets chapter subagents immediately choose candidate figures by inspecting `ls /tmp/arxiv_figures/<id>/` for the papers in their chapters.

Because this task is simple, the parent may run `fetch_arxiv_figures_batch.py` directly instead of using a subagent. The only benefit of a subagent is keeping logs out of the parent's context.

---

```
You are a subagent using the book-writer skill.

## Role

Extract the arXiv e-print for every entry in `{book_dir}/references.bib` under `/tmp/arxiv_figures/<id>/`. After extraction, summarize the available image files for each paper.

## Tasks

1. Read `{book_dir}/references.bib` and extract arXiv IDs from fields matching `url = {https://arxiv.org/abs/XXXX.XXXXX}`
2. Run the following command; the script handles parallelism:

   ```bash
   uv run {skill_root}/scripts/fetch_arxiv_figures_batch.py \
       --bib {book_dir}/references.bib \
       --out /tmp/arxiv_figures \
       --parallel 8
   ```

3. After it finishes, create `{book_dir}/chapter-bib/_figure_manifest.md`:

```markdown
# Figure Manifest

List each paper's arXiv ID and fetched image files. Chapter subagents use this manifest to select candidate figures for their chapters.

## yue2025rlbeyond (2504.13837)
- /tmp/arxiv_figures/2504.13837/figs/teaser.pdf (215 KB) ★ graphical abstract
- /tmp/arxiv_figures/2504.13837/figs/passk-crossover.pdf (180 KB)
- /tmp/arxiv_figures/2504.13837/figs/aime-results.png (95 KB)

## wen2025cotpass (2506.14245)
- ...
```

Sort by descending size and then by file name. Mark likely message-bearing figures with ★ when file names suggest a `graphical abstract`, `teaser`, `overview`, `pipeline`, or `results` figure.

## Error Handling

- Papers not on arXiv, such as papers on another preprint server or outside the allowlist, may be skipped. Write `<not on arxiv>` in the manifest
- For download failures caused by rate limits or format errors, write `<fetch failed>` in the manifest and continue
- Do not stop after a few failures. If 90% succeed, chapter subagents can proceed

## Completion Report

Briefly report: "Fetched successfully: N of M papers," "Failed papers, if any," and "Manifest: {path}."
```

---

## Notes for Using This Template

- Be mindful of arXiv rate limits when setting parallelism with `--parallel 8`; this value has worked in practice
- For more than 100 papers, it may be easier for the parent to run the script directly rather than use a subagent, because the logs are easier to inspect
- If `/tmp/arxiv_figures/<id>/` already exists, the script skips it instead of downloading it again
