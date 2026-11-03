mriqc-flyte
===========

*MRIQC*'s image quality workflows, ported from `nipype <https://nipype.readthedocs.io>`__
to the `Flyte 2 <https://www.union.ai/docs/v2/flyte/>`__ orchestrator.

.. warning::

   Work in progress. Started as an ISC (HES-SO Valais-Wallis) semester project in
   November 2026. The supported tool remains `MRIQC <https://github.com/nipreps/mriqc>`__.

What this is
------------
`MRIQC <https://mriqc.readthedocs.io>`__ extracts image quality metrics (IQMs) from structural
(sMRI), functional (fMRI) and diffusion (dMRI) MRI. Today its processing graph is built and
executed with nipype. This repository re-expresses that graph as Flyte 2 tasks:

* **Stage 1:** each Flyte task wraps one of MRIQC's existing interfaces, so results stay
  numerically identical to MRIQC.
* **Stage 2:** tasks call the underlying tools directly and nipype is no longer needed.

The port starts with the sMRI workflow. See `docs/roadmap.md <docs/roadmap.md>`__ for the plan
and `docs/primer.md <docs/primer.md>`__ for a primer on MRIQC and Flyte.

Getting started
---------------
Development happens inside the dev container, which provides ANTs, AFNI, SynthStrip and
Python 3.11 with this package's dependencies, at the MRIQC commit pinned in ``pyproject.toml``.
From a clone of this repository:

.. code-block:: bash

   docker run --rm -it --platform linux/amd64 -u "$(id -u):$(id -g)" \
       -v "$PWD":/work ghcr.io/nipreps/mriqc-flyte:dev
   pytest   # inside the container

The repository is mounted at ``/work`` and found through ``PYTHONPATH``, so there is nothing to
install. The image is amd64 only (as MRIQC's): on Apple-silicon Macs, enable Rosetta in Docker
Desktop. It is built by the *Dev container* workflow from ``Dockerfile`` and
``docker-bake.hcl``. The onboarding issues (label ``onboarding``) take it from there.

Contributing
------------
See `CONTRIBUTING.md <CONTRIBUTING.md>`__. This project follows the
`NiPreps community guidelines <https://www.nipreps.org/community/>`__.

License
-------
Apache License 2.0. See `LICENSE <LICENSE>`__ and `NOTICE <NOTICE>`__.
