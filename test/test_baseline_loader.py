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
"""Tests for the baseline_loader in src/mriqc_flyte/testing.py"""

from pathlib import Path

import pytest

from mriqc_flyte.testing import baseline_node, find_result


@pytest.mark.baseline
def test_baseline_node_pre_n4():
    node = baseline_node("run-1", "synthstrip_wf", "pre_n4")
    assert Path(node["outputs"]["output_image"]).exists() and isinstance(node, dict)


@pytest.mark.baseline
def test_baseline_node_tpms_std2t1w():
    node = baseline_node("run-1", "SpatialNormalization", "tpms_std2t1w")

    exists = [Path(v).exists() for v in node["outputs"]["output_image"]]
    exists = set(exists)

    assert exists.pop()


def test_find_result_several(tmp_path):
    for sub in ("a_wf", "b_wf"):
        folder = tmp_path / "mriqc_wf" / sub / "smooth"
        folder.mkdir(parents=True)
        (folder / "result_smooth.pklz").touch()
    with pytest.raises(RuntimeError, match="Too many files found"):  # a part of your message
        find_result(tmp_path, "mriqc_wf", "smooth")


def test_baseline_node_needs_the_mount(monkeypatch):
    monkeypatch.setenv("MRIQC_FLYTE_BASELINE", "/elsewhere")
    with pytest.raises(RuntimeError, match="Baseline environment variable must be set to .*"):
        baseline_node("run-1", "synthstrip_wf", "pre_n4")
