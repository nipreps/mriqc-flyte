# Roadmap

Generated from the issue drafts; do not edit by hand. Each row is one GitHub issue.
Weeks: W1 = Nov 23-27, W2 = Nov 30-Dec 4, W3 = Dec 7-11, W4 = Dec 14-15 (2026).

| Tier | Hours | Issues |
|---|---|---|
| prep | 9 | 3 |
| core | 152 | 51 |
| stretch | 40.5 | 14 |
| later | 255.5 | 95 |

Core hours per week: W1 48.5 h, W2 41.5 h, W3 44 h, W4 18 h

## Prep

| ID | Week | Area | Title | Hours | Blocked by |
|---|---|---|---|---|---|
| P-01 | W0 | prep | Build and publish the development container | 4 |  |
| P-02 | W0 | prep | Check that ANTs honours a fixed random seed | 2 | P-01 |
| P-03 | W0 | prep | Run and publish the nipype baseline for the test T1w | 3 | P-01, P-02 |

## Core

| ID | Week | Area | Title | Hours | Blocked by |
|---|---|---|---|---|---|
| M-01 | W1 | meta | Weekly status reports | 4 |  |
| O-01 | W1 | onboarding | Run standard MRIQC on the test T1w image | 3 | P-01 |
| O-02 | W1 | onboarding | List the sMRI nodes and their connections from MRIQC's graph | 4 | O-01 |
| O-03 | W1 | onboarding | Write and run a Flyte 2 hello-world task | 3 | P-01 |
| O-04 | W1 | onboarding | Run a command-line program inside a Flyte task | 4 | O-09, O-01 |
| O-05 | W1 | onboarding | Check that plain values and files survive a Flyte run | 3.5 | O-03 |
| O-06 | W1 | onboarding | Load a nipype result file from the baseline | 2 | P-03, O-07 |
| O-07 | W1 | onboarding | Read MRIQC's outputs and its work folder | 3 | O-01 |
| O-08 | W1 | onboarding | Add each node's interface, package and inputs from the code | 4 | O-02 |
| O-09 | W1 | onboarding | Fan the hello world out with asyncio.gather, and test it | 3 | O-03 |
| O-10 | W1 | onboarding | Check that dataclasses and BIDS metadata survive a Flyte run | 3.5 | O-05 |
| S-01 | W1 | scaffold | Create the package modules and the task environment | 1.5 | O-03 |
| S-02 | W1 | scaffold | Define the AnatInput dataclass, and pass it through a task | 3 | S-01, O-10 |
| S-03 | W1 | scaffold | Define AnatSettings to replace the global MRIQC config | 4 | S-01 |
| S-08 | W1 | scaffold | Build an AnatInput from a BIDS file | 3 | S-02, O-06 |
| A-01 | W2 | smri | Port the image conforming step to a task | 1.5 | S-09, S-05, S-10, S-11 |
| A-02 | W2 | smri | Port the intensity clipping to a task | 1.5 | S-09, S-05, S-10, S-11 |
| A-03 | W2 | smri | Port the first N4 bias-field correction to a task | 3.5 | S-09, S-05, S-10, S-11 |
| A-04 | W2 | smri | Port the SynthStrip brain extraction to a task | 3 | S-09, S-05, S-10, S-11, A-03 |
| A-05 | W2 | smri | Port the mask-weighted N4 correction to a task | 2 | S-09, S-05, S-10, S-11 |
| A-06 | W2 | smri | Chain the skull-stripping steps in a parent task | 2 | A-02, A-03, A-04, A-05 |
| A-07 | W2 | smri | Port the registration to the MNI template to a task | 4 | S-09, S-05, S-10, S-11 |
| S-04 | W2 | scaffold | Write run_interface() and new_workdir() | 3 | S-01, O-04 |
| S-05 | W2 | scaffold | Write the localize() and upload() helpers | 4 | S-04, O-05, O-04 |
| S-06 | W2 | scaffold | Write the baseline loader | 3 | S-01, O-06 |
| S-07 | W2 | scaffold | Write the image and mask comparators | 4 | S-01 |
| S-09 | W2 | scaffold | Keep nipype's side effects inside run_interface() | 3 | S-04 |
| S-10 | W2 | scaffold | Skip the baseline and binaries tests when their requirement is missing | 3 | S-06 |
| S-11 | W2 | scaffold | Write the IQM comparators and the tolerance table | 4 | S-07 |
| A-08 | W3 | smri | Project the template tissue maps into subject space | 4 | S-09, S-05, S-10, S-11 |
| A-09 | W3 | smri | Chain registration and map projection in a parent task | 3 | S-03, A-22, A-08 |
| A-10 | W3 | smri | Port the head mask computation to a task | 4 | S-09, S-05, S-10, S-11 |
| A-11 | W3 | smri | Port the air, hat and artefact masks to a task | 3 | S-09, S-05, S-10, S-11 |
| A-12 | W3 | smri | Port the Atropos tissue segmentation to a task | 3.5 | S-09, S-05, S-10, S-11 |
| A-13 | W3 | smri | Port the AFNI smoothness estimate to a task | 2.5 | S-09, S-05, S-10, S-11 |
| A-14 | W3 | smri | Port the QI2 background noise measure to a task | 2 | S-09, S-05, S-10, S-11 |
| A-15 | W3 | smri | Port the intensity harmonisation to a task | 2 | S-09, S-05, S-10, S-11, A-12 |
| A-16 | W3 | smri | Port the provenance and the IQM file writer to a task | 3 | S-08, S-09, S-05, S-10, S-11 |
| A-17 | W3 | smri | Chain the IQM computation in a parent task | 3 | S-08, S-03, A-05, A-11, A-12, A-13, A-14, A-24, A-16 |
| A-18 | W3 | smri | Chain the whole sMRI pipeline in the anat_qc parent task | 3 | S-08, S-03, A-01, A-06, A-09, A-10, A-11, A-12, A-17 |
| A-22 | W3 | smri | Seed the registration and compare it with the baseline | 3 | A-07, A-23, S-03 |
| A-23 | W3 | smri | Measure the difference between two affine transforms | 3 | A-07, S-11 |
| A-24 | W3 | smri | Port the structural IQMs to a task | 3 | A-15, A-11, A-12, A-13 |
| A-25 | W3 | smri | Check the IQM parent task's wiring on GitHub Actions | 2 | A-17 |
| A-19 | W4 | smri | Select a BIDS dataset's structural scans as MRIQC does | 2 | S-08 |
| A-20 | W4 | smri | Write the script that makes the sMRI parity table | 3 | A-27 |
| A-21 | W4 | smri | Document how to run the sMRI port in the README | 3 | A-27 |
| A-26 | W4 | smri | Check anat_qc's wiring and seeds on GitHub Actions | 1.5 | A-18, A-25 |
| A-27 | W4 | smri | Run anat_qc over every scan, and write the IQM files where MRIQC does | 3 | A-19, A-18 |
| A-28 | W4 | smri | Write the sMRI parity report page | 4 | A-20 |
| A-29 | W4 | smri | List the messages to ignore and the differences from MRIQC in the README | 1.5 | A-21 |

