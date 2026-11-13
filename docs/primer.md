# Primer: MRIQC, nipype and Flyte 2

Read this before starting any issue. It gives you the vocabulary and the overall picture; each
issue then points to the exact lines of code involved. No neuroscience background is assumed.

## 1. What MRIQC does

[MRIQC](https://mriqc.readthedocs.io) takes MRI scans organised in the
[BIDS](https://bids-specification.readthedocs.io) folder structure. For every scan it computes
**image quality metrics (IQMs)**, numbers such as the signal-to-noise ratio, and writes them to a
one-row table (`+iqms.parquet`, with a `+iqms.json` sidecar for the metadata) next to an HTML
visual report. Researchers use these to spot bad scans before analysing them.

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
([`mriqc/workflows/anatomical/base.py:77`](https://github.com/nipreps/mriqc/blob/062b0d1762293876be1e9555b7985e3ec6ff9d99/mriqc/workflows/anatomical/base.py#L77)).

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
   Written to a parquet table, with the BIDS metadata and the provenance in its JSON sidecar.
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
- Each node runs in its own working directory. In MRIQC's work folder that is
  `<work>/mriqc_wf/anatMRIQC/<sub-workflow>/<iterables folder>/<node>/`: the sub-workflows
  nest (`synthstrip_wf`), and the *iterables folder*, one per input, is named from the input's
  entities, path and metadata. `find <work> -type d -name <node>` finds a node's folder.
- After running, nipype saves the node's inputs and outputs to `result_<node>.pklz` in that
  folder, with absolute paths. Loading one checks that those files exist, so load it where it
  was written: the baseline you will compare against is a collection of these folders, made
  under `/baseline`, and mounted there.
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
- **Local mode** (`flyte run --local file.py main`) runs everything in one Python process.
  Container images and resource requests are ignored there. This is how you develop and test.
  `flyte run` prints the outputs as `ActionOutputs(o0=...)`, and from Python,
  `flyte.run(task, ...).outputs()` is a tuple: take `[0]`. Making a `File` outside a task
  (in a test) needs `flyte.init()` first. A `bool` input is a flag: `--debug`, not
  `--debug true`.
- **Fan-out and fan-in**: `asyncio.gather(...)` or `flyte.map(task, items)` starts one child
  task per item (the fan-out); the code that uses their results is the fan-in. This replaces
  both MapNode and iterables.
- **The event loop**: an `async` task runs on Python's event loop, and in local mode all tasks
  share one. A task whose body blocks (a program call, a nipype interface) holds the loop until
  it returns, so the children of a `gather` run one after another locally; on a cluster each
  runs in its own container. That is expected, and it keeps nipype safe: nipype changes the
  working directory of the whole process, so never run an interface in a thread
  (`asyncio.to_thread`, or a plain `def` task, which Flyte runs in a thread).
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

### Settings are inputs

MRIQC keeps its options in `mriqc.config`, a module of classes (`config.execution`,
`config.workflow`, `config.nipype`, `config.seeds`, ...) whose attributes the command line fills
in before the graph is built. The workflow code reads them while it builds the graph, for
example `flavor=['testing', 'fast'][config.execution.debug]`, and some interfaces read them
while they run. This works because MRIQC builds and runs everything in processes that loaded
the same config file.

A Flyte task can run in a fresh container, on another machine. It gets its inputs and nothing
else: a value set in `mriqc.config` by the parent never reaches it. So the port follows one
rule: **every setting that changes an output is a task input.**
- `AnatSettings` ([#20](https://github.com/nipreps/mriqc-flyte/issues/20)) holds those
  settings, one field per `mriqc.config` key, with the key named in each field's docstring.
  `AnatSettings.from_mriqc_config()` builds one from a configured MRIQC, which is how the port
  and MRIQC can be run with the same options.
- Parent tasks receive the whole `AnatSettings`. A leaf task receives only the plain values it
  needs (`omp_nthreads: int`, `seed: int | None`), so its signature says what changes its
  output, and its test can call it without building settings.
- Settings that only say *how* to run (`nprocs`, the plugin, the work folder) are not ported:
  Flyte decides how tasks run.
- Random seeds are settings too. MRIQC draws an ANTs seed and a NumPy seed from
  `--random-seed` (`config.seeds`); `AnatSettings` draws them the same way, and passes each to
  the tasks that use it.
- Some MRIQC interfaces log through `config.loggers`, which MRIQC sets up in its own processes
  only. `run_interface()` sets them up before running an MRIQC interface.

## 8. How the port is organised

Each piece of MRIQC becomes **two layers**:
1. **`_impl` function:** plain Python with no Flyte types. It takes local paths and a working
   directory, runs the MRIQC interface through `run_interface()`, and returns paths or numbers.
   Unit tests call it directly on baseline files. Stage 2 rewrites only this layer.
2. **Task:** a thin `@env.task` that downloads its `File` inputs, calls the `_impl` function,
   and uploads the results.

Import MRIQC, niworkflows and nipype inside the `_impl` function, not at the top of the module.
Importing them takes a second or more and loads nipype's config; inside the `_impl`, only the
code that runs the step pays for it, and the task layer stays free of MRIQC for stage 2.

Planned modules (each one is created by an issue):

```
src/mriqc_flyte/
  env.py        TaskEnvironment definitions
  _helpers.py   run_interface(), localize(), upload(), working-directory handling
  types.py      AnatInput and the result dataclasses passed between tasks
  settings.py   AnatSettings (replaces reads of mriqc.config)
  testing.py    comparators (images, masks, IQM files) and the baseline loader
  shared.py     tasks used by several workflows (skull-stripping)
  anat.py       sMRI tasks and the anat_qc parent task
  main.py       entry task looping over all inputs
```

## 9. Checking that the port is correct

Correctness means **parity with MRIQC**: for the same input and settings, the port must produce
the same IQM file.
- Before the project, the supervisors ran MRIQC twice on the same T1w image and published both
  work directories (the **baseline**), for each platform (`amd64`, `arm64`). The environment
  variable `MRIQC_FLYTE_BASELINE` points to it.
- Some steps draw random numbers (registration, the head mask, Atropos). MRIQC ran with
  `--random-seed 42`, which seeds them all, so its two runs are identical, and the port, run
  with the same seed, gives the same numbers.
- Per-step tests take their inputs from the baseline, not from your own upstream tasks. That way
  each issue can be tested on its own. Each compares with a small margin, set per step with its
  reason next to it: the result must survive a rebuilt image (another compiler or library
  version), not only the pinned one.
- The end-to-end tests compare the IQM files exactly, in the pinned image, with the baseline of
  the same platform: MRIQC's numbers differ slightly between `amd64` and `arm64`.
- When a test passes in the container but fails on GitHub Actions, read the log of the failed
  job first, then compare the package versions (`pip list` in both) before changing the code.

## 10. Reading list
- Flyte 2 user guide: <https://www.union.ai/docs/v2/flyte/user-guide/>
  (sections *Tasks*, *Files and directories*, *Run modes*).
- nipype interfaces tutorial: <https://miykael.github.io/nipype_tutorial/notebooks/basic_interfaces.html>
- MRIQC documentation, *Workflows* and *IQMs* pages: <https://mriqc.readthedocs.io>
- BIDS starter kit: <https://bids-standard.github.io/bids-starter-kit/>
- Python `asyncio` basics: <https://docs.python.org/3/library/asyncio-task.html>
