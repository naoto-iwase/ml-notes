# Citations and Footnotes

<!-- Adapted from posit-dev/skills (quarto-authoring), MIT licensed -->

## Site-Specific Operating Rules

- Place each book's bibliography file at `{lang}/{book}/references.bib`.
- Set `bibliography: references.bib` in `{lang}/{book}/_metadata.yml`.
- Do not repeat `csl: https://www.zotero.org/styles/chicago-author-date` (an author-year style similar to natbib's plainnat) or `link-citations: true` for each book; both are already configured globally in `_quarto.yml`.
- **Do not add a `## 参考文献` (`References`) heading or a `::: {#refs} :::` block**: when `bibliography:` is configured, Pandoc/Quarto automatically inserts the bibliography at the end of the document. `::: {#refs}` is optional and only changes its placement; the list appears at the end without it. Avoid an explicit heading because it creates a duplicate label above the auto-inserted list. Individual reference details are also available through citation hover previews.
- Whenever possible, put an **OpenReview or official repository** URL in the `url` field. If only arXiv is available, use the arXiv URL.
- Standardize citation keys as `lastname{year}{shortname}` (for example, `sahoo2024mdlm` and `austin2021d3pm`).
- Write bibliography entries in the **same style used for ordinary paper writing**: brace-protected title capitalization such as `{T}eaching`, a complete author list, and detailed fields. This policy anticipates sharing entries with research-paper bibliographies.
- For a book with no bibliography file, do not use `[@key]`; use ordinary Markdown links instead to avoid undefined references.
- **Do not expose bibliography keys in prose** (details below).
- **Prevent hallucinations when adding entries** (details below).

## Do Not Expose Bibliography Keys

Citation keys (`@key` / `[@key]`) become meaningful to readers only after Pandoc processes them. A raw key visible to readers leaks an implementation detail and must be avoided.

**❌ Prohibited patterns**:

- `` `[@sahoo2024mdlm]` `` — backticks prevent citation processing and display the raw key.
- `` `@tbl-mapping` `` / `` `@fig-name` `` — the same applies to cross-references: wrapping `@xref` in backticks leaves it raw instead of resolving it to "Table 1" or a similar label.
- `The bib entry is registered as @key` — a meta-level reference to an implementation detail.
- A table column or row labeled `引用キー` (`citation key`) or `Citation key` — not reader-facing information.
- Exposing a key in prose, such as `The paper represented by @key ...`.

**✅ Correct**:

- `MDLM [@sahoo2024mdlm] ...` — processed as a citation and converted to `[1]` or the style's equivalent.
- `MDLM was introduced by @sahoo2024mdlm` — an in-text citation.
- `The paper is unpublished [@ye2025dream7b]` — citing blog or miscellaneous references with `[@key]` also includes them in the bibliography.

If an implementation note such as "the key was registered as X" is necessary, write it as a `%` comment inside `references.bib`.

## Preventing Hallucinations

Do **not guess** bibliography titles, authors, or arXiv IDs. Common LLM failure modes include:

- Confusing a method name with a paper title. For example, "Elastic-Cache" is a method name; the paper title is "Attention is All You Need for KV Cache in Diffusion LLMs."
- Copying a survey caption or explanatory sentence as the title.
- Mistyping or confusing arXiv IDs.

**Recommended procedure**:

1. **Open the arXiv abstract page or OpenReview directly** before transcribing the title and authors.
2. When adding entries from a survey, use the **survey authors' published `main.bib`** (bundled with the arXiv e-print) as the primary source:

```bash
# Extract the arXiv e-print to obtain main.bib / sections/*.tex / figs/*.pdf
uv run .agents/skills/book-writer/scripts/fetch_arxiv_figures.py <arxiv_id>
ls /tmp/arxiv_figures/<arxiv_id>/main.bib
```

3. Use the **validation script** to check the document's `[@key]` references against the bibliography mechanically:

```bash
python3 .agents/skills/book-writer/scripts/lint_chapters.py {lang}/{book}
```

The script detects:

- Keys referenced as `[@key]` in the document but undefined in the bibliography.
- Exposed `[@key]` / `@xref` strings wrapped in backticks and therefore rendered raw.
- Meta-level references such as the Japanese lint fixtures `引用キー` (`citation key`) and `bib エントリ` (`bib entry`).
- Duplicate bibliography keys.
- `*.qmd` filenames exposed outside Markdown links or includes.
- File slugs (for example, `survey-li2025`) exposed in `(slug)` / `（slug）` syntax.

---

Quarto uses Pandoc's citation system with support for BibTeX, CSL styles, and flexible citation formatting.

## Citation Syntax

### Basic Citations

````markdown
According to @smith2020, the results indicate...
The study showed significant results [@smith2020].
````

### Variations

| Syntax                | Output                     |
| --------------------- | -------------------------- |
| `@smith2020`          | Smith (2020)               |
| `[@smith2020]`        | (Smith 2020)               |
| `[-@smith2020]`       | (2020) - author suppressed |
| `@Smith2020 [p. 10]`  | Smith (2020, p. 10)        |
| `[@smith2020, p. 10]` | (Smith 2020, p. 10)        |

### Multiple Citations

````markdown
Several studies [@smith2020; @jones2021] found...
[@smith2020; @jones2021; @williams2022]
````

### Citation with Locators

````markdown
@smith2020 [p. 33]
@smith2020 [chap. 2]
[@smith2020, pp. 10-15]
[@smith2020, fig. 3]
````

Common locators: `p.`, `pp.`, `chap.`, `sec.`, `fig.`, `eq.`, `vol.`.

### In-Text vs Parenthetical

````markdown
@smith2020 says... → Smith (2020) says...
As shown by @smith2020... → As shown by Smith (2020)...
The results [@smith2020]... → The results (Smith 2020)...
````

### Prefix and Suffix

````markdown
[see @smith2020, pp. 10-15, for discussion]
→ (see Smith 2020, pp. 10-15, for discussion)
````

## Bibliography Configuration

### Basic Setup

```yaml
bibliography: references.bib
```

### Multiple Files

```yaml
bibliography:
  - references.bib
  - additional.bib
```

### BibTeX File Example

```bibtex
@article{smith2020,
  author = {Smith, John},
  title = {Article Title},
  journal = {Journal Name},
  year = {2020},
  volume = {10},
  pages = {1-20}
}

@book{jones2021,
  author = {Jones, Sarah},
  title = {Book Title},
  publisher = {Publisher},
  year = {2021}
}
```

### Other Formats

Quarto supports:

- BibTeX (`.bib`)
- BibLaTeX (`.bib`)
- CSL JSON (`.json`)
- CSL YAML (`.yaml`)

## Citation Styles (CSL)

### Specify CSL File

```yaml
bibliography: references.bib
csl: apa.csl
```

### Find CSL Files

- [Zotero Style Repository](https://www.zotero.org/styles)
- [CSL Repository](https://github.com/citation-style-language/styles)

### Common Styles

```yaml
csl: apa.csl           # APA 7th edition
csl: chicago-author-date.csl
csl: ieee.csl
csl: nature.csl
csl: vancouver.csl
```

## Bibliography Placement

By default, bibliography appears at end. Control placement:

````markdown
## References

::: {#refs}
:::

## Appendix

Additional content after references.
````

### Suppress Bibliography

```yaml
suppress-bibliography: true
```

## Footnotes

### Inline Footnotes

````markdown
This is text with a footnote.^[This is the footnote content.]
````

### Reference Footnotes

````markdown
This is text with a footnote.[^1]

[^1]: This is the footnote content.
````

### Multi-Paragraph Footnotes

````markdown
[^longnote]: This is a long footnote.

    It has multiple paragraphs.

    And can include code:

    ```{.r}
    x <- 1
    ```
````

## Citation Methods

### Citeproc (Default)

Standard Pandoc citation processing:

```yaml
bibliography: references.bib
```

### BibLaTeX (PDF)

```yaml
bibliography: references.bib
format:
  pdf:
    cite-method: biblatex
```

### Natbib (PDF)

```yaml
bibliography: references.bib
format:
  pdf:
    cite-method: natbib
```

## Reference Section Title

```yaml
reference-section-title: "References"
```

Or for other languages:

```yaml
lang: de
reference-section-title: "Literaturverzeichnis"
```

## Citation Links

Control hyperlinking:

```yaml
link-citations: true # Link in-text to bibliography
link-bibliography: true # Link URLs in bibliography
```

## Citation Processing Options

```yaml
citeproc: true # Enable citation processing
citation-abbreviations: abbrev.json # Journal abbreviations
notes-after-punctuation: true
```

## DOI and URL Handling

```yaml
format:
  html:
    citations:
      link-citations: true
  pdf:
    include-in-header:
      - text: |
          \usepackage{hyperref}
```

## Footnote Location

Control where footnotes appear:

```yaml
reference-location: document   # End of document
reference-location: section    # End of section
reference-location: block      # End of block
reference-location: margin     # In margin (if supported)
```

## Citation Hover (HTML)

Enable hover previews:

```yaml
format:
  html:
    citation-hover: true
```

## Author-Date vs Numeric

Controlled by CSL style:

```yaml
# Author-date style
csl: apa.csl

# Numeric style
csl: ieee.csl
```

## Citing Software

```bibtex
@software{tidyverse,
  author = {Wickham, Hadley},
  title = {tidyverse: Easily Install and Load the 'Tidyverse'},
  year = {2023},
  url = {https://CRAN.R-project.org/package=tidyverse}
}
```

Or use `@Manual` for R packages.

## Resources

- [Quarto Citations](https://quarto.org/docs/authoring/citations.html)
- [Pandoc Citations](https://pandoc.org/MANUAL.html#citations)
- [CSL Styles](https://citationstyles.org/)
