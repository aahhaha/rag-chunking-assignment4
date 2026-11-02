# RAG chunking comparison for Assignment 4

Student: Aibyn Samat, SE-2415.

This study compares fixed-size, overlapping and percentile-based semantic chunks on the same 500 SQuAD v1.1 development questions. Overlap has the highest Recall@5: 81.8%, compared with 75.2% for fixed-size and 66.4% for semantic. The overlap EM increase is statistically uncertain. Semantic generation is strongly affected by prompt truncation. The report separates these findings from exploratory explanations.

## Submission

- Report: `Assignment4_AibynSamat_Final.docx`
- Original release: `assignment-4`
- Reviewed release: `assignment-4-reviewed`
- Oral preparation: `Assignment4_Defence_Guide_RU.md` and `Defence_Practice_RU.md`
- Reproduction details: `REPRODUCTION.md`
- Repository: https://github.com/aahhaha/rag-chunking-assignment4 (public)

## Course arrangements

On 2 November 2026 the student reported that the instructor accepted reuse and re-examination of the experiments already reported in Assignment 3, and accepted the technical reproduction arrangement for this individual submission. This is recorded in `reproduction/instructor_acceptance.json`. It is not a signed approval record or evidence of a pre-experiment protocol upload. One evaluation sample and one configuration per method were used; no additional seeds or cross-validation are claimed.

## Files

| File | Purpose |
|---|---|
| `run_experiment.py` | Original chunking, embedding, retrieval, generation and scoring pipeline |
| `results_main.csv` | Historical main run, 500 rows per method |
| `results_budget1500.csv` | Exploratory context-budget run, first 300 question IDs per method |
| `results.csv` | Historical pilot, 100 questions per method |
| `dev-v1.1.json` | SQuAD dev data; original source https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json |
| `assignment4/analyse.py` | Summary, bootstrap intervals, paired tests, failure stages and figures |
| `assignment4/build_report.py` | Builds the report from Markdown and saved analysis |
| `assignment4/analysis.json` | Sample IDs, hashes, metric estimates and paired comparisons |
| `assignment4/error_review.json` | Thirty labelled fixed-size EM failures, with source question IDs |
| `semantic_visibility.py` and `.json` | Historical embedding-window diagnostic and saved summary |
| `reproduction/` | Original technical rerun evidence and safe helpers for future checks |
| `Assignment3_AibynSamat.docx` | Prior methodology and historical chunk statistics |

## Recalculate tables and figures

From the repository root, in Python 3.11 or newer:

```powershell
python -m venv .venv-analysis
.\.venv-analysis\Scripts\python.exe -m pip install -r requirements-analysis.txt
.\.venv-analysis\Scripts\python.exe assignment4/analyse.py
.\.venv-analysis\Scripts\python.exe assignment4/build_report.py
```

This uses saved CSVs and does not run the models. In the recorded clean Python 3.12 installation, the regenerated main summary was byte-identical. Fonts are selected automatically for Windows/macOS/Linux. Rendering fonts may differ across systems; numerical calculations do not depend on them.

Bootstrap: 2,000 question-level resamples, NumPy default_rng seed 0, percentile intervals. Binary comparisons use exact McNemar tests with Holm correction across three pairs separately for Recall@5 and EM. F1 differences use paired bootstrap intervals. The budget comparison uses matched question IDs, not independent aggregates from 300 and 500 questions.

## Full model pipeline

The model pipeline uses Python 3.11 in the recorded environment. `reproduction/requirements-inference-observed.txt` lists the packages actually installed there. The entire snapshot has not been installed and tested from scratch; it must not be described as a verified clean inference environment.

```powershell
python -m venv .venv-inference
.\.venv-inference\Scripts\python.exe -m pip install -r reproduction/requirements-inference-observed.txt
.\.venv-inference\Scripts\python.exe run_experiment.py --n-questions 500 --embedder minilm --seed 42 --out rerun_main_new.csv
.\.venv-inference\Scripts\python.exe run_experiment.py --n-questions 300 --embedder minilm --seed 42 --ctx-budget 1500 --out rerun_budget_new.csv
```

Initial model downloads need internet access: `sentence-transformers/all-MiniLM-L6-v2` and `google/flan-t5-base`. The observed Windows CPU environment may require adaptation on another platform. Use new output paths, preserving historical CSVs. Fake embeddings are for smoke testing only.

To add progress and environment evidence for a new full main run:

```powershell
$env:OMP_NUM_THREADS='4'
$env:MKL_NUM_THREADS='4'
$env:TOKENIZERS_PARALLELISM='false'
.\.venv-inference\Scripts\python.exe -u reproduction/run_reproduction.py --operator "Actual operator name" --output-dir reproduction/new_run
.\.venv-inference\Scripts\python.exe reproduction/compare_reproduction.py --operator "Actual operator name" --rerun-csv reproduction/new_run/rerun_main.csv --output reproduction/new_run/comparison.json
```

Replace the operator placeholder with the person or agent who actually performs the run. The wrapper refuses to reuse an output directory containing evidence. It does not change the original splitters, sample, prompt or decoding settings. Offline mode is optional and requires already cached models. See `REPRODUCTION.md`.

## Provenance and interpretation

The 27 October full rerun was operated by Codex on the student computer in the existing environment. All 1,500 prediction strings and per-item numerical metrics matched the original main run. Elapsed time: 3,887.93 seconds. This is a technical reproduction, not an independent human replication. Instructor acceptance is a course arrangement and does not change that methodological description.

Source data and historical logs have not been relabelled or replaced. A later full inference rerun is not an additional sample or seed. The embedding-window groups and the character-budget intervention are exploratory. The original model revisions and original per-method timing were not captured.

## Licence and attribution

The MIT grant in `LICENSE` applies only to the newly authored analysis and document-building scripts identified there. Existing experiment scripts, SQuAD/Wikipedia data and cited publications retain their upstream rights. Preserve the upstream dataset attribution when redistributing.
