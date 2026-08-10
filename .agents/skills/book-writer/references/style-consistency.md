# Style Consistency Reference

Generating chapters with parallel subagents tends to produce inconsistent style. Use this checklist to maintain consistency within a book and with existing books.

Past example, observed while creating the `recursive-reasoning` book: subagents spontaneously added their own style elements. Only five of seven chapters had an italic lede; the Japanese terms `ネット`, `ネットワーク`, and `ニューラルネット` all appeared for "neural net"; headings connected subtitles with em dashes; a Mermaid diagram claimed to have two axes but actually had one; and casual English such as `bucket` leaked into technical prose. Each issue is small, but together they reduce the quality of the entire book. Prevent them by **enumerating the rules explicitly** in `SKILL.md` and the subagent prompt.

## Current Style Baseline from Existing Books

Before creating a new book, choose the closest existing book by field from `ja/reliable-reasoning/`, `ja/dllm/`, `ja/one-step-generation/`, `ja/olmo-3/`, or `ja/molmo2/`. Compare against it for every item below. The goal is not to write according to personal taste but to preserve site-wide consistency.

### Do Not Put an Italic Lede Directly Under H1

**Rule**: start the content immediately after H1 (`# Chapter Title`) with a **normal prose paragraph**. Do **not** insert a one-line abstract styled as `*an italic lede*`.

Past example: refine agents often decide on their own that an abstract-like summary would be useful. Because each subagent decides differently, the style becomes inconsistent even within one book. Existing books such as `reliable-reasoning` and `dllm` never use italic ledes, so the consistent policy is to omit them.

```markdown
# Chapter X Title

*Italic lede ← prohibited*

Body paragraph...
```

```markdown
# Chapter X Title

Body paragraph... ← standard
```

### Do Not Connect Heading Subtitles with an Em Dash

**Rule**: do not use `## X — Y`, an em dash plus subtitle. If the subtitle is worth keeping, use `## X: Y`, an ASCII colon followed by one space. If it is redundant, remove it and use only `## X`.

Past example: subagents tend to write headings such as `## Current Benchmark Status — Three Generations: 1, 2, and 3`. Although intended to improve readability, this makes heading style inconsistent across the book.

### Name Sidebar Sections with Functional Terms

**Rule**: use a **compact Japanese functional label that describes the chapters' role** as a sidebar section title. Japanese examples include `中心` ("Core"), `背景` ("Background"), `評価` ("Evaluation"), `訓練側` ("Training Side"), `推論側` ("Inference Side"), and `構造的アプローチ` ("Structural Approaches"). For numbered Parts, omit the literal word `Part` and the colon: prefer `I 基礎` over `Part I: 基礎`. Do **not** use an abstract expression that merely joins chapter-title concepts with the Japanese conjunction `と` ("and"), such as `系譜と地図` ("Lineage and Map"), `比較と動向` ("Comparison and Trends"), or `位置付けと整理` ("Positioning and Organization").

Past example: the first edition of `recursive-reasoning` used `系譜と地図` and `比較と動向` and was criticized as vague. Use `reliable-reasoning` as the model: it classifies chapters functionally with `訓練側の信号` ("Training-Side Signals"), `推論側の信号` ("Inference-Side Signals"), and `構造的アプローチ` ("Structural Approaches").

### Prohibited Sidebar Section Terms

Avoid these abstract Japanese labels:

- **`文脈`** ("context") — likely to conflict semantically with LLM context.
- **`位置付け`** ("positioning") — too abstract.
- **`諸論点`** ("various issues") — does not identify which issues.
- **`その他`** ("other") — states no function.

Recommended Japanese terms include:

- **`中心`** / **`主役`** / **`本論`** (core / focus / main subject).
- **`背景`** / **`前史`** (background / prehistory).
- **`評価`** / **`対比`** / **`比較`** (evaluation / contrast / comparison).
- **`応用`** / **`派生`** / **`展開`** (applications / derivatives / extensions).
- **`入門`** / **`基礎`** (introduction / foundations).

## Terminology Standardization Rules

Parallel subagents choose translations independently, so one concept can acquire three or four forms if unconstrained. **Enumerate the exact forms in the subagent prompt** and require them.

### Introduce a Japanese Term Once per Chapter, Then Keep It Japanese

Treat every chapter as independently readable and do not alternate between an English technical term and its Japanese translation:

1. Before parallel writing, choose canonical Japanese forms and include them in every subagent prompt.
2. At first body use in each chapter, write `日本語（English）`, or `日本語（English full form, ACRONYM）` for an abbreviation.
3. Thereafter use the Japanese form consistently. For a standard abbreviation, use either it or the Japanese form consistently; do not return to the raw English full form.
4. In Phase 7, audit raw English prose terms and first-use definitions chapter by chapter.

