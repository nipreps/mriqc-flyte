Unreleased
==========
* Repository scaffold (NiPreps boilerplate, CI, issue templates, primer and roadmap).
* Dev container (MRIQC's image at the pinned commit plus Flyte 2), built and published by the
  *Dev container* workflow (#1).
* Dev tooling: the Flyte TUI in the dev image, ruff pinned for the image, CI and pre-commit,
  and the image version labels.
* Baseline: standard MRIQC run twice on the test T1w, published as a pre-release by the
  *Baseline* workflow, which also checks the ANTs seeds (#7, #8).
* MRIQC pinned at d5cb0c82, which adds ``--random-seed`` (nipreps/mriqc#1453). The issues'
  code pointers stay at f6129094.
* Baseline seeded with ``--random-seed 42``, so that its two runs are identical (#7, #8).
