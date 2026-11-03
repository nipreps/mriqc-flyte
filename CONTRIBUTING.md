# Contributing to *mriqc-flyte*

*mriqc-flyte* is a project of the [*NiPreps* Community](https://www.nipreps.org/community/),
whose contributing guidelines apply. This file adds the conventions specific to this repository.

## Picking work
- Every piece of work has an issue. The [project board](https://github.com/orgs/nipreps/projects)
  shows the tier (core, stretch, later), the planned week and the dependencies.
- Start an issue only when all issues in its *Blocked by* line are closed.
- Assign yourself before you start, and comment if you get stuck for more than half a day.

## Branches, commits and pull requests
- **Branch:** `<type>/<short-description>-gh<issue>`, for example `enh/n4-task-gh12`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), for example
  `feat(anat): add the N4 bias-field correction task`.
- **Pull request title:** `TYPE: Short summary`, with the type in capitals (ENH, FIX, TST, DOC,
  MNT, CI) and no scope, for example `ENH: Add the N4 bias-field correction task`.
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
`binaries` markers. Run them inside the dev container.

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
