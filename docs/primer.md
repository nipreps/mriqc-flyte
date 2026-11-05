# Primer: MRIQC, nipype and Flyte 2

Read this before starting any issue. It gives you the vocabulary and the overall picture; each
issue then points to the exact lines of code involved. No neuroscience background is assumed.

## 1. What MRIQC does

[MRIQC](https://mriqc.readthedocs.io) takes MRI scans organised in the
[BIDS](https://bids-specification.readthedocs.io) folder structure. For every scan it computes
**image quality metrics (IQMs)**, numbers such as the signal-to-noise ratio, and writes them to a
JSON file next to an HTML visual report. Researchers use these to spot bad scans before analysing
them.

MRIQC has three workflows, one per kind of scan:

| Workflow | Input | Typical size | What it measures |
|---|---|---|---|
| **sMRI** (structural, `anatomical`) | T1w or T2w image, 3D | 10-30 MB | Noise, contrast, smoothness, artefacts |
| **fMRI** (functional) | BOLD series, 4D (one 3D volume every ~2 s) | 50-500 MB | All of the above, plus head motion and signal stability over time |
| **dMRI** (diffusion) | DWI series, 4D, plus gradient tables | 100 MB-1 GB | Noise, motion, and diffusion model fit quality |

The port starts with **sMRI**: it is the smallest graph, and it only produces scalar IQMs, which
makes it easy to check that the port gives the same answers as MRIQC.

## 2. Glossary

- **NIfTI (`.nii.gz`)**: the file format for MRI volumes. A 3D array of *voxels* (3D pixels)
  plus an affine matrix that places the array in physical space (millimetres). Read it with
  `nibabel`.
- **T1w / T2w**: two kinds of structural scan with different contrast between tissues.
- **Mask**: a binary image (0/1) of the same shape as the scan, marking a region such as the
  brain or the head.
- **Bias field (intensity non-uniformity, INU)**: a smooth, slowly varying brightness gradient
  that the scanner adds to the image. **N4** (from ANTs) estimates and removes it.
- **Skull-stripping (brain extraction)**: computing a brain mask. MRIQC uses **SynthStrip**, a
  neural network (PyTorch).
- **Template**: an average brain in a standard coordinate space (MNI). MRIQC downloads
  templates from **TemplateFlow** (`templateflow.api.get`).
- **Registration (spatial normalisation)**: estimating the transform that aligns the subject's
  image with the template. Its output is a *transform file*, not an image.
- **Tissue probability maps (TPMs)**: template images giving, per voxel, the probability of
  each tissue: **CSF** (cerebrospinal fluid), **GM** (grey matter) and **WM** (white matter).
  MRIQC always orders them CSF, GM, WM.
- **Segmentation**: labelling each voxel as CSF, GM or WM. MRIQC uses ANTs **Atropos**, with the
  TPMs as priors.
- **Air mask / hat mask**: the background around the head, where only noise should be. Many
  IQMs compare the signal inside the head with the noise in the air.
- **FWHM**: full width at half maximum, a measure of image smoothness (AFNI `3dFWHMx`).
- **Reportlet**: one SVG figure of the HTML report.
- **Head motion, framewise displacement (FD)**: fMRI and dMRI only. How much the head moved
  between volumes.
- **Multi-echo**: fMRI acquired at several echo times at once. One "run" is then a list of files.

## 3. The sMRI workflow, step by step

Defined in `anat_qc_workflow`
([`mriqc/workflows/anatomical/base.py:77`](https://github.com/nipreps/mriqc/blob/d5cb0c82ba4004f78b9fe982450397907436bb55/mriqc/workflows/anatomical/base.py#L77)).

1. **Conform**: reorient the image to a standard axis order (RAS).
2. **Skull-strip** (`synthstrip_wf`, in `mriqc/workflows/shared.py`):
   1. clip extreme intensities;
   2. run N4;
   3. run SynthStrip to get the brain mask;
   4. run N4 again, weighted by the mask, keeping the bias field.
3. **Spatial normalisation**: register the image to the MNI template, then bring the template's
   TPMs back into the subject's space.
4. **Head mask**: enhance and threshold the image gradient to find the head.
5. **Air masks**: three masks of the background around the head.
   - The *hat*: the air around the upper part of the head. It is cut below two skull landmarks
     (glabella and inion) mapped from the template, so the face and neck are excluded.
   - The *artefact* mask: voxels in the hat that are too bright to be pure noise.
   - The *air* mask: the hat without the artefacts.
6. **Tissue segmentation**: Atropos, with the subject-space TPMs as priors.
7. **IQMs**: smoothness (FWHM), QI2, and the structural measures (SNR, CNR, CJV, EFC, ...).
   Written to a JSON file with provenance information.
8. **Report**: mosaic figures (reportlets), assembled into HTML after the graph has run.

The fMRI workflow adds head-motion correction, temporal statistics and a "carpet" plot. The
dMRI workflow adds gradient-table handling, denoising and tensor model fits. Both reuse the
skull-stripping step.

## 4. Tools you will meet

| Tool | Kind | Used for |
|---|---|---|
| ANTs (`N4BiasFieldCorrection`, `antsRegistration`, `antsApplyTransforms`, `Atropos`) | C++ command-line programs | Bias field, registration, resampling, segmentation |
| AFNI (`3dFWHMx`; for fMRI `3dvolreg`, `3dTstat`, `3dToutcount`, `3dTqual`) | C command-line programs | Smoothness, motion correction, time statistics |
| SynthStrip | Python + PyTorch (bundled in MRIQC) | Brain mask |
| MRtrix3 `dwidenoise`, dipy | C++ program, Python library | dMRI only |
| nibabel, numpy, scipy, scikit-learn | Python | Everything else |

All of these are installed in the **dev container**. Do not try to install ANTs or AFNI on your
laptop.

## 5. nipype in brief

[nipype](https://nipype.readthedocs.io) wraps each tool in an **Interface** class with typed
inputs and outputs. A **Node** puts an interface into a graph, and a **Workflow** connects nodes:

```python
n4 = pe.Node(N4BiasFieldCorrection(dimension=3), name="pre_n4")
wf.connect([(clip, n4, [("out_file", "input_image")])])
```

What you need to know:
- Each node runs in its own working directory, `<work_dir>/<workflow>/<node>/`. After running,
  nipype saves the node's outputs to `result_<node>.pklz` in that directory. The baseline data
  you will compare against is a collection of these folders.
- You can run any interface outside a workflow: `N4BiasFieldCorrection(...).run(cwd=some_dir)`.
  The port relies on this in stage 1.
- **MapNode**: runs the same interface over a list of inputs.
- **iterables**: duplicates a whole sub-graph once per input, which is how MRIQC processes many
  scans.
- **Function**: wraps a plain Python function as an interface.
- **IdentityInterface**: a node that only passes values through (`inputnode`, `outputnode`).

## 6. Flyte 2 in brief

[Flyte 2](https://www.union.ai/docs/v2/flyte/) has no graph language. A workflow is a Python
function that calls other functions:

```python
env = flyte.TaskEnvironment(name="anat")


@env.task
async def n4(in_file: File) -> File: ...


@env.task
async def main(t1ws: list[File]) -> list[File]:
    return list(await asyncio.gather(*(n4(f) for f in t1ws)))
```

What you need to know:
- **Tasks** are `async` functions decorated with `@env.task`. Inputs and outputs must have type
  hints: `int`, `str`, dataclasses, `flyte.io.File`, lists of those.
- **`File`** is a handle on a file. Inside a task, `await f.download()` gives a local path, and
  `await File.from_local(path)` turns a path back into a handle.
- **Local mode** (`flyte run --local file.py main`) runs everything in one Python process, one
  task at a time. Container images and resource requests are ignored there. This is how you
  develop and test.
- **Fan-out**: `asyncio.gather(...)` or `flyte.map(task, items)`. This replaces both MapNode and
  iterables.
- **Caching**: `@env.task(cache="auto")` skips a task whose inputs have not changed. In local
  mode the cache key is the file *location*, not its content, so keep caching off while
  developing.

## 7. How nipype concepts map to Flyte

| nipype | Flyte 2 (this port) |
|---|---|
| `Node(Interface)` | One task (or part of one) that runs the interface |
| `Workflow` | A parent task that calls child tasks |
| `connect()` | Passing a return value as an argument |
| Connect-function `(("out_file", _pop), "in_file")` | Plain Python, e.g. `files[0]` |
| `MapNode`, `iterables` | `asyncio.gather` or `flyte.map` |
| `IdentityInterface` | Nothing (function arguments) |
| `mem_gb`, `n_procs` | `flyte.Resources` on the `TaskEnvironment` |
| Global `mriqc.config` | A frozen `AnatSettings` dataclass passed to parent tasks |

## 8. How the port is organised

Each piece of MRIQC becomes **two layers**:
1. **`_impl` function:** plain Python with no Flyte types. It takes local paths and a working
   directory, runs the MRIQC interface through `run_interface()`, and returns paths or numbers.
   Unit tests call it directly on baseline files. Stage 2 rewrites only this layer.
2. **Task:** a thin `@env.task` that downloads its `File` inputs, calls the `_impl` function,
   and uploads the results.

Planned modules (each one is created by an issue):

```
src/mriqc_flyte/
  env.py        TaskEnvironment definitions
  _helpers.py   run_interface(), localize(), upload(), working-directory handling
  types.py      AnatInput and the result dataclasses passed between tasks
  settings.py   AnatSettings (replaces reads of mriqc.config)
  testing.py    comparators (images, masks, IQM JSON) and the baseline loader
  shared.py     tasks used by several workflows (skull-stripping)
  anat.py       sMRI tasks and the anat_qc parent task
  main.py       entry task looping over all inputs
```

## 9. Checking that the port is correct

Correctness means **parity with MRIQC**: for the same input, the port must produce the same
IQMs, within a tolerance.
- Before the project, the supervisors ran MRIQC twice on the same T1w image and published both
  work directories (the **baseline**). The environment variable `MRIQC_FLYTE_BASELINE` points to
  it.
- Some steps use random numbers (registration, Atropos), so even MRIQC does not give identical
  numbers twice. The difference between the two baseline runs is the **noise floor**. Your port
  is correct when its difference from run 1 is no larger than that.
- Per-step tests take their inputs from the baseline, not from your own upstream tasks. That way
  each issue can be tested on its own.

## 10. Reading list
- Flyte 2 user guide: <https://www.union.ai/docs/v2/flyte/user-guide/>
  (sections *Tasks*, *Files and directories*, *Run modes*).
- nipype interfaces tutorial: <https://miykael.github.io/nipype_tutorial/notebooks/basic_interfaces.html>
- MRIQC documentation, *Workflows* and *IQMs* pages: <https://mriqc.readthedocs.io>
- BIDS starter kit: <https://bids-standard.github.io/bids-starter-kit/>
- Python `asyncio` basics: <https://docs.python.org/3/library/asyncio-task.html>
