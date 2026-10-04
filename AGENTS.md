# Instructions for AI agents

You are welcome to contribute here.
Read this file and [CONTRIBUTING.md](CONTRIBUTING.md) before you start.

## What you may do

- Work on issues labeled `agent-ready`. Do not start on other issues unless a maintainer asks you to.
- Edit files in `manuscript/`, `figures/`, `analysis/`, `supplement/`, and `data/` as the issue requires.
- Open pull requests as drafts.
- Merge a pull request, including your own, when a maintainer explicitly asks you to and all of these hold: CI passes on the latest commit, the branch has no merge conflicts, and no review thread is unresolved.
  Mark a draft ready for review before merging, and use a merge commit.

## What you must not do

- Do not push to `main`.
- Do not merge a pull request unless a maintainer has explicitly asked you to merge that pull request.
- Do not commit tokens, credentials, or trace files. Read the Hugging Face token from the `HF_TOKEN` environment variable.
- Do not edit `.github/`, license files, or this file unless the issue says so.
- Do not add references you have not checked against the source. Never invent citations.
- Do not state a number in the text that you cannot trace to `data/results_manifest.csv` or a script in `analysis/`.

## Required in every pull request

- Link the issue.
- Say how each number or claim was verified, including checks against independent ground truth.
- Regenerate every figure you touch from code, and update its `source_data.csv`.
- Confirm the manuscript still builds with `quarto render manuscript`.
- Name the tool and model you used, so the paper's AI-use disclosure can be written accurately.
- Add the label `agent` to your pull request.

## Conventions

- One sentence per line in `.qmd` files.
- Keep each pull request small: one section or one figure.
- If an issue is unclear or you cannot verify something, say so in the PR rather than guessing.