## Stretch

| ID | Week | Area | Title | Hours | Blocked by |
|---|---|---|---|---|---|
| I-01 | none | integration | Write the anat mosaics task | 2.5 | S-09, S-05, S-10, A-01, A-04 |
| I-02 | none | integration | Write the reportlet sink task | 2 | S-02, S-09, S-05, S-10 |
| I-03 | none | integration | Write the anat_report parent task | 2 | I-01, I-02, A-18 |
| I-04 | none | integration | Build the HTML report via mriqc.reports | 4 | I-03, A-16 |
| I-05 | none | integration | Add the mriqc-flyte CLI entry point | 3 | S-08, S-03, A-27 |
| I-06 | none | integration | Write a caching demo | 2 | A-27 |
| I-07 | none | integration | Compare nipype and Flyte timing on the circle-tests T1w images | 2 | A-27 |
| I-08 | none | integration | Run the port on a T2w image | 3.5 | A-27, A-20 |
| I-09 | none | integration | Write the verbose reportlets | 3.5 | I-03, A-07, A-10, A-11, A-12, A-14 |
| I-10 | none | integration | Write the IQM upload task for the MRIQC web API | 3 | S-03, S-09, S-05, A-16, A-18 |
| I-11 | none | integration | Split the task environments by memory needs | 3 | S-01, A-04, A-07, A-12 |
| I-12 | none | integration | Run the port on FLAIR scans | 4 | I-08 |
| X-01 | none | deployment | Build the Flyte image with Image.from_base | 3 | P-01, S-01 |
| X-02 | none | deployment | Run the sMRI port on a local devbox | 3 | X-01, A-27 |

