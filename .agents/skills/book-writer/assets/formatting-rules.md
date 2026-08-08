# Book Writer - Formatting Rules

When creating supplementary documents as a subagent, follow the formatting rules below strictly.

For a comprehensive style-consistency checklist—including terminology consistency, sidebar section naming, checks that Mermaid diagrams serve a real purpose, and avoidance of casual English terms in Japanese—see [`references/style-consistency.md`](../references/style-consistency.md). Read it whenever writing a new book and when sweeping all chapters in Phase 7.

---

## 1. Choosing Figures, Tables, and Diagrams

Choose an appropriate representation for the type of information. **Do not use ASCII box drawings.** **Mermaid is off by default; use it only where it is effective.**

### Priority Order

1. **A figure exists in the paper** → obtain it from the arXiv e-print (highest priority)
2. **Structured data** → Quarto table
3. **Algorithm / equation** → pseudocode (Python) + LaTeX equations
4. **Cross-paper concept map / genealogy / decision flow / dependencies** → Mermaid (consider it only at this point)

### Paper Figures: Obtain Them from arXiv E-Prints

For books about papers, **directly cite figures from the original papers** whenever possible. They contain more information than newly created Mermaid diagrams and provide clear provenance.

```bash
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures.py 2406.07524
# Select figures from the listing → convert PDFs to PNG with pdftoppm → copy them to {book}/images/
```

Insertion format:

```markdown
![図のキャプション。出典: [@sahoo2024mdlm]](images/mdlm-overview.png){#fig-mdlm-overview width="80%"}
```

- Write what the figure shows in the context of this book; do not reuse the paper's original caption verbatim
- In Japanese captions, always append **`出典: [@key]`** (“Source”) with **brackets**. Unbracketed `出典: @key` is treated as an in-text citation rather than a parenthetical citation, causing inconsistent rendering among figure captions
- Use a meaningful filename; names such as `graphical_abstract_updated_3.png` are prohibited

#### Require Auto-Trim after Placement

PNGs derived from PDFs, especially those generated with `pdftoppm`, often retain large white margins. After placing them, always run:

```bash
uv run .agents/skills/book-writer/scripts/trim_whitespace.py {book_dir}
```

This Pillow-based script crops to the smallest bounding box whose difference from white exceeds a threshold:

- Images with no existing margin are a no-op (idempotent)
- It retains 12 px of padding so text is not cut off in figures whose axis labels reach the edge
- It supports both PNG and JPG

Prior example: of 31 images in one book, 24 needed trimming. The maximum reduction was 40% by area (`hrm-brain-pr.png`), and the average reduction in total area was 7%. Some images became visually much tighter, such as `lineage-looped-lego.png`, whose h/w ratio changed from 0.56 to 0.67. **Run it once during the Phase 7 sweep as well** so it also catches images added later.

#### Width: Check the Aspect Ratio

When inserting an image, `width="70%"` to `width="85%"` tends to become the default choice, but **these values are too large for portrait images (h/w > 1.3)**. Quarto's `width="80%"` means 80% of the container width and preserves the aspect ratio, so a portrait image can grow to nearly twice the container width in height and appear enormous.

Check the source image dimensions first:

```bash
sips -g pixelWidth -g pixelHeight images/foo.png  # macOS
identify images/foo.png  # ImageMagick (Linux)
```

Guidelines:

| h/w ratio | Recommended width | Examples |
|-----------|-------------------|----------|
| < 0.7 (landscape) | 85–95% | Scaling curves, performance-comparison bar charts |
| 0.7–1.3 (roughly square) | 70–85% | Architecture overviews, flow diagrams |
| 1.3–2.0 (portrait) | 40–55% | Tall algorithm diagrams, composite figures |
| > 2.0 (extremely tall) | 30–40% | Vertical pipelines, long equation lists |

Prior example: inserting an architecture figure from the TRM paper (1200×2372, h/w=1.98) at `width="78%"` made its height 1.55 times the container width, so it appeared enormous. `width="40%"` produced an appropriate size.

### Structured Data: Use Quarto Tables

Use them for comparison tables, experimental results, parameter lists, and similar content. They support cross-references.

```markdown
| Method | Accuracy | Cost |
|--------|----------|------|
| Best-of-N | 85% | High |
| Bo∞ | 90% | Medium |

: Method comparison {#tbl-comparison}
```

Refer to the table in the body as `@tbl-comparison`. See `references/tables.md` for details.

### Equations and Algorithms: Use Code Blocks + Equations

Write pseudocode in Python-style code blocks and mathematical definitions as LaTeX equations.

### Mermaid Is Off by Default (Use Only Conditionally)

**Stop and think before using Mermaid.** Casual use often produces tall diagrams that occupy too much screen space.

**Acceptable uses**:

- **A concept map / genealogy / classification tree not present in the papers** (for example, a genealogy spanning multiple papers)
- **A decision or branching flow** (such as “when to use X”)
- **A dependency graph** (an A → B → C structure when no paper figure exists)

**Unacceptable uses**:

- The paper already has a figure → obtain and cite it from the arXiv e-print
- Structured data → use a Quarto table
- Algorithm flow → pseudocode is sufficient
- A list merely enclosed in boxes
- Repeating the same information in the body, equations, and a diagram (information duplication is a quality penalty)

In particular, ordered procedures such as “sampling loops” and “processing pipelines” are usually covered by **a paper figure + pseudocode + prose**, so Mermaid is unnecessary.

If Mermaid is still warranted, use this format:

````markdown
```{mermaid}
%%| label: fig-genealogy
%%| fig-cap: "..."

flowchart LR
    A --> B --> C
```
````

See `references/diagrams.md` for details.

#### Checklist Before Drawing Mermaid

Prior example: a diagram advertised as a “two-axis map” actually arranged three levels along a single axis (LLM dependence). Because it duplicated information from a table, it was judged to have no purpose. To avoid casual Mermaid use, answer the following before drawing:

1. **Does the diagram express information that cannot be expressed elsewhere?** If a table suffices, use a table
2. **Are the advertised “two axes” or “three axes” truly independent?** Highly correlated axes reduce to a single ordering (for example, “presence of a language channel” and “degree of LLM dependence” are highly correlated and do not function as independent axes)
3. **Does it duplicate the immediately preceding table?** If so, remove either the diagram or the table
4. **Does it merely connect subgraphs in order with `-.->`?** Writing “A → B → C” in prose has higher information density

#### Do Not Use Unicode Arrows (→) inside Mermaid

Mermaid syntax uses ASCII arrows (`-->`, `-.->`, `==>`). Writing `→` (Unicode arrow, U+2192), familiar from Japanese prose, inside a Mermaid block prevents the parser from recognizing the token and causes a **syntax error**, so the diagram does not render.

```
flowchart LR
    A -.→ B    ← ❌ syntax error (Unicode arrow)
    A -.-> B   ← ✅ OK (ASCII)
```

Prior example: a refinement agent tried to standardize arrows inside Mermaid to `→` along with prose and broke the diagram. During Phase 7, run `quarto preview` and visually confirm Mermaid rendering. Detect `→` mechanically inside Mermaid blocks with grep:

```bash
for f in *.qmd; do
  awk '/^```\{mermaid\}/,/^```$/' "$f" | grep -nH "→"
done
```

---

## 2. Chapter Titles and the Sidebar

Chapter-title rules **differ by language**:

- **ja**: H1 ≡ pagetitle ≡ sidebar text must match exactly. **Do not use** a bilingual `# English: 日本語` form with a subtitle; it redundantly repeats the same term. The short label in sidebar text becomes the H1 unchanged
- **en**: H1 is a fully descriptive chapter name and may have a subtitle. Pagetitle may be a shorter form that matches sidebar text. H1 ↔ pagetitle is not enforced

### ja Chapter H1

Make each chapter H1 under `ja/` and `private/` **match sidebar text exactly**:

```markdown
---
pagetitle: "RLVR の理論と限界"
---

# RLVR の理論と限界
```

```markdown
---
pagetitle: "Reasoning in Diffusion LLMs"
---

# Reasoning in Diffusion LLMs
```

If the ja sidebar text is Japanese, use that Japanese text unchanged as the H1. If it remains English, use that English text unchanged as the H1. See the language rules in [`references/index-and-sidebar.md`](../references/index-and-sidebar.md).

### en Chapter H1

For `en/`, use English only. The title may include a descriptive subtitle:

```markdown
---
pagetitle: "Multimodal DLM"
---

# Multimodal Diffusion Language Models
```

```markdown
---
pagetitle: "Survey: Li et al. 2025"
---

# A Survey on Diffusion Language Models: A Map of Li et al. 2025
```

### overview.qmd and index.qmd

`overview.qmd` is where the main heading for the entire book belongs. It may use a book-title form such as `# {Book Name} Technical Report Summary` or the Japanese-title example `# Reliable Reasoning: 信頼できる LLM reasoning のための信号と手法` (it is excluded from H1 synchronization checks).

Because `index.qmd` has `title:`, it does not need `pagetitle:`.

### Do Not Put an Italic Lede Directly under H1

Begin immediately after the H1 (`# Chapter Title`) with a **normal body paragraph**. Do **not** add an abstract-like `*one-line italic lede*`.

```markdown
# X Chapter Title

*Italic lede ← prohibited*

Body paragraph ...
```

```markdown
# X Chapter Title

Body paragraph ... ← standard
```

Prior experience: refinement agents and chapter-writing subagents often add these spontaneously because they decide an abstract-like summary would be useful. This creates chapter-by-chapter inconsistency even within one book, and existing books such as reliable-reasoning and dllm do not use them at all. For consistency, omit them. See [`references/style-consistency.md`](../references/style-consistency.md) for details.

### Do Not Join a Heading and Subtitle with an Em Dash

Do not use `## X — Y` (em dash + subtitle). If the subtitle is needed, use `## X: Y` (ASCII colon + space). If it is redundant, remove it and use only `## X`.

