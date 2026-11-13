# Contributing to *mriqc-flyte*

*mriqc-flyte* is a project of the [*NiPreps* Community](https://www.nipreps.org/community/),
whose contributing guidelines apply. This file adds the conventions specific to this repository.

## Picking work
- Every piece of work has an issue. The [project board](https://github.com/orgs/nipreps/projects/18)
  shows the tier (core, stretch, later), the planned week and the dependencies.
- The core tier is the roadmap of the sMRI port, not a quota: its hours add up to more than a
  semester project, and nobody expects all of it. Each week, the sync-up picks what comes
  next, in the order of the board.
- Start an issue only when all issues in its *Blocked by* line are closed.
- Comment on the issue when you start it, so that a maintainer assigns it to you. Comment
  again if you get stuck for more than half a day.

## Your fork
You work in your own fork of this repository, and open pull requests from it. Once:
```bash
# After forking nipreps/mriqc-flyte on GitHub (the Fork button, top right)
git clone https://github.com/<your-user>/mriqc-flyte.git
cd mriqc-flyte
git remote add upstream https://github.com/nipreps/mriqc-flyte.git
```
Then for each issue, start a branch from the latest `main` of this repository, and push it to
your fork:
```bash
git fetch upstream
git switch -c enh/n4-task-gh12 upstream/main
# ... commit your work ...
git push -u origin enh/n4-task-gh12
```
GitHub then offers to open a pull request into `nipreps/mriqc-flyte`, branch `main`. The tests
of GitHub Actions run on it; for a new contributor, a maintainer approves the first runs.

## Branches, commits and pull requests
- **Branch:** `<type>/<short-description>-gh<issue>`, for example `enh/n4-task-gh12`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), for example
  `feat(anat): add the N4 bias-field correction task`.
- **Pull request title:** `TYPE: Short summary`, with the type in capitals (ENH, FIX, TST, DOC,
  MNT, CI) and no scope, for example `ENH: Add the N4 bias-field correction task`. ENH adds
  code (a task, an example, with its tests), FIX corrects it, TST changes only tests, DOC only
  documentation, MNT the build and the dependencies, CI the workflows. The branch prefix is
  the same type, in lower case.
- **Pull request body:** what changed, why, and the exact commands you ran to test it.
  End with `Closes #<issue>`.
- One issue per pull request, unless the issue says otherwise.

## Before opening a pull request
Inside the dev container (see the README):
```bash
ruff format --diff   # must print nothing
ruff check
pytest
```
Tests that need the baseline data or the neuroimaging binaries carry the `baseline` or
`binaries` markers. Run them inside the dev container. The tests that run the whole pipeline
carry the `pipeline` marker, and a plain `pytest` leaves them out: run `pytest -m pipeline`
too before opening a pull request that changes a task of the pipeline.

## Review
- The review asks for changes on the pull request itself. Push them to the same branch of
  your fork; the pull request is merged once they are in.
- When another merge makes your branch conflict, merge the new `main` into it
  (`git fetch upstream`, then `git merge upstream/main`), keep both sides, and run the tests
  again. Two open pull requests that add to the same module
  often conflict at its end, or on the same import line.

## Weekly status report
Every Friday, post a comment of at most 300 words on the pinned *Weekly status reports* issue,
with three headings: **Done**, **Next**, **Risks**.

## Use of AI tools
This repository started as an ISC semester project run at **AI level 1**:
- AI tools may be used for *assistance only*: explaining concepts, finding documentation, or
  interpreting an error message.
- Code, tests, documentation and reports must be written by you. Do not paste generated
  content into a contribution.

## License
By contributing you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