## Later

| ID | Week | Area | Title | Hours | Blocked by |
|---|---|---|---|---|---|
| D-01 | none | dmri | Run and publish the nipype baseline for one DWI dataset | 4 | P-01, P-02, P-03 |
| D-02 | none | dmri | Define DwiInput and DwiSettings | 3 | S-02, S-03 |
| D-03 | none | dmri | Add the dwi module, its task environment and baseline access | 1.5 | S-01, S-06, D-01, F-03 |
| D-04 | none | dmri | Port the q-space neighbours and the shell detection | 3 | S-04, S-05, S-07, D-03 |
| D-05 | none | dmri | Port the volume extraction and reuse the sanitising task | 2.5 | S-04, S-05, S-07, D-03, F-07 |
| D-06 | none | dmri | Port the b=0 reference and the per-shell average maps | 3 | S-04, S-05, S-07, D-03 |
| D-07 | none | dmri | Check the shared skull-strip and head-motion tasks on DWI | 2.5 | D-02, D-03, A-06, F-05 |
| D-08 | none | dmri | Port the signal drift correction without mriqc.config | 3 | S-04, S-05, S-07, D-03 |
| D-09 | none | dmri | Port the MRtrix3 denoising to a task | 2 | S-04, S-05, S-07, D-03 |
| D-10 | none | dmri | Port the spiking-voxels mask and the PIESNO noise estimate | 2.5 | S-04, S-05, S-07, D-03 |
| D-11 | none | dmri | Port the DTI and DKI model fit to a task | 3 | S-04, S-05, S-07, D-03, D-04 |
| D-12 | none | dmri | Port the corpus callosum segmentation to a task | 2 | S-04, S-05, S-07, D-03, D-11 |
| D-13 | none | dmri | Port the b-vector rotation to a task | 2 | S-04, S-05, S-07, D-03 |
| D-14 | none | dmri | Write the dMRI head-motion parent task | 2.5 | D-07, D-13, F-05, F-06 |
| D-15 | none | dmri | Reuse the EPI to MNI alignment for the DWI reference | 2 | D-02, D-03, F-15 |
| D-16 | none | dmri | Port the noise floor and the diffusion IQMs | 3.5 | S-04, S-05, S-07, D-03, D-04, D-11, D-12, D-14 |
| D-17 | none | dmri | Write the dMRI IQMs and provenance to JSON | 2.5 | D-02, D-04, D-16, A-16 |
| D-18 | none | dmri | Port the FA, MD, background and SNR reportlets | 3.5 | S-04, S-05, D-03, I-01 |
| D-19 | none | dmri | Port the white-matter mask and the FA heatmap reportlet | 2.5 | S-04, S-05, D-03, D-04, I-01 |
| D-20 | none | dmri | Write the dMRI report parent task | 3 | D-18, D-19, I-02 |
| D-21 | none | dmri | Write the dMRI preparation parent task | 3 | D-02, D-04, D-05, D-06, D-07, D-08 |
| D-22 | none | dmri | Write the dMRI model and derivatives parent task | 3.5 | D-09, D-10, D-11, D-12, D-14, D-15, D-21 |
| D-23 | none | dmri | Write the dwi_qc parent task | 2.5 | D-16, D-17, D-20, D-22 |
| D-24 | none | dmri | Add DWI inputs to the main entry task | 2 | D-02, D-23, A-19 |
| D-25 | none | dmri | Check end-to-end dMRI parity with the baseline | 3 | D-01, D-24 |
| D-26 | none | dmri | Write the dMRI parity report | 2 | D-25 |
| F-01 | none | fmri | Run and publish the nipype fMRI baseline for one BOLD run | 4 | P-01, P-02, P-03 |
| F-02 | none | fmri | Define the FuncInput and FuncSettings dataclasses | 3 | S-02, S-03, F-03 |
| F-03 | none | fmri | Add func_env and point the baseline loader at the fMRI baseline | 2 | S-01, S-06, F-01 |
| F-04 | none | fmri | Port the echo selection and non-steady-state detection | 2 | S-04, S-05, S-07, F-03 |
| F-05 | none | fmri | Port the head-motion estimation (3dvolreg) to a shared task | 2.5 | S-04, S-05, S-07, F-03 |
| F-06 | none | fmri | Port the framewise displacement computation to a shared task | 1.5 | S-04, S-05, S-07, F-03 |
| F-07 | none | fmri | Port the image sanitising that drops the dummy volumes | 2 | S-04, S-05, S-07, F-03 |
| F-08 | none | fmri | Port the per-echo realignment with nitransforms | 3 | S-04, S-05, S-07, F-03 |
| F-09 | none | fmri | Write the hmc parent task for the default options | 3 | F-02, F-05, F-06, F-08 |
| F-10 | none | fmri | Port the mean EPI and temporal SNR maps | 2 | S-04, S-05, S-07, F-03 |
| F-11 | none | fmri | Skull-strip the mean EPI with the shared skullstrip task | 1.5 | A-06, F-02, F-03 |
| F-12 | none | fmri | Port the EPI sharpening (N4) to a shared task | 1.5 | S-04, S-05, S-07, F-03 |
| F-13 | none | fmri | Port the EPI to MNI registration to a shared task | 3.5 | S-04, S-05, S-07, F-03, A-07 |
| F-14 | none | fmri | Port the resampling of the carpet segmentation to a shared task | 2 | S-04, S-05, S-07, F-03 |
| F-15 | none | fmri | Write the epi_mni_align parent task in shared.py | 2 | F-12, F-13, F-14 |
| F-16 | none | fmri | Port the DVARS computation to a task | 1.5 | S-04, S-05, S-07, F-03 |
| F-17 | none | fmri | Reuse the FWHM task for the smoothness of the mean EPI | 1.5 | A-13, F-03 |
| F-18 | none | fmri | Port the AFNI outlier, quality index and GCOR measures | 3 | S-04, S-05, S-07, F-03 |
| F-19 | none | fmri | Port the functional IQMs (FunctionalQC) to a task | 3 | S-04, S-05, S-07, F-03 |
| F-20 | none | fmri | Port the timeseries TSV and its sidecar to a task | 2 | S-04, S-05, S-07, F-03 |
| F-21 | none | fmri | Write the fMRI IQM JSON with its provenance | 3 | S-04, S-05, S-07, F-03, A-16 |
| F-22 | none | fmri | Write the compute_func_iqms parent task | 3.5 | F-02, F-16, F-17, F-18, F-19, F-20, F-21 |
| F-23 | none | fmri | Port the background spike series for the carpet plot | 2 | S-04, S-05, S-07, F-03 |
| F-24 | none | fmri | Port the carpet parcellation with its crown mask | 2 | S-04, S-05, S-07, F-03 |
| F-25 | none | fmri | Port the carpet plot (FMRISummary) to a task | 2 | S-04, S-05, F-03 |
| F-26 | none | fmri | Port the four fMRI mosaic reportlets | 2 | S-04, S-05, F-03, I-01 |
| F-27 | none | fmri | Write the func_report parent task | 3 | F-02, F-10, F-22, F-23, F-24, F-25, F-26, I-02 |
| F-28 | none | fmri | Write the fmri_qc parent task for one run | 4 | F-02, F-04, F-07, F-09, F-10, F-11, F-15, F-22, F-27 |
| F-29 | none | fmri | Fan out the fMRI workflow over all runs and echoes | 4 | F-02, F-28, A-19 |
| F-30 | none | fmri | Check end-to-end fMRI parity against the nipype baseline | 3 | S-07, F-01, F-29 |
| F-31 | none | fmri | Write the fMRI parity report | 2 | F-30 |
| F-32 | none | fmri | Add 3dDespike and 3drefit to the development image | 2.5 | P-01, P-02, F-01 |
| F-33 | none | fmri | Port the despike and deoblique options of the hmc task | 3 | F-09, F-28, F-32 |
| F-34 | none | fmri | Port the FFT spike detector option | 3.5 | F-22, F-27 |
| G-01 | none | group | Aggregate the IQM JSON files into group_T1w.tsv | 2 | A-16, A-19 |
| G-02 | none | group | Generate the group HTML report | 2 | G-01 |
| G-03 | none | group | Extend the group outputs to BOLD and DWI | 2 | G-01, G-02 |
| G-04 | none | group | Add the species setting and record a rat baseline | 3.5 | S-03, S-06 |
| G-05 | none | group | Port the rodent brain extraction to a task | 4 | G-04, A-06, A-18 |
| G-06 | none | group | Apply the rodent templates and thresholds in the sMRI tasks | 4 | G-04, A-07, A-08, A-10, A-15 |
| N-01 | none | stage-2 | Vendor MRIQC's anatomical IQM functions without the config import | 3 | S-01 |
| N-02 | none | stage-2 | Write the run_command() helper and a command-line comparator | 2.5 | S-04, S-06 |
| N-03 | none | stage-2 | Rewrite conform and clip_intensity with nibabel only | 2.5 | A-01, A-02 |
| N-04 | none | stage-2 | Build the N4 command line and rewrite n4_pre without nipype | 3 | A-03, N-02 |
| N-05 | none | stage-2 | Rewrite n4_post with the weight image and the bias field output | 2 | A-05, N-04 |
| N-06 | none | stage-2 | Rewrite synthstrip to call MRIQC's bundled SynthStrip program | 2 | A-04, N-02 |
| N-07 | none | stage-2 | Prepare the registration inputs and the initial affine transform | 3 | A-07, N-02 |
| N-08 | none | stage-2 | Build the antsRegistration command line from the JSON presets | 3.5 | N-07 |
| N-09 | none | stage-2 | Run antsRegistration with the preset fallback and draw its report | 3.5 | N-08, N-10 |
| N-10 | none | stage-2 | Rewrite project_tpms with antsApplyTransforms and the header fix | 2 | A-08, N-02 |
| N-11 | none | stage-2 | Rewrite head_mask with vendored functions and a numpy ApplyMask | 2 | A-10 |
| N-12 | none | stage-2 | Rewrite air_masks without the RotationMask and ArtifactMask classes | 3 | A-11, N-01 |
| N-13 | none | stage-2 | Rewrite segment_tissues by calling Atropos directly | 3 | A-12, N-02 |
| N-14 | none | stage-2 | Rewrite estimate_fwhm with 3dFWHMx and its output parsing | 2 | A-13, N-02 |
| N-15 | none | stage-2 | Rewrite compute_qi2 with the vendored art_qi2 function | 1.5 | A-14, N-01 |
| N-16 | none | stage-2 | Rewrite structural_measures as plain functions over the vendored IQMs | 3 | A-15, N-01 |
| N-17 | none | stage-2 | Write the IQM JSON and its provenance without IQMFileSink | 3 | A-16 |
| N-18 | none | stage-2 | Add a CI check that the sMRI path never imports nipype | 2.5 | N-03, N-05, N-06, N-09, N-11, N-12, N-13, N-14, N-15, N-16, N-17 |
| N-19 | none | stage-2 | Make nipype an optional dependency of the sMRI install | 3.5 | N-18 |
| N-20 | none | stage-2 | Rewrite the head-motion estimation by calling 3dvolreg directly | 2 | F-05, D-07, N-02 |
| N-21 | none | stage-2 | Rewrite the EPI to MNI alignment with the sMRI command builders | 3.5 | F-12, F-13, F-14, N-04, N-09, N-10 |
| N-22 | none | stage-2 | Rewrite the AFNI temporal measures with direct program calls | 3.5 | F-10, F-18, N-02 |
| N-23 | none | stage-2 | Rewrite the dMRI denoising by calling MRtrix3 dwidenoise directly | 2 | D-09, N-02 |
| P-04 | none | prep | Deploy a Flyte 2 backend on the Carnaval K3s cluster | 4 |  |
| X-03 | none | deployment | Run the sMRI port on the Carnaval K3s backend | 3 | P-04, X-02 |
| X-04 | none | deployment | Run one participant per sbatch job with Apptainer | 4 | P-01, I-05 |
| X-05 | none | deployment | Evaluate the flyteplugins-slurm connector | 3 | X-03, X-04 |
| X-06 | none | deployment | Measure the object-store traffic of one sMRI run | 3 | X-02 |
| X-07 | none | deployment | Write the HPC deployment guide | 4 | X-02, X-03, X-04, X-05, X-06 |

