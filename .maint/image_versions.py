# Copyright The NiPreps Developers <nipreps@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Check the dev container's tools and record their versions (issue #1).

Run by the Dockerfile at build time::

    python image_versions.py /opt/mriqc-flyte/versions.json

and by the *Baseline* workflow in MRIQC's own image, where Flyte is missing::

    python image_versions.py --allow-missing /tmp/versions.json

The build fails if a tool is missing or does not report its version. The output is a flat JSON
object (name to version), which the *Dev container* workflow also copies into the image labels
``org.nipreps.mriqc-flyte.<name>``.
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# Tools that report a version: the command, and the pattern that extracts the version.
# MRIQC's image ships AFNI's programs but not the `afni` GUI binary, so a program reports it.
# AFNI programs exit with status 1 after `-ver`: the version pattern is the check.
TOOLS = {
    "ants": (["antsRegistration", "--version"], r"ANTs Version: (\S+)"),
    "afni": (["3dFWHMx", "-ver"], r"AFNI version=(AFNI_[\w.]+)"),
    "svht_denoise": (["svht_denoise", "--version"], r"svht_denoise (\S+)"),
}
# Tools that only need to start.
CHECKS = (
    ["N4BiasFieldCorrection", "--version"],
    ["3dFWHMx", "-help"],
    ["synthstrip", "-h"],
)
# SynthStrip has no version of its own: its code comes with mriqc, its model from this file.
SYNTHSTRIP_MODEL = Path("/opt/freesurfer/models/synthstrip.1.pt")
PACKAGES = (
    "flyte",
    "mriqc",
    "nipype",
    "niworkflows",
    "nireports",
    "nitransforms",
    "nibabel",
    "numpy",
    "scipy",
    "dipy",
    "torch",
    "templateflow",
    "pandas",
    "pyarrow",
)


def run(cmd: list[str], check: bool = True) -> str:
    """Run a command and return what it prints (stdout and stderr)."""
    return subprocess.run(
        cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    ).stdout


def main(out: Path, allow_missing: bool = False) -> None:
    for cmd in CHECKS:
        run(cmd)

    versions = {"python": platform.python_version()}
    for name, (cmd, pattern) in TOOLS.items():
        match = re.search(pattern, run(cmd, check=False))
        if match is None:
            sys.exit(f"Cannot read the version of {name} from `{' '.join(cmd)}`")
        versions[name] = match.group(1)
    digest = hashlib.sha256(SYNTHSTRIP_MODEL.read_bytes()).hexdigest()
    versions["synthstrip-model"] = f"sha256:{digest[:12]}"
    for name in PACKAGES:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            if not allow_missing:
                raise

    # A wheel built from git without its tags reports 0.0, which would then go into the
    # provenance of every IQM file.
    if versions["mriqc"] == "0.0":
        sys.exit("mriqc reports version 0.0")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(versions, indent=2) + "\n")
    print(out.read_text(), end="")


if __name__ == "__main__":
    args = sys.argv[1:]
    allow_missing = "--allow-missing" in args
    (out,) = (a for a in args if a != "--allow-missing")
    main(Path(out), allow_missing)