Prior example: subagents tend to write headings such as `## Current Benchmark Status — Three Generations: 1, 2, and 3`. Although intended to improve readability, it makes heading style inconsistent across the book. Likewise, in list syntax use `**[X]** [@key]: Description` (colon), not `**[X]** [@key] — Description`.

### English Title Case Rules

Use **Chicago-style Title Case** consistently for **all English H1 / H2 / H3 / H4 headings**, `pagetitle`, `sidebar text`, and callout headings (`## Heading` form):

- Always capitalize the first and last words
- Capitalize words of four or more letters (`Reasoning`, `Diffusion`, `Models`)
- Lowercase short prepositions, conjunctions, and articles (`and`, `or`, `of`, `to`, `in`, `for`, `the`, `a`, `an`, `on`, `at`, `with`, `as`, `via`, `vs`, `by`, `from`, `but`, `is`), unless they are first or last
- **Capitalize the root after a hyphen as well**: `Long-Context`, `Test-Time`, `Self-Consistency`, `Post-Training`, `Pre-Trained`, `Self-Supervised`, `Step-Wise`, `Sampling-Based`
- Preserve abbreviations, model names, and proper nouns (`RLVR`, `GRPO`, `MCTS`, `MDLM`, `LLaDA`, `Molmo2`)

Why this applies to H2/H3 too: if different subagents write different chapters or augmentation commits, Title Case and sentence case easily diverge across chapters. Variants such as `## Chapter Summary` and `## Chapter summary` within one book are mechanically detected by `[H2_CASE]` / `[H3_CASE]` in `lint_chapters.py`.

Correct examples:

- H1: `Theory and Limits of RLVR`, `Self-Consistency and Weighted Majority Voting`, `Test-Time Compute Scaling`, `Reasoning in Diffusion LLMs`
- H2: `## Chapter Summary`, `## Adaptive Sampling and Early Stopping`, `## The Landscape After OpenAI o1`, `## Self-Supervised RL: R-Zero and Absolute Zero`
- H3: `## KV Cache Compression`, `## Speculative Reasoning`, `## Moving to Offline`

Avoid: `Test-time Compute Scaling` (lowercase root after hyphen), `Self-consistency and Weighted Voting` (missing capitalization), `Process Reward Model` ↔ `Process Reward Models` (singular/plural drift), and `## Chapter summary` (sentence case splits chapter-summary style).

Headings in JA (`ja/`, `private/`) are exempt from Title Case because Japanese has no case distinction. English terms inside a JA heading should still use their conventional casing (for example, `Self-Consistency と重み付き多数決` is correct; `self-Consistency と...` is not).

### Sidebar Titles (`text:`)

`text:` in `_quarto-public.yml` / `_quarto-private.yml` is a short navigation label. **Shortened English forms are allowed** to conserve sidebar width:

```yaml
- text: "Multimodal DLM"           # Shortened form is allowed
  href: ja/dllm/multimodal-dllm.qmd
- text: "Survey: Li et al. 2025"   # Short label with subtitle
  href: ja/dllm/survey-li2025.qmd
```

See [`references/index-and-sidebar.md`](../references/index-and-sidebar.md) for detailed language rules.

### Synchronization Rules

Maintain these relationships for each chapter:

1. **pagetitle ≡ sidebar text** (same language, required): the browser tab and sidebar use the same short label
2. **ja H1 ≡ pagetitle** (required): a ja H1 uses the same label as sidebar text, with no subtitle
3. **en H1 is unrestricted**: it may include a subtitle and need not match en pagetitle
4. **ja H1 ≡ en H1 main** (cross-language, only when ja H1 is English): skip this for chapters whose ja sidebar is localized into Japanese
5. **Visible text of overview `[→ 詳細:]` / `[→ Detail:]` links ≡ the target chapter's pagetitle / sidebar text**
6. **Visible text of cross-chapter body links ≡ the target chapter's pagetitle / sidebar text**

`lint_chapters.py` validates these with `[TITLE_SYNC]` / `[TITLE_XLANG]` (items 5 and 6 require manual review).

### Pagetitle (Browser-Tab Title)

Every chapter's YAML front matter must contain `pagetitle:`:

```markdown
---
pagetitle: "Sliding Window Attention"
---

# Sliding Window Attention: スライディングウィンドウアテンション
```

- Make the value of `pagetitle:` **match sidebar text exactly**
- `pagetitle:` affects only the HTML `<title>` and does not affect the body H1 or title block
- Because `index.qmd` has `title:`, it does not need `pagetitle:`

---

## 3. Quarto Syntax

### Callouts (Supplementary Information Boxes)

Use Quarto callouts for comparisons, advanced material, and supplementary information.

**Basic syntax** (`## Heading` is required):

```markdown
::: {.callout-note}
## Title
Content
:::
```

Every callout in this book must have a `## Heading`; mixing in callouts without headings breaks consistency. **Even a one-sentence callout needs a concise heading that describes its content** (Japanese example: `## 別書を参照`).

**Callout types**:

- `.callout-note`: supplementary information (default, blue)
- `.callout-tip`: hint / tip (green)
- `.callout-important`: important information (red)
- `.callout-warning`: warning (orange)
- `.callout-caution`: caution (red)

**Make it collapsible**:

```markdown
::: {.callout-note collapse="true"}
## Comparison with Other Models
Long content is collapsed by default.
:::
```

**Appropriate uses**:

- Comparison with other models or methods
- Advanced material that departs from the main thread but is useful to know
- Reference information and sources
- Detailed technical supplements

### Cross-References (Figures and Tables)

References to figures, tables, and sections occur frequently in technical documents.

**Figure reference**:

```markdown
![Caption](image.png){#fig-name}

Refer to it in the body as @fig-name.
```

**Table reference**:

```markdown
| Col1 | Col2 |
|------|------|
| A    | B    |

: Caption {#tbl-name}

Refer to it in the body as @tbl-name.
```

**Section reference**:

```markdown
## Section Title {#sec-name}

Refer to it in the body as @sec-name.
```

**Equation reference**:

```markdown
$$
y = mx + b
$$ {#eq-linear}

Refer to it in the body as @eq-linear.
```

See `references/cross-references.md` for details.

### Theorem Environments (Theorems, Lemmas, Definitions, etc.)

Use theorem environments for mathematical propositions that should be distinguished explicitly. Quarto numbers them automatically during rendering and allows references from the body.

```markdown
::: {#thm-mdlm-loss}
## MDLM Objective

Under a continuous-time absorbing forward process, the negative ELBO of MDLM is equivalent to:

$$
\mathcal{L} = \mathbb{E}_t \left[ \frac{1}{t} \dots \right]
$$ {#eq-mdlm-loss}
:::

Referring to @thm-mdlm-loss in the body links to "Theorem 1."
```

Available prefixes:

- `#thm-` theorem, `#lem-` lemma, `#cor-` corollary, `#prp-` proposition, `#def-` definition, `#exm-` example, `#exr-` exercise

See `references/divs-and-spans.md` for details.

### Citations and References

When the book directory has `references.bib` and `_metadata.yml` configures `bibliography:`, cite sources with `[@key]` syntax.

```markdown
MDLM [@sahoo2024mdlm] is a foundational formulation of masked diffusion [@austin2021d3pm].
```

- One citation: `[@key]` → `[1]`
- Multiple citations: `[@key1; @key2]` → `[1, 2]`
- Page specification: `[@key, p. 10]`
- Suppress author: `[-@key]` → `(2020)`

**Do not add a `## 参考文献` (“References”) heading or a `::: {#refs}` block.** When `bibliography:` is configured, Pandoc / Quarto **automatically inserts a list of cited references at the end of the document**. Writing an explicit heading or div duplicates the auto-inserted list. Explicitly write `::: {#refs} :::` only when moving its position, such as after an appendix.

When adding a new BibTeX entry, append it directly to `references.bib`. If an OpenReview URL is placed in the `url` field, the corresponding reference-list entry links to OpenReview.

#### Do Not Expose Bibliography Keys in Body Text

Citation keys (`@key` / `[@key]`) **become meaningful to readers only after Pandoc / Quarto processes them**. Exposing the raw key string is an internal-implementation leak and must always be avoided.

**❌ Prohibited patterns**:

- `` `[@sahoo2024mdlm]` `` — backticks prevent citation processing and render the raw text (the most frequent bug)
- `` `@tbl-mapping` `` / `` `@fig-name` `` — cross-references in backticks do not resolve to “Table 1” / “Figure 1” and remain raw
- `The bibliography entry is registered as @key` — meta commentary about the internal implementation
- A table column or row labeled “citation key” / “Citation key” — not reader-facing information
- Prose such as `The paper represented by @key ...` — exposes the key name

**✅ Correct**:

- `MDLM [@sahoo2024mdlm] ...` — processed as a citation and converted to `[1]`, etc.
- `MDLM was introduced in @sahoo2024mdlm` — in-text citation in “Sahoo et al. (2024)” form
- `The paper remains unpublished [@ye2025dream7b]` — citing a blog with `[@key]` also lists it automatically in the bibliography

If an internal implementation note is needed, do not put it in body text; write it as a `%` comment inside `references.bib`.

#### False Citation Recognition of `@<number>` and `@<English-word>`

Pandoc's citation parser interprets `@<word>` as a citation key. Strings containing `@` in method labels and similar text can therefore be misinterpreted as citations:

- `NCV@3`, `Pass@8`, `Greedy@K` — `@3`, `@8`, and `@K` are parsed as citation keys
- `Gittins@cost`, `Gittins@linear` — `@cost` and `@linear` are parsed as citation keys
- The `quarto preview` console reports warnings such as `Citeproc: citation 3 not found`

**Fix patterns** (choose one):

