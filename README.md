# Assignment 4 reproduction package

This package reanalyses saved RAG chunking experiments. It does not claim a new unseen evaluation or an independently verified full inference rerun.

## Contents

- `run_experiment.py`: original inference pipeline.
- `dev-v1.1.json`: original SQuAD v1.1 dev file; source https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json
- `results_main.csv`: 500 questions per condition.
- `results_budget1500.csv`: first 300 sampled questions per condition with 1,500-character context cap.
- `results.csv`: 100-question pilot per condition.
- `semantic_visibility.py` and `.json`: historical embedding-window diagnostic.
- `assignment4/analyse.py`: regenerate numerical tables, exact paired tests, CIs, matched comparison, figures, and hashes.
- `assignment4/build_report.py` and `report.md`: regenerate the DOCX from analysis outputs.
- `assignment4/error_review.json`: 30 reviewed failure examples with original question IDs; AI-assisted labels need student verification.
- `Assignment4_AibynSamat_Final.docx`: report.

## Reproduce saved-output analysis

Use Python 3.11 or newer in a new environment. The lightweight analysis does not need the inference models or SciPy.

```powershell
py -3 -m venv .venv-a4
.\.venv-a4\Scripts\python.exe -m pip install -r requirements-analysis.txt
.\.venv-a4\Scripts\python.exe assignment4/analyse.py
.\.venv-a4\Scripts\python.exe assignment4/build_report.py
```

The figure script uses Windows Arial at `C:/Windows/Fonts/arial.ttf`. For another OS, replace that font path with a local Arial-compatible font. Numerical calculations do not depend on the font. `build_report.py` expects error_candidates.json, included in this package. No inference is performed by either command.

Check SHA-256 values against `assignment4/analysis.json`. The script asserts identical question IDs across conditions and that the budget sample is exactly the first 300 main-run IDs. Bootstrap: NumPy default_rng seed 0, 2,000 resamples, percentile 2.5 and 97.5. McNemar: exact two-sided binomial tail over discordant pairs; Holm separately within each binary metric.

## Full experiment

The original script requires langchain-core, langchain-text-splitters, langchain-experimental, langchain-community, langchain-huggingface, faiss-cpu, numpy, scipy, sentence-transformers, transformers and torch. These models must be downloaded: `sentence-transformers/all-MiniLM-L6-v2` and `google/flan-t5-base`. Network access is needed for initial downloads. CPU execution can be slow.

```powershell
python run_experiment.py --n-questions 500 --embedder minilm --seed 42 --out rerun_main.csv
python run_experiment.py --n-questions 300 --embedder minilm --seed 42 --ctx-budget 1500 --out rerun_budget1500.csv
python semantic_visibility.py --squad dev-v1.1.json --results rerun_main.csv --out rerun_visibility.json
```

Use distinct output paths to preserve historical results. Fake embeddings are smoke-test utilities and must never be reported as real experimental results. The original environment was not exported; Assignment 3's listed versions are historical claims, not a verified lockfile. Model revision identifiers and historical runtime/hardware records are missing. A fully pinned inference environment still needs an actual clean-environment test. Do not interpret the lightweight requirements file as the inference environment.

## Independent reproduction record and remaining submission steps

1. Student checks the report, AI disclosure and all 30 qualitative labels; compare the three discussion sources against the actual Assignment 1 bibliography.
2. Confirm whether a real prior Moodle protocol upload exists. Never backdate it. If absent, discuss the retrospective study with the instructor.
3. Resolve the AI-track requirement for three seeds or CV versus the deterministic-run CI option with the instructor. The report explicitly declares the single configuration.
4. Have a classmate install and run the full pipeline in a clean environment, and fill Appendix C with their real name, date, hardware, logs and result differences.
5. Publish only the intended package files to a chosen GitHub/GitLab repository, add its URL to the report, and create the real `assignment-4` release/tag. No repository has been published by this preparation step.
6. Open the DOCX in Word and check every page before submitting. The packaged renderer could not run locally because soffice.exe is unavailable; page layout has not been visually verified.

## Licence

The new analysis and document-building scripts are supplied under the MIT licence in LICENSE_Assignment4.txt. The pre-existing experiment scripts, SQuAD/Wikipedia data, and cited publications retain their original rights and licences. The MIT grant does not relicense those materials. Preserve SQuAD attribution and review its upstream licence before public redistribution.

## Defence guide

See Assignment4_Defence_Guide_RU.md for the research explanation, code walkthrough, statistical interpretation, commands, numerical provenance and pending requirements.
