# Reference: Consistency Checks for Later Augmentation

Adding chapters or strengthening existing chapters after the first edition can silently break consistency that originally held. Many such problems cannot be detected mechanically by lint, and running this checklist before committing an augmentation substantially reduces proofreading cost.

Run this checklist in addition to the Phase 7 lint. **You may skip it for the initial edition.** Use it only before committing an augmentation that adds text to the book or existing chapters.

## Why Later Augmentation Breaks Consistency

An augmentation commit typically adds a new chapter, inserts a section into the middle of an existing chapter, or appends a section to an existing chapter. The problem is that **dispersed consistency anchors** far from the augmentation's diff hunk become stale at the same time. Lint detects syntactic consistency problems such as bibliography integrity and H1 synchronization, but **semantic anchors** are difficult to detect mechanically: for example, how many times the prose states the book's paper count, or where a list states the total number of observations.

Typical problems observed together in commit `edf6637`, which augmented the `reliable-reasoning` book:

- The end of the overview still said "the four observations above" after observations 5 and 6 were added.
- In `tree-search.qmd`, "PC (including the Self-Consistency family discussed later)" needed to say "discussed earlier" after accounting for the sidebar order.
- The label "Prefix Consistency family" leaked into the overview and made one newly covered method the parent of six pre-existing independent methods.
- Four new "relationship between X and Y" bridges appeared at the ends of sections in the new chapter, compromising the chapter's neutrality.

## 1. Stale Counts

When augmentation adds chapters, citations, observations, or similar items, verify that every **expression counting them** has been updated. These are relatively easy to find with `grep`.

```bash
# Collect count expressions; the alternatives are Japanese counting terms used in Japanese books
grep -nE "[0-9０-９]+\s*(つの|本超|本の|章|節|点|主軸|観察|系統)" {lang}/{book}/*.qmd
```

Review points:

- Paper counts in the overview / index, for example, `more than 170 papers` → `more than 190 papers`.
- Counts of observations or findings, for example, `four observations` → `six observations`.
- Count expressions in end-of-chapter summary lists, for example, `the following three points` → `the following four points`, or `three main axes` → `five main axes`.
- Number of chapters, for example, `This book has eight chapters` → `This book has nine chapters`.

WHY: a statement that counted "N in total" in the first edition becomes stale as soon as augmentation raises the count to N+k. Because the statement is absent from the augmentation diff, human reviewers often miss it.

## 2. Order-Dependent Forward and Backward References

Changing the chapter order in the sidebar (`_quarto-public.yml`) or inserting a chapter can invalidate inter-chapter references such as "described earlier," "described later," "previous chapter," "next chapter," "previously discussed," "discussed later," and "following chapter."

```bash
# Extract forward/backward reference expressions; the first alternatives are Japanese fixtures
grep -nE "前述|後述|前章|次章|前項|previously discussed|discussed later|following chapter|previous chapter" {lang}/{book}/*.qmd
```

Compare every extracted line against the corresponding book section in the `_quarto-public.yml` sidebar.

WHY: "later" and "earlier" are relative positional references and become stale together when chapter order changes. Unlike an absolute reference such as `@chapter-name`, they require mechanical discovery followed by human judgment.

## 3. Imposing a Method Name on an Entire Family or Category

When a newly added chapter centers on **one particular method**, wording can leak into the book that names the **entire pre-existing method family** after that method. For example, calling a prefix-based family of six independently developed methods the "Prefix Consistency family" makes one paper appear to be the family's parent.

Review from these perspectives:

- Does a newly introduced proper name followed by `系` / `系手法` / `ファミリー` / `family` refer not only to the new paper but to an entire existing set of methods? The Japanese suffixes mean "family," "family of methods," and "family," respectively.
- Has terminology from the new chapter overwritten an established family name in existing chapters? Japanese examples include `prefix を活用する系` ("the family that uses prefixes"), `重み付け系` ("the weighting family"), and `Self-Consistency 系` ("the Self-Consistency family").

```bash
# Check whether a new term is being used as a family name
grep -nE "<new-term>\s*(系|系手法|ファミリー|family)" {lang}/{book}/*.qmd
```

WHY: family names define the semantic map of the entire book. Naming a family after one paper makes readers perceive that paper as the family's representative and therefore overvalues it. A valid family label should name a **structural feature** that abstracts across all N independent methods in the family.

## 4. Excessive Bridges to One Paper

When a new chapter is conceptually close to a particular method in an existing chapter, writers tend to append a "relationship between X and Y" bridge to the ends of **multiple sections** in the new chapter. One or two bridges are healthy; bridging to the same paper in four or more places within one chapter compromises neutrality.

Aggregate citation counts within each chapter to make outliers visible:

```bash
# Citation count by bib key within each chapter (highest first)
for f in {lang}/{book}/*.qmd; do
  echo "=== $f ==="
  grep -oE "@[a-z]+[0-9]+[a-z]*" "$f" | sort | uniq -c | sort -rn | head -8
done
```

