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
"""Tests for the examples (examples folder)."""

import importlib.util
from pathlib import Path

import flyte
import nibabel as nb
import numpy as np
import pytest
from flyte.io import File

EXAMPLES = Path(__file__).parents[1] / "examples"


def load_example(name):
    """Import ``examples/<name>.py``, which is not part of the package."""
    spec = importlib.util.spec_from_file_location(name, EXAMPLES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def t1w(tmp_path):
    """A small synthetic image with a smooth intensity ramp, as a ``File``."""
    flyte.init()  # making a File outside a task needs it
    rng = np.random.default_rng(0)
    ramp = np.linspace(100, 200, 32)[:, None, None] * np.ones((32, 32, 32))
    path = tmp_path / "t1w.nii.gz"
    nb.Nifti1Image(ramp + rng.normal(0, 5, ramp.shape), np.eye(4)).to_filename(path)
    return File.from_local_sync(str(path))


@pytest.mark.binaries
def test_n4_output_path(t1w):
    n4 = load_example("n4")
    corrected = flyte.run(n4.n4, in_file=t1w).outputs()[0]
    path = flyte.run(n4.show_path, in_file=corrected).outputs()[0]
    assert corrected.path == path


@pytest.mark.binaries
def test_n4_delete_workdir(t1w):
    n4 = load_example("n4")
    with pytest.raises(
        Exception, match=r"FileNotFoundError: \[Errno 2\] No such file or directory.*"
    ):
        flyte.run(n4.main, in_file=t1w, delete_workdir=True)
