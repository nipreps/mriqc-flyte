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
Development happens inside the dev container: MRIQC's own image of the release pinned in
``pyproject.toml`` (ANTs, AFNI, SynthStrip, Python 3.13), plus this package's dependencies.
From a clone of your fork (``CONTRIBUTING.md``, *Your fork*):

.. code-block:: bash

   docker run --rm -it -u "$(id -u):$(id -g)" -v "$PWD":/work ghcr.io/nipreps/mriqc-flyte:dev
   pytest   # inside the container

The repository is mounted at ``/work`` and found through ``PYTHONPATH``, so there is nothing to
install. The image runs natively on ``linux/amd64`` and ``linux/arm64`` (Apple-silicon Macs),
as MRIQC's. It is built by the *Dev container* workflow from ``Dockerfile`` and
``docker-bake.hcl``. The versions of its tools and main packages are in the image labels
(``docker inspect``) and in ``/opt/mriqc-flyte/versions.json``, with the full package lists
beside it. The onboarding issues (label ``onboarding``) take it from there.

The baseline
~~~~~~~~~~~~
The tests compare the port with the **baseline**: standard MRIQC (the pinned release, in its
own image) run twice on the test T1w (sub-50137 of MRIQC's CI dataset), keeping every node's
outputs. MRIQC ran with ``--random-seed 42`` and one thread per process, so the two runs are
identical, as the release notes show. MRIQC's numbers differ slightly between ``amd64`` and
``arm64``, so the baseline has a pair of runs for each: take the one of your machine. It is
published as the pre-release ``baseline-t1w-26.1.0``. Download and unpack it once:

.. code-block:: bash

   url=https://github.com/nipreps/mriqc-flyte/releases/download/baseline-t1w-26.1.0
   case "$(uname -m)" in x86_64) arch=amd64 ;; *) arch=arm64 ;; esac
   mkdir -p baseline && cd baseline
   for f in bids.tar.gz run-1-$arch.tar.gz run-2-$arch.tar.gz SHA256SUMS; do
       curl -fLO "$url/$f"
   done
   grep -E "bids|$arch" SHA256SUMS | shasum -a 256 -c && for f in *.tar.gz; do tar -xzf "$f"; done
   cd ..

Then mount it at ``/baseline`` and point ``MRIQC_FLYTE_BASELINE`` to it. The baseline was
produced there, so the paths stored in its result files resolve as they are:

.. code-block:: bash

   docker run --rm -it -u "$(id -u):$(id -g)" \
       -v "$PWD":/work -v "$PWD/baseline":/baseline:ro -e MRIQC_FLYTE_BASELINE=/baseline \
       ghcr.io/nipreps/mriqc-flyte:dev

The tests that need it are skipped when ``MRIQC_FLYTE_BASELINE`` is unset, as on GitHub Actions.

With the baseline mounted, the tests run the real programs, so a plain ``pytest`` grows to
minutes as the port does (about 12 min for the whole sMRI port, on a recent x86 machine). The
tests that run the whole pipeline carry the ``pipeline`` marker, and a plain ``pytest`` leaves
them out: run them before opening a pull request that changes the pipeline. For a quick check,
run one file, or the tests GitHub Actions runs (under a minute):

.. code-block:: bash

   pytest -m pipeline   # the end-to-end tests only
   pytest test/test_<one file>.py
   pytest -m "not baseline and not binaries"

Contributing
------------
See `CONTRIBUTING.md <CONTRIBUTING.md>`__. This project follows the
`NiPreps community guidelines <https://www.nipreps.org/community/>`__.

License
-------
Apache License 2.0. See `LICENSE <LICENSE>`__ and `NOTICE <NOTICE>`__.
