# Reproduction record

## Recorded checks

1. The student ran `assignment4/analyse.py` on 27 October 2026.
2. The assistant independently checked six main exact McNemar p-values against `scipy.stats.binomtest`.
3. The assistant installed the analysis requirements in a new Python 3.12 environment, reran analysis, and obtained a byte-identical `main_summary.csv`.
4. The Codex AI assistant performed a full 500-question-per-method inference rerun on the student computer on 27 October 2026, using the existing Python 3.11 environment and cached models. All 1,500 predictions and numerical outcomes matched. Duration: 3,887.93 seconds.

The full inference rerun was not performed by an independently verified classmate and did not install the full model environment from scratch. The student reported instructor acceptance of this alternative on 2 November 2026. See `instructor_acceptance.json`; no exact date of the instructor conversation or signed approval is asserted.

## Evidence

| File in reproduction/ | Evidence |
|---|---|
| `environment.json` | Original operator, timestamps, machine, input hashes and completed status |
| `requirements-inference-observed.txt` | Actual installed inference environment; not a clean-install guarantee |
| `hardware.json` | CPU model and logical processors |
| `full_run.log` | Raw output, progress, chunk counts, scores and tests |
| `rerun_main.csv` | New inference outputs from the recorded run |
| `comparison.json` and `.log` | Per-item comparison with the historical main run |
| `statistics_check.log` | Six exact tests matched SciPy |
| `clean_analysis_check.json` | Separate clean saved-output analysis check |
| `clean_analysis_install.log` and `clean_analysis_run.log` | Installation and execution of the analysis check |
| `instructor_acceptance.json` | Student-reported course approval, recorded separately from historical logs |

`progress.json` records progress only and is not evidence of successful completion on its own. Read `status=completed` in environment.json and the comparison results together.

## Safe future checks

Use the commands in README.md. `run_reproduction.py` requires the actual operator name and writes to a new folder by default. `compare_reproduction.py` accepts explicit input/output paths; it preserves the historical comparison.json. These helpers were updated for safe future use on 2 November 2026. The historical logs predate that maintenance change and remain unchanged.

Offline model loading can be enabled with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1 once both models are cached. Four Torch/OMP/MKL threads were used for every condition in the recorded rerun. The original dataset, splitters, prompt, sampling seed and greedy decoding remain unchanged. No new model experiment was performed during the 2 November report review.
