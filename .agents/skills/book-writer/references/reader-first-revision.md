# Reader-First Revision

Use this workflow when a technically correct chapter is still difficult for a first-time reader.

## Diagnose the Difficulty

Do not add more material first. Check whether the chapter has one of these structural problems:

- It begins with equations, an optimizer taxonomy, or paper names before stating the question.
- Abstract labels such as `artifact`, `surface`, `policy`, or a newly coined umbrella term appear before a concrete example.
- Several method-specific mechanisms are introduced at once even though they are not needed for the chapter's claim.
- A table classifies methods before the reader understands the classification axis.
- The introduction, final section, and summary repeat the same principle without adding a new role.

## Rewrite Order

Prefer this order:

1. **Question:** state the practical question the chapter answers.
2. **Plain definition:** define the central concept in one or two sentences.
3. **Concrete example:** map one failure, decision, or object across the chapter's categories.
4. **Structure:** introduce the table, stages, or roles used to organize the chapter.
5. **Formalization:** add notation or equations after the reader knows what each symbol represents.
6. **Evidence:** introduce papers as examples of the structure, not as the structure itself.
7. **Limits:** distinguish what the evidence supports from what remains unknown.
8. **Takeaway:** state the decision rule or main claim once.

Equations may remain early when the equation itself is the chapter's object. Otherwise, intuition should precede formalization.

## Preserve Substance While Reducing Load

A readability rewrite should preserve:

- the chapter's central claim;
- primary-source citations;
- figures that carry unique information;
- quantitative results needed for the argument;
- explicit limitations and uncertainty.

Remove or move details that do not change the reader's decision, such as an optimizer's training acronym, internal lifecycle hook names, or a complete search algorithm when the chapter only needs the update boundary.

## Check Terminology Provenance

For every term used as a heading, table row, or organizing axis, determine whether it is:

1. an established term used by the cited source;
2. a repository-wide convention;
3. a new label introduced only for this chapter.

Do not present category 3 as established terminology. Prefer a direct functional label. If the new label is necessary, define it explicitly and state that it is this book's organizing term.

A source may discuss code, workflows, or agentic systems without using the exact umbrella phrase chosen by the author. Verify the exact wording before attributing the phrase to the paper.

## Use Examples to Explain Scope

When categories differ by edit scope or abstraction level, use one synthetic example across all categories. For example, the same tool-use failure can be addressed by:

- changing an instruction;
- enforcing an execution order;
- adding an implementation-level validator.

The example should clarify the boundary between categories. It should not introduce a second taxonomy.

## Revision and Rendering Cadence

During interactive prose revision:

1. Make a coherent batch of wording and structure edits.
2. Run cheap source checks for stale terms, tone, links, and citations.
3. Do not render after every small wording change.
4. Render at a user-requested checkpoint, after structural or asset changes, and before publication.
5. After rendering, inspect the actual page width for table wrapping, figure scale, clipping, and navigation.

A successful Quarto render proves syntax and asset resolution. It does not prove that the chapter is understandable.