For example, use `最適化器（optimizer）` once and `最適化器` thereafter. Apply the same rule to `評価器（evaluator）`, `現行版（incumbent）`, `更新候補（candidate）`, `編集面（edit surface）`, and `成果物（artifact）`. Method and product names, API identifiers, code, mathematical variables, citation keys, link destinations, and the common abbreviations exempted by `SKILL.md` are outside this rule.

### Neural-Network Terminology in Japanese

- **Standardize every occurrence as `ニューラルネット`** ("neural net"). The variants `ネット` ("net"), `ネットワーク` ("network"), and `ニューラルネットワーク` ("neural network") otherwise tend to coexist.
- First-use expansion: `ニューラルネット（Neural Network, NN）`.
- Exception: preserve wording in a quotation when fidelity to the source matters, such as `人工ニューラルネットワーク` ("artificial neural network").
- Module names such as `入力ネット` ("input net") should also become `入力ニューラルネット` ("input neural net").

### Teacher and Student in Knowledge Distillation

- Translate **`student` as `生徒`**, meaning "pupil," **not `学生`**, meaning "university student."
- Translate **`teacher` as `教師`**.
- Examples: `生徒モデル` ("student model"), `教師の CoT を生徒の hidden 層に蒸留` ("distill the teacher's CoT into the student's hidden layers"), and `教師-生徒蒸留` ("teacher-student distillation").
- Past example: subagents tend to translate literally with `学生モデル` or write `学生は通常 forward を 1 回流す` ("the student usually runs one forward pass"). Existing repository usage, such as `ja/dllm/inference-acceleration.qmd` and its phrase `教師-生徒で diffusion step を圧縮する` ("compress diffusion steps with teacher-student distillation"), consistently uses `生徒`; follow it.

### Describing LLM Scale in Japanese

- Standardize on **`大規模言語モデル`** ("large language model"), **`大規模 LLM`** ("large-scale LLM"), or **`大規模モデル`** ("large-scale model"). Do not use `巨大` ("giant" or "huge").
- `巨大` is acceptable only in a quantitative metaphor unrelated to the LLM itself, such as `莫大な thinking budget` ("an enormous thinking budget"), preferably with wording appropriate to that quantity.
- Past example: subagents tend to write `巨大言語モデル` ("huge language model"); the standard term uses `大規模` ("large-scale").

### Adjectives for Model Size in Japanese

- Standardize on **`小規模モデル`** ("small-scale model") and **`大規模モデル`** ("large-scale model"). Avoid the colloquial abbreviations `小モデル` and `大モデル`.
- Past example: subagents tend to write phrases such as `小モデルアプローチ` ("small-model approach"), `小モデルが Frontier LLM を上回る` ("a small model outperforms a frontier LLM"), or `大モデル少数サンプリング` ("few-sample generation with a large model"). In technical writing, `小規模` and `大規模` are the standard forms.
- To preserve a comparative nuance, use `より小さなモデル` ("smaller models") or `より大きなモデル` ("larger models").

### Distinguishing Test-Time/Inference Terms in ml-notes

- Reserve the Japanese term **`推論`** for inference, meaning a model forward pass.
- Leave reasoning, meaning thought or logical development, in roman letters as **`reasoning`**.
- Keep related terms in English: `reasoning model`, `latent reasoning`, `reasoning trace`, and `recursive reasoning`.

### Casual English Terms Such as bucket / ballpark / flavor

**Rule**: avoid English industry slang such as `bucket`, `ballpark`, `flavor`, `flavor of`, and `ish` in Japanese technical writing.

Preferred Japanese alternatives:

- **`bucket`** → `グループ`, `カテゴリ`, `類型`, or `系統` (group / category / type / family).
- **`ballpark`** → `概算` or `目安` (rough estimate / guideline).
- **`flavor`** → `種類`, `バリアント`, or `版` (type / variant / version).

Past example: a Deep Research note created original categories named "Bucket A" and "Bucket B." They carried into the book and later required a bulk replacement with `グループ A` and `グループ B` ("Group A" and "Group B"). Translating them from the beginning would have avoided the cleanup.

## Be Wary of Fancy or Metaphorical Language

Subagents tend to favor **metaphorical headings** in an attempt to make a book memorable. Avoid them in technical writing.

### Metaphors to Avoid

