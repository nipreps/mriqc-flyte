# mriqc-flyte development container
#
# MRIQC's own image at the release pinned in pyproject.toml, plus Flyte 2 and the test tools.
# `docker-bake.hcl` builds it, and the `Dev container` workflow publishes it to
# ghcr.io/nipreps/mriqc-flyte (tags `dev`, `dev-<date>`), for linux/amd64 and linux/arm64,
# as MRIQC's.

ARG BASE_IMAGE=nipreps/mriqc:26.1.0
FROM ${BASE_IMAGE}

# MRIQC's pixi environment (Python 3.13, first on the PATH) has no pip: ensurepip adds it.
# Only the dependencies are installed (core, dev and test, read from pyproject.toml): the
# source is mounted at /work and found through PYTHONPATH.
COPY pyproject.toml /tmp/
RUN python -m ensurepip \
    && python -c "import tomllib; p = tomllib.load(open('/tmp/pyproject.toml', 'rb'))['project']; \
        x = p['optional-dependencies']; print('\n'.join(p['dependencies'] + x['dev'] + x['test']))" \
        > /tmp/requirements.txt \
    && cat /tmp/requirements.txt \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt /tmp/pyproject.toml

# The checks of issue #1: the build fails if a tool is missing. They also record the versions
# of the tools and main packages in /opt/mriqc-flyte/versions.json, which the workflow copies
# into the image labels, and the full package lists next to it.
COPY .maint/image_versions.py /tmp/
RUN python /tmp/image_versions.py /opt/mriqc-flyte/versions.json \
    && python -m pip list --format=freeze > /opt/mriqc-flyte/pip-freeze.txt \
    && ls /app/.pixi/envs/mriqc/conda-meta | sed -n 's/\.json$//p' \
        > /opt/mriqc-flyte/conda-packages.txt \
    && rm /tmp/image_versions.py

# $HOME (/home/mriqc) holds TemplateFlow (.cache/templateflow) and matplotlib's settings
# (.config/matplotlib), some of them owned by root. With `docker run -u`, any user must be able
# to write there: matplotlib warns otherwise, and TemplateFlow can't add a template.
RUN chmod -R a+rwX /home/mriqc

# MRIQC's image finds TemplateFlow through $HOME. Apptainer mounts the host's home over $HOME,
# which would hide the image's cache, so name it explicitly.
ENV TEMPLATEFLOW_HOME=/home/mriqc/.cache/templateflow \
    PYTHONPATH=/work/src
WORKDIR /work
ENTRYPOINT []
CMD ["/bin/bash"]

LABEL org.opencontainers.image.source="https://github.com/nipreps/mriqc-flyte" \
      org.opencontainers.image.description="mriqc-flyte development container: MRIQC (pinned release), ANTs, AFNI, SynthStrip, Flyte 2" \
      org.opencontainers.image.licenses="Apache-2.0"
