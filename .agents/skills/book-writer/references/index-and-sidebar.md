# Phase 6 Reference: Details for index.qmd and _quarto-public.yml

In Phase 6, create the book landing page, `index.qmd`, and register it in the site-wide sidebar. These details have been separated from `SKILL.md`.

## 6.1: Create index.qmd

### Division of Responsibilities: index.qmd vs overview.qmd

- Before drafting, inspect two or three existing `index.qmd` files from the same repository. Preserve the site's landing-page pattern instead of designing the entry from scratch.
- **index.qmd = the book's "cover"**: what the book is about, what its sources are, and when it was written. A reader arriving from a listing should be able to decide within five seconds whether the book is relevant. **Keep it minimal.**
- **overview.qmd = an optional "big picture" chapter**: use it only when the main questions, structure, and importance need a substantial treatment that would overload the landing page.

The default repository pattern is front matter plus one or two lead paragraphs. Avoid bibliography citations such as `[@key]`; a claim that needs evidence belongs in `overview.qmd`. Direct links serve a different purpose and are allowed: after the introduction, one compact line may link to the primary paper, code, demo, dataset, or official project page. For a compact book with no overview, a brief problem statement may remain in the index only when existing entries use that pattern. For a multi-part or survey book, move problem formulation, scope, notation, and the unit of comparison into `overview.qmd`. Do not add a “Structure of This Book” section, a chapter list, or a standalone “Read the overview” link; the sidebar already provides that navigation.

### Write a Strong Lead Without Turning It into Marketing

Minimal does not mean generic. The lead should make the subject worth reading before it summarizes the book.

- Open with a concrete capability, tension, consequence, or unresolved question that the intended reader can recognize. Prefer specific choices and outcomes over a generic sentence such as “This book surveys X.”
- Establish why the subject matters before introducing unfamiliar terminology. Define the central object in the first paragraph, after showing what is distinctive about it or what changes when it is used differently.
- Use the second paragraph to frame the central question or reader payoff and connect the scope through one organizing idea. For optimization or evaluation books, also state how genuine progress will be distinguished from apparent gains. Do not replace this arc with a chapter-topic list.
- Favor one precise contrast and varied sentence lengths. Avoid marketing adjectives, unsupported superlatives, false either-or claims, and quantitative claims that would require a citation.
- Source introductions may be used to understand motivation and terminology, but draft the landing page independently. Do not reuse their sentence structure, metaphor, example sequence, or distinctive phrasing.
- For Japanese, compose directly in natural **de aru** style rather than translating an English lead literally. A restrained question can create momentum, but the surrounding sentences should remain concrete and technically precise.

### Minimal Template

```yaml
---
title: "Book Title"
description: "One-line book description"
date: "YYYY-MM-DD"
date-modified: last-modified
author:
  name: "Author Name"
  url: "https://example.com"
categories: [Category 1, Category 2]
image: "images/cover-image.png"
toc: false
---

A brief description of the model or technique (one or two paragraphs explaining what the book covers and why it matters)

**Paper**: [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)

**Code**: URL (if available)

**Demo**: URL (if available)
```

Even for a multi-paper survey, do not put a paper-list table in the index. The sidebar already conveys chapter order and the opening of each chapter provides paper information; do not duplicate those functions in the index.

### Content That Usually Does Not Belong in index.qmd

Do **not** put the following in `index.qmd` unless the compact-book exception above requires a brief version:

- A bullet list of main contributions or features.
- A list of model variants or model sizes.
- Benchmark or performance-evaluation tables.
- Training costs or compute resources.
- A list of open artifacts.
- A list of major topics equivalent to chapter titles, because the sidebar already provides it.
- A literal `## 目次` ("Table of Contents") section, because it duplicates the sidebar completely.
- A “Structure of This Book” section or manual link to the first chapter, because it creates a second chapter map beside the sidebar.
- A paper-list table, even for a multi-paper survey, because the sidebar and chapter openings provide this information.
- Bibliography citations used to support technical claims. Move both the claim and citation to `overview.qmd`; do not confuse this with a compact direct link to the primary artifact.

For a cover-only index, do not place any `## ...` heading in the index. A compact book that combines its overview with the index may use a small number of functional headings. In either case, include `toc: false` so the right-hand table-of-contents sidebar stays hidden.

### Field Descriptions

- **title**: the book title.
  - **English only**, whether it is a model, method, or book name. Do not add a Japanese subtitle.
  - For an existing book, **respect the original title**, including any subtitle after a colon; for example, `Probabilistic Machine Learning: An Introduction`.
  - Keep it **identical across Japanese and English**.
  - Examples: `Olmo 3`, `Molmo2`, `Diffusion Language Models`, `CoT Verification`.
