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
"""Tests for types that the Flyte tasks return."""

import flyte
from flyte.io import File

env = flyte.TaskEnvironment(name="types")


def get_test_file(tmp_path, file_name: str = "a.txt"):
    """Util function that creates a testing file in a temporary directory."""
    (tmp_path / file_name).write_text("a")
    return File.from_local_sync(str(tmp_path / file_name))


# Single File
@env.task
def pass_file(x: File) -> File:
    return x


def test_file(tmp_path):
    """Test that a file can be serialized for a Flyte task."""
    f = get_test_file(tmp_path)
    out = flyte.run(pass_file, x=f).outputs()[0]  # outputs() is a tuple
    assert out.path == f.path  # == on two Files also compares hidden state


# Optional File
@env.task
def file_none(x: File | None) -> File | None:
    return x


def test_file_optional_file(tmp_path):
    """Test that a file can be serialized for a "File | None" input for a Flyte task."""
    f = get_test_file(tmp_path)
    out = flyte.run(file_none, x=f).outputs()[0]  # outputs() is a tuple
    assert out.path == f.path  # == on two Files also compares hidden state


def test_file_optional_none():
    """Test that "None" can be used for a "File | None" input for a Flyte task."""
    out = flyte.run(file_none, x=None).outputs()[0]
    assert out is None


# list[File]
@env.task
def listfile(x: list[File]) -> list[File]:
    return x


def test_list_file(tmp_path):
    """Test that a list of Files can be correctly serialized and sent through a Flyte task"""
    files = [get_test_file(tmp_path, f"{i}.txt") for i in range(5)]
    out = flyte.run(listfile, x=files).outputs()[0]  # outputs() is a tuple
    right = [files[i].path == out[i].path for i in range(len(out))]
    set_right = set(right)
    assert len(out) == len(files) and len(set_right) == 1 and set_right.pop()


# dict[str, float | int]
@env.task
def dict_str_float_int(d: dict[str, float | int]) -> dict[str, float | int]:
    return d


def test_dataclass_dict_str_float_or_int():
    """dict[str, float | int] can be used as an input and return type while running flyte.run()."""
    d = {"a": 1.2, "b": 5.4, "c": 62}
    outputs = flyte.run(dict_str_float_int, d).outputs()[0]

    # are types right?
    right = [type(d[i]) is type(outputs[i]) for i in outputs]
    right_set = set(right)

    assert isinstance(outputs, dict) and len(right_set) == 1 and right_set.pop()


# Two outputs (tuple)
@env.task
def two_outputs(x: int) -> tuple[int, str]:
    return x, str(x)


def test_tuple():
    """Tuples are returned correctly from Flyte tasks"""
    test_val = 3
    run = flyte.run(two_outputs, x=test_val)
    assert (
        len(run.outputs()) == 2
        and run.outputs()[0] == test_val
        and run.outputs()[1] == str(test_val)
    )
