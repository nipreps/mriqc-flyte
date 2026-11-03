# mriqc-flyte development container
#
# MRIQC's own image at the MRIQC commit pinned in pyproject.toml, plus Flyte 2 and the test
# tools. No MRIQC image is published for that commit, so the base is built from MRIQC's own
# Dockerfile. `docker-bake.hcl` builds both, and the `Dev container` workflow publishes them
# to ghcr.io/nipreps/mriqc-flyte (tags `base-<mriqc commit>`, `dev`, `dev-<date>`).
#
# Both images are amd64 only, like MRIQC's. Apple-silicon Macs run them through Rosetta.

ARG BASE_IMAGE=ghcr.io/nipreps/mriqc-flyte:base-f6129094
FROM ${BASE_IMAGE}

# MRIQC's micromamba base already runs Python 3.11 (pinned in /opt/conda/conda-meta/pinned),
# which Flyte 2 supports, so the dependencies go into that same environment. Only the
# dependencies are installed (core, dev and test, read from pyproject.toml): the source is
# mounted at /work and found through PYTHONPATH.
COPY pyproject.toml /tmp/
RUN python -c "import tomllib; p = tomllib.load(open('/tmp/pyproject.toml', 'rb'))['project']; \
        x = p['optional-dependencies']; print('\n'.join(p['dependencies'] + x['dev'] + x['test']))" \
        > /tmp/requirements.txt \
    && cat /tmp/requirements.txt \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt /tmp/pyproject.toml

# The stock image keeps its TemplateFlow cache outside $HOME (/templateflow), so Apptainer's
# home mount does not hide it. Let any user add templates to it.
RUN tf_home="$(python -c 'from templateflow.conf import TF_HOME; print(TF_HOME)')" \
    && echo "TemplateFlow cache: $tf_home" \
    && chmod -R a+rwX "$tf_home"

# The checks of issue #1: the build fails if a tool is missing.
RUN N4BiasFieldCorrection --version \
    && antsRegistration --version \
    && 3dFWHMx -help > /dev/null \
    && afni -ver \
    && synthstrip -h > /dev/null \
    && python -c "import flyte, mriqc; print('flyte', flyte.__version__, 'mriqc', mriqc.__version__); assert mriqc.__version__ != '0.0'"

ENV PYTHONPATH=/work/src
WORKDIR /work
ENTRYPOINT []
CMD ["/bin/bash"]

LABEL org.opencontainers.image.source="https://github.com/nipreps/mriqc-flyte" \
      org.opencontainers.image.description="mriqc-flyte development container: MRIQC (pinned commit), ANTs, AFNI, SynthStrip, Flyte 2" \
      org.opencontainers.image.licenses="Apache-2.0"