- **description**: a one-line description.
  - In Japanese, prefer a compact noun phrase for a neutral summary. An active verb is also allowed when it states the reader benefit or distinctive angle more clearly than a nominalized phrase.
  - Do not add a final period.
  - Do not use a colon. Express scope or qualification in parentheses.
  - Make the subject and distinctive angle clear in one line. Do not merely repeat the title or use an empty phrase such as “a systematic overview.”
  - Target length: **20–35 Japanese characters** for `ja`, **60–85 characters** for `en`.
  - Japanese example: `拡散言語モデル（DLLM）の主要文献を体系的に整理` ("Systematic organization of the key literature on diffusion language models (DLLMs)").
  - Japanese example: `1ステップ生成モデルの最前線（Flow Matching から Drifting Models まで）` ("The frontier of one-step generative models, from Flow Matching to Drifting Models").
  - English example: `Fully open language and reasoning models (7B/32B)`.
- **date**: the creation date or paper publication date in `YYYY-MM-DD` format.
  - **Important**: determine the current date by running `date +%Y-%m-%d` with the Bash tool.
  - Always use the command output rather than typing the year manually, to prevent typographical errors.
- **date-modified**: set to `last-modified`, which is resolved automatically from Git history. This is required to show "last updated" on the book's index page.
- **author**: copy the canonical author object from an existing public book index or project metadata. Do not hard-code a person's identity in a reusable example.
- **categories**: specify **at most two** appropriate categories as a list.
  - **Important**: first inspect existing categories to avoid spelling variants:
    ```bash
    python .agents/skills/book-writer/scripts/list_categories.py .
    ```
  - Prefer an existing category; add a new one only when necessary. Avoid a one-entry category unless it is likely to be reused.
  - Treat categories as a small browsing taxonomy, not as exhaustive keywords. Prefer broad, reusable topics; omit redundant parent/child labels and details already clear from the title.
  - Use singular forms for countable topic labels, such as `AI Agent` and `Generative Model`; do not mix them with `AI Agents` or `Generative Models`.
  - Examples: `[LLM, Reasoning]`, `[LLM, AI Agent]`, `[Deep Learning, Generative Model]`.
- **image**: path to the cover image within the `images/` directory.
- **toc**: always `false`. A book's `index.qmd` is a landing page, so this is required to suppress the right-hand table-of-contents sidebar.

## 6.2: Configure the Sidebar (`_quarto-public.yml`)

Add a new public book sidebar to `_quarto-public.yml`. Register every chapter in the sidebar. Because `index.qmd` contains no table of contents, the sidebar is the only entry point for chapter navigation.

```yaml
sidebar:
  - id: new-book-ja
    title: "ML Notes"
    style: "docked"
    collapse-level: 3
    contents:
      - section: "New Book Title"
        href: ja/new-book/index.qmd
        contents:
          - text: "Overview"
            href: ja/new-book/overview.qmd
          - text: "Concept A"
            href: ja/new-book/concept-a.qmd
          - text: "Concept B"
            href: ja/new-book/concept-b.qmd
          # Add the remaining supplementary documents in the same way
```

If an English edition exists, add a separate sidebar in the same way with an `-en` suffix:

```yaml
  - id: new-book-en
    title: "ML Notes"
    style: "docked"
    collapse-level: 3
    contents:
      - section: "New Book Title"
        href: en/new-book/index.qmd
        contents:
          - text: "Overview"
            href: en/new-book/overview.qmd
          # ...
```

### Notes

- `id` is a unique identifier. It must match `sidebar` in `_metadata.yml` and, for a public book, end in `-ja` or `-en`.
- Standardize `title` as **exactly `"ML Notes"`**. The gray area at the top of the sidebar serves as the site name; the book title appears in the `section:` below.
- `collapse-level: 3` expands all sections by default.
- Use `section:` plus `href:` to make `index.qmd`, the landing page, a collapsible parent.
- Always write `href` as a relative path.
- Register every chapter, including the overview and supplementary documents. Because `index.qmd` has no table of contents, the sidebar is the only navigation entry point.
- For a book with many chapters, nest `section:` entries by Part or Section; see `murphy1` and `olmo-3`.
- Use existing sidebar entries such as `olmo-3` and `molmo2` as references.
- Add a private book to `private/_quarto-private.yml`.

### Renaming a Book or Chapter Slug

A slug rename is a cross-file operation. Before editing, search for the old directory name, filename, `.qmd` path, and generated `.html` path. Then update and verify all applicable locations:

1. Rename the source directory or chapter file.
2. Update every sidebar `href` in `_quarto-public.yml` or `_quarto-private.yml`.
3. If the book directory or sidebar ID changes, update `sidebar:` in the book's `_metadata.yml` and keep the sidebar `id` synchronized.
4. Update relative links in QMD files and any public listings.
5. Remove stale generated output under `_site/` unless an explicit redirect policy requires it.
6. Render the book once after the rename.
7. Verify that the new index and chapter URLs return success, the old URL follows the chosen 404/redirect policy, and previous/next navigation points to the new path.

