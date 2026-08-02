# Repository instructions

## Local preview

Use `quarto preview --profile public` only when the whole public site is needed. On a cold output directory, Quarto prepares every page before serving it.

For a quick visual check of one page, render only that page and serve `_site`:

```bash
quarto render en/one-step-generation/drifting-models.qmd --profile public --to html
python3 -m http.server 4200 --directory _site
```

Rerun the render command after changing the page or shared CSS/JavaScript.
