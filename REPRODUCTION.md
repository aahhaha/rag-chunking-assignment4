# Reproduction evidence

Repository: https://github.com/aahhaha/rag-chunking-assignment4

The student successfully ran `assignment4/analyse.py` on 27 October 2026 and supplied its console output. The Codex assistant also checked all six main binary pairwise p-values against `scipy.stats.binomtest`; see `reproduction/statistics_check.log`.

A full 500-question, three-condition inference rerun was started by the Codex AI assistant on the student's computer on 27 October 2026. Its final status, actual duration, Python details and input hashes are recorded in `reproduction/environment.json` when present. Do not infer success from the existence of a start log. `status=completed` and the comparison file are required to establish completion.

This rerun uses the existing `venv` and locally cached models. It is not an independent classmate test and not a clean-environment installation. It must not be described as satisfying those separate course requirements without instructor approval. It cannot establish that the original protocol was registered before results were seen.

## Commands

From the repository root, in an environment containing the inference dependencies:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:OMP_NUM_THREADS='4'
$env:MKL_NUM_THREADS='4'
$env:TOKENIZERS_PARALLELISM='false'
python -u reproduction/run_reproduction.py *> reproduction/full_run.log
python reproduction/compare_reproduction.py
```

Offline mode requires both models to be cached already. For a first download, omit the two offline variables and obtain the models normally. The wrapper imports the unchanged experiment script, runs the original 500-question configuration, and adds progress/environment logging. Four CPU threads are recorded as a computational setting; all three methods share it. No dataset, splitter, prompt or decoding parameter is changed. Outputs go to `reproduction/rerun_main.csv`, preserving the historical results.

## Evidence files

- `environment.json`: operator, environment, timestamps, input hashes, completion status and duration.
- `requirements-inference-observed.txt`: actual packages in the rerun environment. This is an observed environment snapshot, not proof that installation succeeds in a fresh environment.
- `full_run.log`: stdout and stderr from full model inference.
- `progress.json`: progress only, not evidence of completion.
- `rerun_main.csv`: newly generated predictions and metrics, available after completion.
- `comparison.json`: paired comparison with original saved outputs, available after the comparison command succeeds.
- `statistics_check.log`: independent SciPy verification of the six exact main paired p-values.

The comparison checks method/question keys, per-item metrics and predictions. Numerical differences must be retained and explained rather than overwritten. The original report outcomes remain historical results unless explicitly revised and documented.

## Clean saved-output analysis check

The assistant also created a fresh Python 3.12 environment, installed requirements-analysis.txt and reran analyse.py. The summary matched byte for byte. See clean_analysis_check.json, clean_analysis_install.log and clean_analysis_run.log. This check covers only analysis dependencies; the full inference rerun still uses the existing environment.
