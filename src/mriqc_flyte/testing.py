# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
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
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
"""Comparators (images, masks, IQM files) and the baseline loader"""

import os
from pathlib import Path
from typing import Any

from nipype.interfaces.base.support import Bunch
from nipype.interfaces.base.traits_extension import isdefined
from nipype.utils.filemanip import loadpkl

# Where the baseline was made, so where its result files say their inputs and outputs are
BASELINE_ROOT = "/baseline"


def find_result(work: str | Path, subworkflow: str, node: str) -> Path:
    """Return the one ``result_<node>.pklz`` under ``work`` with ``subworkflow`` above it."""
    work = Path(work)
    found = sorted(
        path
        for path in work.rglob(f"result_{node}.pklz")
        # Leave out the node's folder and the file: a node may share its workflow's name
        if subworkflow in path.relative_to(work).parts[:-2]
    )

    # Raise FileNotFoundError if no results
    if len(found) == 0:
        raise FileNotFoundError(f"No file named 'result_{node}.pklz' was found.")

    # Raise RuntimeError if several are found, and list them
    if len(found) > 1:
        raise RuntimeError("Too many files found: , ".join([str(p) for p in found]))

    return found[0]


def baseline_node(run: str, subworkflow: str, node: str) -> dict[str, Any]:
    """Load the result file of one node of the baseline, as inputs and outputs."""
    root = os.environ.get("MRIQC_FLYTE_BASELINE")
    if root != "/baseline":
        raise RuntimeError("Baseline environment variable must be set to '/baseline'.")

    result = loadpkl(find_result(Path(root, run, "work"), subworkflow, node))

    # A Bunch for the MapNode (.dictcopy()), an output spec otherwise (.get())
    if isinstance(result.outputs, Bunch):
        outputs = result.outputs.dictcopy()
    else:
        outputs = result.outputs.__dict__

    # Keep only defined values
    outputs_defined = {}
    for key in outputs:
        if isdefined(outputs[key]):
            outputs_defined[key] = outputs[key]

    return {
        "inputs": result.inputs,
        "outputs": outputs_defined,
    }
