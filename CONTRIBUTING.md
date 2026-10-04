# Contributing

Humans and agents contribute the same way, and every change gets a human review.

## Workflow

1. Open an issue for any piece of work: a section to draft, a figure to make, an analysis to run, a claim to verify.
2. Create a branch for that issue. One section file or one figure per branch keeps diffs small.
3. Open a pull request linked to the issue. CI builds a preview of the paper; check it.
4. At least one other author reviews with inline comments before the PR is merged to `main`.

Assign each issue to one person or agent at a time to avoid conflicting edits to the same section.

## Small fixes

Typos and wording fixes do not need an issue.
Use GitHub's web editor on the file and open a pull request from there.

## Writing conventions

- One sentence per line in `.qmd` files. GitHub comments attach to lines, so this keeps feedback precise and diffs readable.
- Every number in the text traces to `data/results_manifest.csv` or a script in `analysis/`.
- Every figure is generated from code in `figures/` and has a `source_data.csv`.
- Do not add references you have not checked against the source.

## Giving feedback

- Use PR review comments for line-level feedback, and "suggest a change" so authors can apply edits in one click.
- Use issues or Discussions for broader questions, such as whether a claim is supported.
- Use `TODO` markers in source for quick notes to co-authors, and clear them before submission.

## Authorship and roles

Record your contribution roles in [CONTRIBUTIONS.md](CONTRIBUTIONS.md) so author lists and contribution statements are easy to assemble at submission.
AI tools are not listed as authors, and AI use is disclosed in the Methods of the paper.

## Secrets

Never commit tokens or credentials.
The Hugging Face token lives in your environment locally and in GitHub Actions secrets in CI.
Do not commit trace files; they are fetched by script.