- `地図`, `landscape`, `俯瞰`, `見取り図`, and `地形` (map / landscape / bird's-eye view / sketch map / terrain) → use `分類`, `整理`, `概要`, or `全体像` (classification / organization / overview / big picture).
- `目線`, `視座`, and `眺める` (gaze / vantage point / look at) → use `観点`, `視点`, or `整理する` (perspective / viewpoint / organize).
- `橋`, `橋渡し`, and `架け橋` (bridge / bridging) → use `接続`, `対応`, or `関係` (connection / correspondence / relationship).
- `群雄割拠` and `百花繚乱` (rival powers / profusion of blossoms) → use `並走` or `並存` (developing in parallel / coexistence).

### Apply This to H1, pagetitle, and Sidebar Text

Remove metaphors especially from **high-frequency locations** such as H1 and sidebar text.

| Bad (metaphorical) | Good (direct) |
|--------------------|---------------|
| `Latent reasoning の地図` (map of latent reasoning) | `Latent reasoning の分類` (classification of latent reasoning) |
| `Depth recurrence の見取り図` (sketch map of depth recurrence) | `Depth recurrence の系譜` (lineage of depth recurrence) |
| `LLM の俯瞰` (bird's-eye view of LLMs) | `LLM の概要` (overview of LLMs) |

## Naming the Book: Avoid Confusion with Established Fields

When choosing a book's `title:` and overview H1, **check whether it can be confused with an extremely well-known existing concept**.

Past example: `Recursive Reasoning Models` alone can be confused with the o1/R1 family of "reasoning models," meaning LLM thinking models. Add a **scope-defining prefix** such as `Small Recursive Reasoning Models` so a first-time reader immediately understands that the subject differs from LLMs.

### Examples of Differentiating Prefixes

- **Small / Tiny** — emphasizes small model scale in contrast to LLM scaling.
- **Latent / Continuous** — emphasizes continuous representations in contrast to discrete token generation.
- **Symbolic / Neuro-Symbolic** — emphasizes symbolic computation.
- **Multimodal** — emphasizes multimodality.

## Check Whether a Mermaid Diagram Has a Purpose

Used casually, Mermaid produces diagrams with **no reason to exist**: a purely linear sequence, duplication of a table, or a supposed two-axis diagram that actually has one axis.

### Three Questions to Answer Before Drawing

1. **Does the diagram express information that only a diagram can express?** If a table suffices, use a table.
2. **Are the claimed "two axes" or "three axes" truly independent?** Highly correlated axes merely arrange items along one axis.
3. **Does it duplicate the table immediately before it?** If so, delete the diagram or delete the table.

### Failure Pattern: Subgraphs Connected Only in a Sequence

```
subgraph A [...] / subgraph B [...] / subgraph C [...]
A -.-> B -.-> C
```

This merely **places three subgraphs in order**. The arrows convey nothing but sequence, so the information density is zero.

Better alternative: state the relationship directly in prose, for example, "A → B → C" or "A is a prerequisite for B, and B is a prerequisite for C." This has higher information density.

### Unicode Arrows (→) Cause Syntax Errors in Mermaid

Mermaid syntax requires ASCII arrows such as `-->`, `-.->`, and `==>`. A Unicode arrow `→` (U+2192), although familiar in Japanese prose, is not recognized as a token inside a Mermaid block and causes a syntax error.

```
flowchart LR
    A -.→ B    ← ❌ syntax error
    A -.-> B   ← ✅ OK
```

Past example: a refine agent tried to standardize arrows in Mermaid along with prose and broke the diagram by replacing them with `→`. Run `quarto preview` in Phase 7 to confirm Mermaid rendering.

## Slug Naming Policy

A file slug is **exposed in the URL and sidebar**, so make it neither too short nor too long and preserve enough information to infer the chapter topic.

### Good

- `process-reward-model.qmd`
- `depth-recurrence.qmd`
- `latent-reasoning.qmd`
- `inference-acceleration.qmd`

### Bad (Too Short and Lacking Context)

- `lineage.qmd` ← lineage of what is unclear.
- `map.qmd` ← map of what is unclear.
- `latent-map.qmd` ← `map` is metaphorical and semantically weak.

### Bad (Too Long and Redundant)

- `lineage-depth-recurrence.qmd` ← `depth-recurrence` is sufficient.
- `arc-agi-and-small-models.qmd` ← `arc-agi` is sufficient.

**Guideline**: one to three words in kebab case. Extract the core functional noun phrase from the chapter title.

Review chapter titles and slugs in one pass. A title change that changes the core concept also requires a slug review. For bilingual books, keep the same relative slug under `ja/` and `en/`; only the visible titles are translated.

## Style Elements That Regeneration Will Not Fix

After generating chapters with parallel subagents, remove these in the post-Phase-4 sweep because lint does not detect them:

- An italic lede directly below H1.
- An em dash in a heading, such as `## X — Y`.
- Inserted em dashes in prose, such as `AAA——BBB——CCC`.
- `—` used for an empty table cell; prefer an ASCII `-` or a blank cell.
- Inconsistent Japanese neural-net terms: `ネット`, `ネットワーク`, and `ニューラルネットワーク` instead of the required `ニューラルネット`.
- Inconsistent Japanese scale terms: `巨大` instead of `大規模` where the model or data is large-scale.
- Casual English terms such as `bucket` and `flavor`.
- Metaphorical Japanese headings containing terms such as `地図` ("map") or `俯瞰` ("bird's-eye view").
- Unicode arrows `→` inside Mermaid.
- Sidebar section names that abstractly enumerate "X and Y."

Prevent these issues by adding `references/style-consistency.md` to the required reading in the `chapter-writer` subagent prompt, then detect any remaining instances with a manual sweep in Phase 7.