## Core dependency graph

```mermaid
flowchart LR
  A01["A-01 Port the image conforming step to a task"]
  S09 --> A01
  S05 --> A01
  S10 --> A01
  S11 --> A01
  A02["A-02 Port the intensity clipping to a task"]
  S09 --> A02
  S05 --> A02
  S10 --> A02
  S11 --> A02
  A03["A-03 Port the first N4 bias-field correction to a task"]
  S09 --> A03
  S05 --> A03
  S10 --> A03
  S11 --> A03
  A04["A-04 Port the SynthStrip brain extraction to a task"]
  S09 --> A04
  S05 --> A04
  S10 --> A04
  S11 --> A04
  A03 --> A04
  A05["A-05 Port the mask-weighted N4 correction to a task"]
  S09 --> A05
  S05 --> A05
  S10 --> A05
  S11 --> A05
  A06["A-06 Chain the skull-stripping steps in a parent task"]
  A02 --> A06
  A03 --> A06
  A04 --> A06
  A05 --> A06
  A07["A-07 Port the registration to the MNI template to a task"]
  S09 --> A07
  S05 --> A07
  S10 --> A07
  S11 --> A07
  A08["A-08 Project the template tissue maps into subject space"]
  S09 --> A08
  S05 --> A08
  S10 --> A08
  S11 --> A08
  A09["A-09 Chain registration and map projection in a parent task"]
  S03 --> A09
  A22 --> A09
  A08 --> A09
  A10["A-10 Port the head mask computation to a task"]
  S09 --> A10
  S05 --> A10
  S10 --> A10
  S11 --> A10
  A11["A-11 Port the air, hat and artefact masks to a task"]
  S09 --> A11
  S05 --> A11
  S10 --> A11
  S11 --> A11
  A12["A-12 Port the Atropos tissue segmentation to a task"]
  S09 --> A12
  S05 --> A12
  S10 --> A12
  S11 --> A12
  A13["A-13 Port the AFNI smoothness estimate to a task"]
  S09 --> A13
  S05 --> A13
  S10 --> A13
  S11 --> A13
  A14["A-14 Port the QI2 background noise measure to a task"]
  S09 --> A14
  S05 --> A14
  S10 --> A14
  S11 --> A14
  A15["A-15 Port the intensity harmonisation to a task"]
  S09 --> A15
  S05 --> A15
  S10 --> A15
  S11 --> A15
  A12 --> A15
  A16["A-16 Port the provenance and the IQM file writer to a task"]
  S08 --> A16
  S09 --> A16
  S05 --> A16
  S10 --> A16
  S11 --> A16
  A17["A-17 Chain the IQM computation in a parent task"]
  S08 --> A17
  S03 --> A17
  A05 --> A17
  A11 --> A17
  A12 --> A17
  A13 --> A17
  A14 --> A17
  A24 --> A17
  A16 --> A17
  A18["A-18 Chain the whole sMRI pipeline in the anat_qc parent task"]
  S08 --> A18
  S03 --> A18
  A01 --> A18
  A06 --> A18
  A09 --> A18
  A10 --> A18
  A11 --> A18
  A12 --> A18
  A17 --> A18
  A19["A-19 Select a BIDS dataset's structural scans as MRIQC does"]
  S08 --> A19
  A20["A-20 Write the script that makes the sMRI parity table"]
  A27 --> A20
  A21["A-21 Document how to run the sMRI port in the README"]
  A27 --> A21
  A22["A-22 Seed the registration and compare it with the baseline"]
  A07 --> A22
  A23 --> A22
  S03 --> A22
  A23["A-23 Measure the difference between two affine transforms"]
  A07 --> A23
  S11 --> A23
  A24["A-24 Port the structural IQMs to a task"]
  A15 --> A24
  A11 --> A24
  A12 --> A24
  A13 --> A24
  A25["A-25 Check the IQM parent task's wiring on GitHub Actions"]
  A17 --> A25
  A26["A-26 Check anat_qc's wiring and seeds on GitHub Actions"]
  A18 --> A26
  A25 --> A26
  A27["A-27 Run anat_qc over every scan, and write the IQM files where MRIQC does"]
  A19 --> A27
  A18 --> A27
  A28["A-28 Write the sMRI parity report page"]
  A20 --> A28
  A29["A-29 List the messages to ignore and the differences from MRIQC in the README"]
  A21 --> A29
  M01["M-01 Weekly status reports"]
  O01["O-01 Run standard MRIQC on the test T1w image"]
  P01 --> O01
  O02["O-02 List the sMRI nodes and their connections from MRIQC's graph"]
  O01 --> O02
  O03["O-03 Write and run a Flyte 2 hello-world task"]
  P01 --> O03
  O04["O-04 Run a command-line program inside a Flyte task"]
  O09 --> O04
  O01 --> O04
  O05["O-05 Check that plain values and files survive a Flyte run"]
  O03 --> O05
  O06["O-06 Load a nipype result file from the baseline"]
  P03 --> O06
  O07 --> O06
  O07["O-07 Read MRIQC's outputs and its work folder"]
  O01 --> O07
  O08["O-08 Add each node's interface, package and inputs from the code"]
  O02 --> O08
  O09["O-09 Fan the hello world out with asyncio.gather, and test it"]
  O03 --> O09
  O10["O-10 Check that dataclasses and BIDS metadata survive a Flyte run"]
  O05 --> O10
  P01["P-01 Build and publish the development container"]
  P02["P-02 Check that ANTs honours a fixed random seed"]
  P01 --> P02
  P03["P-03 Run and publish the nipype baseline for the test T1w"]
  P01 --> P03
  P02 --> P03
  S01["S-01 Create the package modules and the task environment"]
  O03 --> S01
  S02["S-02 Define the AnatInput dataclass, and pass it through a task"]
  S01 --> S02
  O10 --> S02
  S03["S-03 Define AnatSettings to replace the global MRIQC config"]
  S01 --> S03
  S04["S-04 Write run_interface() and new_workdir()"]
  S01 --> S04
  O04 --> S04
  S05["S-05 Write the localize() and upload() helpers"]
  S04 --> S05
  O05 --> S05
  O04 --> S05
  S06["S-06 Write the baseline loader"]
  S01 --> S06
  O06 --> S06
  S07["S-07 Write the image and mask comparators"]
  S01 --> S07
  S08["S-08 Build an AnatInput from a BIDS file"]
  S02 --> S08
  O06 --> S08
  S09["S-09 Keep nipype's side effects inside run_interface()"]
  S04 --> S09
  S10["S-10 Skip the baseline and binaries tests when their requirement is missing"]
  S06 --> S10
  S11["S-11 Write the IQM comparators and the tolerance table"]
  S07 --> S11
```