If one bibliography key is cited at least as often as the chapter's principal papers, meaning the papers named in the chapter title or section headings, that is a sign of excessive bridging.

The same paper name appearing in multiple section titles (`### ...`) is another warning sign:

```bash
# Detect a chapter containing the same paper name in section titles
grep -nE "^###?\s+.*Prefix Consistency" {lang}/{book}/<new-chapter>.qmd
```

WHY: appending "the relationship between X and Y" to every section causes the chapter's argument to converge on how X connects to every other concept. The chapter's intended protagonists, such as the four source papers of a new chapter, are pushed into the background. This structure is especially likely around the writer's own or favored paper, making it difficult for the writer to notice.

## 5. Missing Mentions of the New Chapter

After adding a chapter, update every location that originally served to enumerate all chapters.

- Does the overview / index chapter list include the new chapter?
- Does the overview section describing the scope of each chapter include a mini-summary of the new chapter?
- Should the cross-cutting observations section, for example, "Observation 1," "Observation 2," and so on, add the new chapter's topic as an independent observation?
- Should closely related end-of-chapter summaries in existing chapters add a "see also [new chapter name]" link?

A mechanical comparison against the chapter list can detect omissions:

```bash
# Check whether the new chapter slug appears in overview / index
grep -l "<new-chapter-slug>.qmd" {lang}/{book}/overview.qmd {lang}/{book}/index.qmd
```

WHY: if a new chapter is absent from the overview / index, readers can reach it through the sidebar but cannot see it in the explanation of the book's overall structure. Readers who build their mental map from the overview may perceive it as an isolated supplementary chapter.

## 6. Speculative Claims and Performance Predictions

A new chapter that "reevaluates" methods from existing chapters can accumulate performance predictions unsupported by papers. These predictions are particularly likely to favor **the writer's own method**. The safest choices are to frame them as open questions or remove them.

Risky Japanese sentence patterns, retained as search fixtures with English meanings:

- `X は Y と同等のポテンシャルがある` — "X has potential equivalent to Y."
- `X は Y の代替になりうる` — "X could substitute for Y."
- `X は Y と同じ効果が期待される` — "X is expected to have the same effect as Y."
- `X は Y の逆相関指標として機能する` — "X functions as an inversely correlated proxy for Y," when no empirical comparison has been published.

```bash
# Detect speculative forms; Japanese alternatives are fixtures for Japanese books
grep -nE "同等のポテンシャル|代替になりうる|同じ効果が期待|逆相関指標|equivalent potential|inverse-correlated proxy" {lang}/{book}/*.qmd
```

WHY: a performance prediction between methods without empirical support in the literature raises the perceived value of the writer's favored method. It may feel like a reasonable inference to the writer but read as a definitive claim. Replace it with explicit hedging such as the Japanese literal phrases `open question として残る` ("remains an open question"), `未公表` ("unpublished"), or `経験的比較は今後の課題` ("empirical comparison is future work") to preserve the book's credibility.

## 7. Japanese / English Synchronization

For books with both Japanese and English editions, augmentation can land on only one side while the other remains stale.

```bash
# Check symmetry in qmd file counts and line counts between ja and en
for chapter in ja/{book}/*.qmd; do
  base=$(basename "$chapter")
  en="en/{book}/$base"
  if [ -f "$en" ]; then
    ja_lines=$(wc -l < "$chapter")
    en_lines=$(wc -l < "$en")
    diff_pct=$(echo "scale=1; ($ja_lines - $en_lines) * 100 / $ja_lines" | bc 2>/dev/null)
    echo "$base: ja=$ja_lines en=$en_lines diff=${diff_pct}%"
  fi
done
```

A large line-count difference, for example, at least ±30%, suggests that only one edition may have been augmented. The check detects omissions in either direction: English only or Japanese only.

WHY: `lint_chapters.py` checks H1 / `pagetitle` / sidebar synchronization across Japanese and English through `[TITLE_XLANG]`, but it cannot detect differences in body-section structure or newly added callouts.

## Order of Application

Before committing an augmentation, run at least these checks in order:

1. Use `grep` to check item 1, stale counts.
2. Use `grep` to check item 2, earlier / later references.
3. Use the newly introduced terms with `grep` to check item 3, imposed family names.
4. Aggregate citation counts to check item 4, excessive bridges.
5. Inspect the overview / index for item 5, mentions of the new chapter.
6. Read the new chapter and use `grep` to check item 6, speculative claims.
7. Compare line counts for item 7, Japanese / English synchronization.
8. Run the normal Phase 7 lint, `lint_chapters.py`.

For the mechanically detectable checks, you may write a thin per-book wrapper such as `scripts/check-augmentation.sh` so that all `grep` commands run together.