Review titles and slugs together, and audit the complete Part or book rather than correcting only the chapter that drew attention. Do not keep a weak or stale slug merely to avoid a rename. Prefer a one-to-three-word functional noun phrase that matches the chapter's core concept. Bilingual editions use the same relative slug under `ja/` and `en/`; translate the visible title, not the filename.

### Naming Nested `section:` Entries: Use Functional Terms

When a book has at least eight chapters and the sidebar nests them by Part or Section, use a **compact functional label that describes the chapters' role**. If the sections are numbered Parts, prefer a Roman numeral plus the label, such as `I 基礎`, rather than the width-consuming `Part I: 基礎` or `第 I 部: 基礎`.

Past example: the first edition of `recursive-reasoning` used the Japanese labels `系譜と地図` ("Lineage and Map") and `比較と動向` ("Comparison and Trends") and was criticized as vague. Those labels merely joined chapter-title concepts with "and," so the section's contents were not inferable from its name. The `reliable-reasoning` labels `訓練側の信号` ("Training-Side Signals"), `推論側の信号` ("Inference-Side Signals"), and `構造的アプローチ` ("Structural Approaches") are the model for functional classification.

| Recommended (functional term) | Not recommended (abstract enumeration) |
|-------------------------------|-----------------------------------------|
| `中心` / `主役` / `本論` (core / focus / main subject) | `系譜と地図` (lineage and map) |
| `背景` / `前史` (background / prehistory) | `比較と動向` (comparison and trends) |
| `評価` / `対比` / `比較` (evaluation / contrast / comparison) | `位置付けと整理` (positioning and organization) |
| `訓練側の信号` (training-side signals) | `学習関連の話題` (learning-related topics) |
| `推論側の信号` (inference-side signals) | `推論まわり` (things around inference) |
| `構造的アプローチ` (structural approaches) | `アーキテクチャ系` (architecture-ish) |
| `応用` / `派生` / `展開` (applications / derivatives / extensions) | `その他` (other) |
| `入門` / `基礎` (introduction / foundations) | `前提知識` (prerequisite knowledge) |

Avoid these abstract Japanese labels: **`文脈`** ("context," which conflicts semantically with LLM context), **`位置付け`** ("positioning," too abstract), **`諸論点`** ("various issues," which does not identify the issues), and **`その他`** ("other," which states no function).

See [style-consistency.md](style-consistency.md) for details.

### Language Rules for `text:`

- **English sidebar (`-en`)**: keep text in English.
- **Japanese sidebar (`-ja`) and private sidebar**: localize text toward Japanese, except for the following items, which remain in English:
  - Model and dataset names, such as LLaDA, MDLM, Dolma 3, olmOCR, and Dolci.
  - Established method names and abbreviations, such as MaskGIT, MeanFlow, NTK, RG Flow, GRPO, VAE, GANs, MCMC, GLM, and BD3-LMs.
  - Task names without an established Japanese translation, such as Dense Video Captioning, Video Grounding, and Vision-Language Connector.
- Translate abstract or descriptive titles into Japanese:
  - `Overview` → `概要` ("Overview").
  - `Open Problems` → `未解決問題` ("Open Problems").
  - `Part I: Foundations` → `I 基礎` ("Part I: Foundations").
  - `Deduplication` → `重複除去` ("Deduplication") and `Data Mixing` → `データ混合` ("Data Mixing").
- Match the tone of existing sidebar groups in `_quarto-public.yml` / `_quarto-private.yml`.
- **Japanese sidebar text must match the chapter's Japanese H1 exactly**, as described below. When adding a chapter, use the same string for H1 and sidebar text.

### Chapter-Title Synchronization Rules

- **Japanese**: H1 ≡ `pagetitle` ≡ sidebar text, exactly. Do not use the bilingual `# English: 日本語` format, where `日本語` means "Japanese"; it was retired because repeating the same words is redundant.
- **English**: H1 may be fully descriptive and can include a subtitle. Only `pagetitle` ≡ sidebar text is mandatory; H1 does not have to match `pagetitle`.
- **Cross-language**: require Japanese H1 to match the main portion of the English H1 before the colon only when the Japanese H1 itself is entirely English. If the Japanese H1 is localized into Japanese, the automatic check skips it and a human must verify semantic alignment.
- In the overview, the visible text of `[→ 詳細:]` / `[→ Detail:]` links must equal the target chapter's sidebar text. The first label is the literal Japanese "Details" label.
- Visible text in inter-chapter links within prose must equal the target chapter's sidebar text.

Use **Chicago-style Title Case** for English, including capitalization of roots after hyphens: `Long-Context`, `Test-Time`, `Self-Consistency`, and `Post-Training`.

`lint_chapters.py` verifies these rules automatically with `[TITLE_SYNC]` / `[TITLE_XLANG]`:

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py ja/{book}
python3 .agents/skills/book-writer/scripts/lint_chapters.py en/{book}
```

When `--sidebar` is omitted, the script automatically finds `_quarto-public.yml` for a public book or `private/_quarto-private.yml` for a private book.
