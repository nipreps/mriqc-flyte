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
"""Utility that skips `baseline` tests when the `MRIQC_FLYTE_BASELINE` environment
variable is not defined, and skips `binaries` tests when `N4BiasFieldCorrection`
is not on the `PATH`."""

import os

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "baseline: needs the nipype baseline outputs (set MRIQC_FLYTE_BASELINE)",
    )
    config.addinivalue_line(
        "markers",
        "binaries: needs ANTs, AFNI and SynthStrip on the PATH (run in the dev container)",
    )


def pytest_collection_modifyitems(items):
    """Skips all tests with markers baseline or binaries if conditions are not met"""
    from shutil import which

    baseline = os.getenv("MRIQC_FLYTE_BASELINE") is not None
    binaries = which("N4BiasFieldCorrection") is not None

    # Reference: https://medium.com/@vlasjes/pytest-conditional-testing-using-custom-parameter-5a86f67d12d4
    if not baseline:
        skip_baseline = pytest.mark.skip("MRIQC_FLYTE_BASELINE flag not set")
        for item in items:
            if "baseline" in item.keywords:
                item.add_marker(skip_baseline)
    if not binaries:
        skip_binaries = pytest.mark.skip(reason="N4BiasFieldCorrection not found in $PATH")
        for item in items:
            if "binaries" in item.keywords:
                item.add_marker(skip_binaries)
