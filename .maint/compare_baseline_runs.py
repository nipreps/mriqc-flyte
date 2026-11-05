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
"""Compare two MRIQC runs of the baseline (issues #7 and #8).

Usage, inside the dev container, with the baseline at ``/baseline``::

    python .maint/compare_baseline_runs.py /baseline/run-1 /baseline/run-2 > report.md

Prints a Markdown report with three parts:

1. **Seeds (#7):** whether registration and Atropos gave identical outputs in both runs.
2. **Steps:** for every NIfTI file in the work directories, whether the two runs agree
   (identical data, or the largest absolute difference).
3. **Noise floor (#8):** the relative difference of every IQM between the two runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h5py
import nibabel as nb
import numpy as np


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_difference(a: Path, b: Path) -> float | None:
    """Largest absolute voxel difference, or None when shapes or affines differ."""
    ia, ib = nb.load(a), nb.load(b)
    if ia.shape != ib.shape or not np.allclose(ia.affine, ib.affine):
        return None
    da = np.asanyarray(ia.dataobj, dtype="float64")
    db = np.asanyarray(ib.dataobj, dtype="float64")
    return float(np.abs(da - db).max()) if da.size else 0.0


def h5_parameters(path: Path) -> list[np.ndarray]:
    """All datasets of an ITK HDF5 transform file, in a stable order."""
    with h5py.File(path, "r") as f:
        names: list[str] = []
        f.visit(lambda n: names.append(n) if isinstance(f[n], h5py.Dataset) else None)
        return [np.asarray(f[n][()]) for n in sorted(names)]


def node_dirs(run: Path, node: str) -> list[Path]:
    """The folders of the nipype nodes called ``node``.

    A node folder holds ``result_<node>.pklz``. Matching folder names alone would also find
    workflows of the same name (MRIQC's ``SpatialNormalization`` workflow holds a
    ``SpatialNormalization`` node).
    """
    return sorted(p.parent for p in (run / "work").rglob(f"result_{node}.pklz"))


def nifti_files(root: Path) -> list[Path]:
    """NIfTI files under ``root``. Iterable folders can have ``.nii.gz`` in their names."""
    return sorted(
        p for p in root.rglob("*.nii*") if p.is_file() and p.name.endswith((".nii", ".nii.gz"))
    )


def seed_section(run1: Path, run2: Path) -> list[str]:
    lines = ["## 1. Seeds (#7)", ""]
    for node, pattern in (("SpatialNormalization", "*Composite.h5"), ("segmentation", "*.nii.gz")):
        d1, d2 = node_dirs(run1, node), node_dirs(run2, node)
        if len(d1) != 1 or len(d2) != 1:
            lines.append(
                f"- `{node}`: expected one node folder per run, found {len(d1)} and {len(d2)}"
            )
            continue
        files = sorted(p.name for p in d1[0].glob(pattern) if p.is_file())
        if not files:
            lines.append(f"- `{node}`: no `{pattern}` in `{d1[0]}`")
            continue
        verdicts = []
        for name in files:
            a, b = d1[0] / name, d2[0] / name
            if sha256(a) == sha256(b):
                verdicts.append(f"`{name}` byte-identical")
            elif name.endswith(".h5"):
                pa, pb = h5_parameters(a), h5_parameters(b)
                same = len(pa) == len(pb) and all(
                    np.array_equal(x, y) for x, y in zip(pa, pb, strict=True)
                )
                verdicts.append(f"`{name}` {'same parameters' if same else 'differs'}")
            else:
                diff = image_difference(a, b)
                verdicts.append(
                    f"`{name}` " + ("identical data" if diff == 0 else f"differs (max abs {diff})")
                )
        lines.append(f"- `{node}`: " + "; ".join(verdicts))
    return lines


def steps_section(run1: Path, run2: Path) -> list[str]:
    lines = [
        "## 2. Steps",
        "",
        "Every NIfTI file in run 1's work directory, compared with run 2's.",
        "",
        "| File | Result |",
        "|---|---|",
    ]
    w1, w2 = run1 / "work", run2 / "work"
    for a in nifti_files(w1):
        rel = a.relative_to(w1)
        b = w2 / rel
        if not b.exists():
            result = "missing in run 2"
        else:
            diff = image_difference(a, b)
            result = (
                "shape or affine differ"
                if diff is None
                else "identical"
                if diff == 0
                else f"max abs diff {diff:.3g}"
            )
        lines.append(f"| `{rel}` | {result} |")
    return lines


def flatten(d: dict, prefix: str = "") -> dict[str, float]:
    out = {}
    for key, value in d.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flatten(value, f"{name}."))
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            out[name] = float(value)
    return out


def iqm_section(run1: Path, run2: Path) -> list[str]:
    (j1,) = sorted((run1 / "out").rglob("sub-*_T1w.json"))
    j2 = run2 / "out" / j1.relative_to(run1 / "out")
    v1 = flatten(json.loads(j1.read_text()))
    v2 = flatten(json.loads(j2.read_text()))
    lines = [
        "## 3. Noise floor (#8)",
        "",
        f"Relative difference |run 2 - run 1| / |run 1| of each IQM in `{j1.name}`.",
        "",
        "| IQM | Run 1 | Run 2 | Relative difference |",
        "|---|---|---|---|",
    ]
    for key in sorted(v1):
        if key not in v2:
            lines.append(f"| `{key}` | {v1[key]:.6g} | missing | |")
            continue
        rel = abs(v2[key] - v1[key]) / abs(v1[key]) if v1[key] else abs(v2[key] - v1[key])
        lines.append(f"| `{key}` | {v1[key]:.6g} | {v2[key]:.6g} | {rel:.2e} |")
    return lines


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("run1", type=Path)
    parser.add_argument("run2", type=Path)
    args = parser.parse_args()

    lines = ["# Baseline runs compared", ""] + seed_section(args.run1, args.run2)
    lines += [""] + steps_section(args.run1, args.run2)
    lines += [""] + iqm_section(args.run1, args.run2)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