- Escape: `NCV\@3` (use `\` to make `@` literal)
- Rename: `Gittins@cost` → `Gittins-cost` (change the notation)
- Backticks: `` `NCV@3` `` (treat it as code, which is appropriate for a method name)

If the paper's official notation is `NCV@k`, use escaping or backticks; renaming moves away from the original meaning. After Phase 7 linting passes, always run `quarto preview` and check console warnings.

#### Prevent Hallucinations

**Do not guess** bibliography-entry titles, authors, or arXiv IDs.

- **Do not confuse method names with paper titles.** For example, “Elastic-Cache” is a method name; the paper title is “Attention is All You Need for KV Cache in Diffusion LLMs”
- Obtain metadata directly from the arXiv abstract page, OpenReview, or the official GitHub repository
- When adding entries from a survey, compare against `main.bib` published by the survey authors and included in the arXiv e-print as the primary source. Fetching the survey e-print with `fetch_arxiv_figures.py` also obtains `main.bib`

See `references/citations.md` for details.

### Do Not Expose Filenames in Body Text

Do not write `.qmd` filenames such as `overview.qmd` or `guidance.qmd` directly in body prose. They are implementation details and reduce readability.

**❌ Prohibited patterns**:

- ``In this book's `overview.qmd` ...`` — exposes a filename in backticks
- `This is discussed in another chapter (guidance.qmd)` — shows a raw filename in parentheses
- `See survey-li2025.qmd for details` — uses a filename instead of a reader-facing link
- `Return to this chapter (survey-li2025)` / `(survey-li2025)` — placing a **file slug** without its extension in parentheses is also an implementation leak

**✅ Correct**:

- `See the book's [Overview](overview.qmd) ...` — visible text is the chapter name, and `.qmd` appears only in the link destination
- `This is discussed in [Guidance](guidance.qmd)` — a Markdown link displays the chapter name
- `See [Survey: Li et al. 2025](survey-li2025.qmd) for details`
- `Returning to this chapter, see @tbl-mapping` — “this chapter” is sufficient; there is no need to annotate the slug

The only exception is the **`{{< include _shared/X.qmd >}}` include shortcode**, because the filename is required by Quarto syntax. `lint_chapters.py` detects `[QMD_LEAK]` (exposed extension) and `[SLUG_LEAK]` (slug exposed in parentheses).

### Include (Shared Notation and Reusable Components)

Move notation definitions and shared components repeated across multiple chapters into `_shared/`, then include them from each chapter.

```markdown
### Notation

{{< include _shared/notation.qmd >}}
```

- Because filenames under `_shared/` begin with an underscore, Quarto automatically excludes them from rendering targets and treats them as include-only files
- The contents of an included file are expanded inline in the chapter that includes it
- Paths are relative to the including file

`{{< include >}}` is a Quarto shortcode. See `references/shortcodes.md` for other shortcodes such as `{{< video >}}` and `{{< pagebreak >}}`.

### Equations

Use LaTeX notation.

**Inline equation**: `$\frac{4}{\sqrt{n}}$`

**Display equation**:

```markdown
$$
\text{weight} = \begin{cases}
0.1 & \text{if video caption} \\
0.2 & \text{if pointing} \\
\frac{4}{\sqrt{n}} & \text{otherwise}
\end{cases}
$$
```

### Lists (Bullets)

**Always insert a blank line** before starting a list.

#### ❌ Prohibited: No Blank Line (Rendering Failure)

```markdown
**Dataset scale**:
- **104k video-level captions**
- **431k clip-level captions**
- Extremely detailed descriptions averaging **924 words/video**
```

In this form, the list does not render correctly.

#### ✅ Correct: Blank Line Present

```markdown
**Dataset scale**:

- **104k video-level captions**
- **431k clip-level captions**
- Extremely detailed descriptions averaging **924 words/video**
```

When a list follows a sentence:

```markdown
More detailed captions give the model these capabilities:

- **Spatiotemporal understanding**: accurately identify when, where, and what happened
- **Fine-grained visual recognition**: capture small objects, subtle actions, and attribute changes
- **Contextual understanding**: learn causal relationships and temporal dependencies among events
```

**Reason**: Markdown/Quarto does not recognize a list correctly when no blank line precedes it.

**Scope**:

- Unordered lists (`-`, `*`, `+`)
- Ordered lists (`1.`, `2.`, `3.`)
- Checklists (`- [ ]`, `- [x]`)

### Blockquotes inside List Items

When using a blockquote (`>`) inside a list item, insert a blank line before the blockquote as well.

#### ❌ Prohibited: No Blank Line before the Blockquote

```markdown
1. **Fast, scalable global deduplication**: a new tool at trillion-token scale
   > According to the authors, this is “the first method made practical at trillion-token scale.”
```

#### ✅ Correct: Blank Line before the Blockquote

```markdown
1. **Fast, scalable global deduplication**: a new tool at trillion-token scale

   > According to the authors, this is “the first method made practical at trillion-token scale.”
```

**Reason**: A blockquote inside a list item also fails to render correctly without a preceding blank line.

---

## 4. File-Naming Rules

### Directory Structure

```
{lang}/{book}/
├── _metadata.yml           # Specifies the sidebar ID
├── index.qmd               # Book landing page
├── overview.qmd            # Main document (big picture)
├── concept-a.qmd           # Supplementary document
├── concept-b.qmd           # Supplementary document
├── concept-c.qmd           # Supplementary document
└── images/                 # Image directory
    └── figure.png
```

### Naming Rules

- **Main document**: `overview.qmd` (fixed)
- **Supplementary documents**: use only a kebab-case topic name (do not add prefixes such as `01-`; the sidebar configuration controls chapter order)
- **Images**: place them in the `images/` directory
- **Extension**: use `.qmd` to take full advantage of Quarto features

---

## 5. Links

### Use Relative Paths

Use relative paths for links from the main document to supplementary documents and between supplementary documents.

**Correct example**:

```markdown
[→ 詳細:]{.detail-link} [Sliding Window Attention](sliding-window-attention.qmd)

**Related sections**:

- [Dense Video Captioning](dense-video-captioning.qmd)
- [Video Grounding](video-grounding.qmd)
```

### Standard Style for Detail Links

Standardize links that lead from the end of a section to a supplementary document on the **`[→ 詳細:]{.detail-link}` span form**. `styles.css` applies light styling to it.

```markdown
[→ 詳細:]{.detail-link} [Supplementary Document Title](concept-name.qmd)
```

Use the same form inside list items while preserving indentation:

```markdown
1. **Innovation A**: Description

   [→ 詳細:]{.detail-link} [Supplement A](concept-a.qmd)
```

#### ❌ Deprecated: Blockquote Detail Links

```markdown
> 詳細: [Supplement A](concept-a.qmd)
```

The old `> 詳細:` blockquote style is deprecated. When found in an existing file, standardize it to `[→ 詳細:]{.detail-link}`.

### ❌ Prohibited: References by Chapter Number (`第 N 章` / `Chapter N`)

When referring to another chapter, use the **chapter name + qmd link**, not a chapter number.

```markdown
# ✅ Correct
The prefix consensus discussed in [Self-Consistency and Weighted Majority Voting](self-consistency.qmd) ...

# ❌ Prohibited
The prefix consensus discussed in Chapter 4 ...
The prefix consensus discussed in Chapter 4 ([Self-Consistency and Weighted Majority Voting](self-consistency.qmd)) ...
```

Reason: filenames have no numeric prefixes and the sidebar controls chapter order, so simply rearranging the sidebar would make body references false. Each chapter is also intended to be read independently, so numbered references that imply linear reading do not fit the premise.

For a self-reference within the same Japanese chapter, use **`本章`** (“this chapter”). The same applies to table captions and section titles (Japanese example: `: 本章で扱った主要論文 {#tbl-...}`).

### ❌ Prohibited: Trailing Navigation Blockquotes

Do **not** put navigation blockquotes such as `> 次章:` / `> 関連文書:` / `> 概要に戻る:` at the end of a chapter. The sidebar provides chapter navigation, so explicit next/previous links are redundant under the minimal-chrome policy.

```markdown
# ❌ Do not write this
> 次章: [Weighted Voting](weighted-voting.qmd)
> 関連文書: [概要に戻る](overview.qmd)
> 概要に戻る: [Overview](overview.qmd)
```

### ❌ Prohibited: Links to Files That Do Not Exist

**Invalid example**:

```markdown
- [Nonexistent Document](nonexistent.qmd)  ← this file has not been created
```

Link **only to files that actually exist**. If uncertain, inspect the supplementary-document list defined in the main document (`overview.qmd`).

### Extensions

- Always include the `.qmd` extension
- Use `.qmd`, not `.md`

---

## 6. Language Selection

### Body Text

- For `ja/`: write in Japanese
  - **Style**: use **である調** (plain assertive style)
  - Examples: `〜である`, `〜する`, `〜となる`
  - Do not use **ですます調** (polite style)
- For `en/`: write in English

### Expand Technical Terms and Abbreviations at First Use (Important)

**Expand abbreviations and technical terms at first use in every chapter.**

**Format**:

- Japanese (`ja/`, `private/`): `日本語訳（English full form, ACRONYM）`
- English (`en/`): `English full form (ACRONYM)`

```markdown
# ja
強化学習（Reinforcement Learning, RL）を使用して...

# en
Reinforcement Learning (RL) is used to...
```

**Core rules**:

- **Each chapter is independent**: because every chapter may be read on its own, **treat the same abbreviation as a first use in each chapter** and expand it again even if another chapter already did
- **Expand abbreviations appearing in H1 in the first body paragraph**: for a chapter title such as `# LLaDA: MDLM 定式化を 8B にスケール`, do not add a parenthetical expansion to H1 itself; expand it in the first body paragraph as `MDLM（Masked Diffusion Language Model）`
- **Use the abbreviation alone from its second appearance in the same chapter**: one expansion per chapter is sufficient
- **Common English abbreviations such as PDF / OCR / API / GPU / CPU are allowed**: abbreviations generally known by readers need not be expanded

**Common expansion targets** in ML books:

LLM / VLM / MLLM / DLLM / AR / RL / SFT / DPO / GRPO / PPO / RLHF / RLVR / MDLM / D3PM / SEDD / DDPM / DDIM / LDM / DSM / SDE / ODE / VAE / GAN / DiT / ViT / KV / RoPE / NTK / VDM / SNR / KL / ELBO / VLB / NFE / FID / FLOP / SOTA / CoT / MCTS / MDP / DAG / MLE / MAP / CNN / RNN / MLP / ReLU / SVD / EVD / NLL / MSE / EM / GMM / GP / RBF / DNN / BNN / MoE / PRM.

### Code and Equations

**Write them in English** (international convention).

### Do Not Use Em Dashes or En Dashes in Japanese Prose

Do not use em dashes (`—`, U+2014) or en dashes (`–`, U+2013) in Japanese prose.

- **Em dash** (`—`): subagents tend to overproduce it as a heading subtitle separator, an aside in prose, or a description separator in list syntax. Remove every occurrence
  - Heading: `## X — Y` → `## X: Y` (ASCII colon)
  - Prose aside: `AAA——BBB——CCC` → split the sentence at a Japanese period, or use Japanese parentheses: `AAA（BBB）CCC`
  - List: `**[X]** [@key] — Description` → `**[X]** [@key]: Description`
  - Empty table cell: `| — |` → `| - |` (ASCII hyphen)
- **En dash** (`–`): English typographic conventions may permit it for numeric ranges (`2025–2026`, `5–24%`, `Bucket A–B`). Decide the policy at the beginning of each book and apply it consistently

Prior example: a chapter-writing subagent tried to make subtitle structure easier to read by adding em dashes to headings, creating 20–30 occurrences that required a bulk fix with `sed` in Phase 7. Explicitly stating “no em dashes” in the subagent prompt from the start prevents this.

### Terminology Consistency: Neural-Network Terms

Standardize Japanese neural-network terminology on **`ニューラルネット`**:

- ❌ `ネット` / `ネットワーク` / `ニューラルネットワーク` (do not mix these across subagents)
- ✅ `ニューラルネット`
- Expansion at first use: `ニューラルネット（Neural Network, NN）`
- Also change module names such as `入力ネット` to `入力ニューラルネット`
- Exception: preserve wording in quotations when respecting the source, such as `人工ニューラルネットワーク`

### Terminology Consistency: Large-Scale vs. Huge

For Japanese descriptions of LLM scale, **`大規模`** is standard:

- ❌ `巨大言語モデル` / `巨大 LLM` / `巨大モデル` / `巨大データ` / `巨大事前学習`
- ✅ `大規模言語モデル` / `大規模 LLM` / `大規模モデル` / `大規模データ` / `大規模事前学習`
- Use `巨大` only in literary rhetoric (for example, `莫大な thinking budget` or `莫大な計算量`)

### Terminology Consistency: Small-Scale / Large-Scale (Model-Size Adjectives)

- ❌ `小モデル` / `大モデル` (colloquial abbreviations)
- ✅ `小規模モデル` / `大規模モデル`
- Express comparative nuance as `より小さなモデル` (“smaller model”) and `より大きなモデル` (“larger model”)

### Localize Casual English Terms into Japanese

Do not carry casual industry English directly into Japanese technical documents:

- **bucket** → `グループ`, `カテゴリ`, or `類型`
- **ballpark** → `概算` or `目安`
- **flavor** / **flavor of** → `種類`, `バリアント`, or `版`
- **ish** (for example, “scaling-ish”) → `〜的` or `〜系`

Prior example: an author categorized material as “Bucket A” and “Bucket B” in a Deep Research note. Those labels carried into the book and later required a global replacement with `グループ A` and `グループ B`. Localizing them from the beginning would have avoided the rework.

### Avoid Fancy or Metaphorical Expressions

Subagents favor metaphorical headings and phrases in an effort to sound memorable. For technical writing, choose direct terms:

| Metaphorical (avoid) | Direct (recommended) |
|----------------------|----------------------|
| `地図` / landscape / `見取り図` | `分類` / `整理` / `概要` |
| `俯瞰` / `眺める` | `整理する` / `全体像` |
| `橋` / `橋渡し` | `接続` / `対応` |
| `群雄割拠` / `百花繚乱` | `並走` / `並存` |

Eliminate metaphors especially from frequently read locations such as H1, pagetitle, and sidebar text.

---

## 7. Tables and Figures

### Creating Tables

Use Markdown pipe tables.

```markdown
| Model | Parameters | Performance |
|-------|------------|-------------|
| Molmo2-4B | 4B | 85.5 |
| Molmo2-8B | 8B | 86.2 |
```

Complex tables may use list tables as well; see `references/tables.md`.

### Inserting Figures

```markdown
![Figure caption](images/figure.png)
```

Always place images in the `images/` directory.

### Custom SVG Figures

Use a custom SVG only when it explains a relationship or boundary that is not available in a primary-source figure and is not clearer as a table. Keep it self-contained and portable.

- Give colors stable semantic roles, such as fixed/runtime, editable/candidate, optimizer action, failure/rejection, and accepted/success. Do not recolor the same role between panels.
- Separate label styles by function: role names in bold sans-serif, mathematical notation in a math typeface, and state descriptions in smaller sans-serif text.
- Avoid `<foreignObject>` for text layout. Use explicit `<text>` and `<tspan>` positions so rendering does not depend on browser HTML support inside SVG.
- An SVG loaded through an HTML `<img>` does **not** reliably inherit the surrounding page's fonts. Do not assume that naming the CSS font is enough.
- When mathematical labels must match the rendered Quarto body, inspect the actual MathJax font in the browser. If external font loading inside the SVG is unreliable, subset only the required glyphs, embed the WOFF2 as a data URL in the SVG, and preserve the font's license notice.
- Parse the final SVG as XML before rendering. Literal angle-bracket examples inside XML comments can make an otherwise valid-looking SVG fail to parse.
- After Quarto rendering, inspect the SVG at the actual article width rather than only in a standalone viewer. Check text wrapping, clipping, overlap, baselines, arrowheads, `viewBox`, aspect ratio, panel alignment, and whether the figure is still legible at its displayed size.

If SVG markers or external resources render inconsistently in the target browser, replace them with explicit self-contained geometry rather than adding browser-specific workarounds.

---

## 8. Mermaid Diagrams

Create flowcharts, sequence diagrams, and relationship diagrams with Mermaid. Quarto renders them automatically, so no image file is needed.

**Flowchart**:

````markdown
```{mermaid}
%%| label: fig-pipeline
%%| fig-cap: "Processing pipeline"

flowchart LR
    A[Input] --> B[Process] --> C[Output]
```
````

**Direction**: `LR` (left → right), `TD` (top → bottom), `RL`, `BT`

**Rules for text inside nodes**:

- **Line breaks**: use `<br/>` (`\n` is not allowed)
- **Bold**: `<b>...</b>` is available
- **HTML escaping is required**:
  - `&` → `&amp;`
  - `<` → `&lt;` (unless it is an HTML tag)
  - `>` → `&gt;` (unless it is an HTML tag)
- Enclose node labels in `["..."]` to enable HTML syntax

```
A["<b>Title</b><br/>Line 1 &amp; Line 2"]
```

**Main diagram types**:

- `flowchart`: flowcharts and decision branches
- `sequenceDiagram`: sequence diagrams (API calls, protocols, etc.)
- `stateDiagram-v2`: state-transition diagrams
- `classDiagram`: class and relationship diagrams

See `references/diagrams.md` for details.

---

## 9. Checklist

When creating a supplementary document, confirm the following:

- [ ] For a ja chapter, H1 ≡ pagetitle ≡ sidebar text match exactly (do not use bilingual `English: 日本語`)
- [ ] For an en chapter, pagetitle ≡ sidebar text (H1 may freely include a subtitle)
- [ ] English text uses Chicago-style Title Case (including capitalization of the root after a hyphen)
- [ ] When both ja/en editions exist and the ja H1 is English-only, the main portions of both H1s match exactly
- [ ] Japanese (`ja/`, `private/`) uses **である調**
- [ ] **Abbreviations and technical terms are expanded at first use in every chapter** (`日本語訳（English, ACRONYM）` form; each chapter is independent)
- [ ] **Abbreviations present in H1 are expanded in the first body paragraph** (do not put the parenthetical expansion in H1 itself)
- [ ] Structured data uses Quarto tables; flow diagrams use Mermaid
- [ ] **A blank line appears before every list** (unordered, ordered, and checklist)
- [ ] **A blank line also appears before any blockquote inside a list item**
- [ ] Callouts open and close correctly (matching `:::`)
- [ ] Detail links use `[→ 詳細:]{.detail-link}` (the `> 詳細:` blockquote is deprecated)
- [ ] No trailing navigation blockquotes (`> 次章:` / `> 関連文書:`, etc.); leave navigation to the sidebar
- [ ] Chapters requiring citations do not add a `## 参考文献` heading or `::: {#refs}` block (Pandoc inserts the list automatically)
- [ ] Links point only to files that exist
- [ ] Extensions are `.qmd`
- [ ] Images are in the `images/` directory
- [ ] Equations use LaTeX syntax
- [ ] The body uses the appropriate language (Japanese under `ja/`, English under `en/`)
- [ ] Citations use `[@key]` syntax (only when a `.bib` file exists; otherwise use an ordinary link)
- [ ] No undefined citation keys are used (only entries present in `references.bib`)
- [ ] Theorems and lemmas use theorem environments such as `::: {#thm-...}`

---

## 10. Reference Resources

For more detailed Quarto functionality, see these reference files:

- `references/callouts.md`: detailed callout options
- `references/cross-references.md`: cross-reference system
- `references/figures.md`: figure insertion and sizing
- `references/tables.md`: table creation and styling
- `references/diagrams.md`: Mermaid and Graphviz diagrams
- `references/citations.md`: BibTeX citations and reference lists
- `references/divs-and-spans.md`: theorem-family environments and general `::: {.class}` syntax
- `references/shortcodes.md`: shortcodes such as `{{< include >}}`
- `references/layout.md`: page width, multiple columns, and margin placement
- `references/conditional-content.md`: format-specific display for HTML/PDF and other outputs
- `references/yaml-front-matter.md`: YAML front-matter settings
- `references/markdown-linting.md`: Markdown lint rules

---

**Important**: Following these rules produces consistent, high-quality technical documents. If anything is unclear, consult existing supplementary documents such as `ja/dllm/` and `ja/olmo-3/`.
