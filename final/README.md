# Final manuscript and defence

Author: Aibyn Samat, SE-2415. Defence: 16 November 2026.

The final manuscript integrates the earlier chunking research and saved experiments. It does not claim newly collected inference results. The instructor accepted the individual final project, as reported by the student on 14 November 2026.

## Submission files

- `submission/Final_Manuscript_Aibyn_Samat.docx`: journal-formatted article, 4,880 main-text words and 230-word abstract.
- `submission/Journal_Fit_and_Readiness.docx`: Appendix A with primary and backup journals, Appendix B checklist and rubric evidence map.
- `submission/Cover_Letter.docx`: one-page cover letter for Discover Computing.
- `submission/Supplementary_Results.docx`: budget outcomes, raw p values and hashes.
- `submission/Final_Defence_Aibyn_Samat.pdf`: 12 slides for the 10-minute presentation.
- `submission/Final_Defence_Aibyn_Samat.pptx`: editable slide version adapted from Canva template EAGwX2VN8ps by Hayyan Creative Studio.
- `Defence_Guide_RU.md` and `speaker_notes.json`: plain Russian explanations and English speech per slide.

PDF copies of the Word documents are included for stable viewing. The DOCX files remain the editable manuscripts.

## Regenerate every Results table and figure

From the repository root, with Python 3.11 or 3.12:

```powershell
py -3.12 -m venv .venv-final
.\.venv-final\Scripts\python.exe -m pip install -r requirements-analysis.txt
.\.venv-final\Scripts\python.exe final\reproduce.py
```

On Linux or macOS, create a virtual environment with your installed Python, install the same requirements and run `python final/reproduce.py`. Arial is used for figure lettering on Windows; DejaVu Sans or Arial is selected on other systems. Numeric outputs do not depend on fonts. Byte-identical image rendering is not promised across platforms.

This command analyses saved predictions, validates paired IDs, checks direct success counts and chunk statistics against the rerun log, then creates all eight manuscript table CSVs and both high-resolution figures under `final/generated/`. It does not download models or rerun inference. Original raw files are hashed before and after to verify immutability.

Add `--documents` to rebuild Word outputs using the current Markdown and verified reference metadata. PDF conversion requires an Office or compatible document renderer. The checked delivery PDFs are included. Rebuilding slides is separate from numerical analysis and requires the original Canva template and the bundled authoring runtime; all charts and tables in the supplied PPTX are editable.

## Numerical provenance

| Article object | Generated file | Source |
|---|---|---|
| Table 1 closest studies | related.csv | Verified published studies and manuscript comparison |
| Table 2 chunk statistics | config.csv | reproduction/full_run.log, checked against recorded counts |
| Table 3 main scores | main.csv | results_main.csv through assignment4/analyse.py |
| Table 4 input diagnostics | depth.csv | results_main.csv |
| Table 5 binary tests | tests.csv | Paired outcomes in results_main.csv |
| Table 6 F1 differences | f1.csv | Paired F1 values and question bootstrap |
| Table 7 errors | errors.csv | Sequential classification of all EM failures |
| Table 8 matched cap check | budget.csv | Same first 300 IDs in main and budget CSVs |
| Figure 1 | Fig1.png | Main means and bootstrap intervals |
| Figure 2 | Fig2.png | semantic_visibility.json, historical aggregate groups |

The visibility summary does not retain question membership, so it supports regeneration of the published group figure but not new subgroup significance tests. Supplementary results derive from the same analysis JSON. Table 1 is a literature comparison rather than an experimental statistic.

## Journal verification

Primary: Discover Computing, eISSN 2948-2992, Scopus source 21101228213. Backup: Discover Artificial Intelligence, eISSN 2731-0809, source 21101215114. On 14 November 2026 the official October source workbook lists both Active and neither in its discontinued sheet. Source-card percentiles and coverage are recorded in `sources/journal_verification.json`; workbook checks in `sources/scopus_list_check.json`; hijacked-title lookup in `sources/hijacked_check.json`. Links and dates are supplied so the status can be checked again.

Discover Computing accepts Word for Research articles and does not mandate a separate Research Word template on the checked guidelines page. The manuscript implements its font, abstract, citation, figure and table requirements. A course submission is not a journal submission or acceptance.

## Integrity and actions remaining for the student

The source register verifies bibliographic records; it does not certify that the student has read them. The author must review the manuscript, references and declarations and approve the final version. University similarity checking is not performed in this package. External human reproduction is not performed. The AI-operated technical rerun and clean saved-output analysis are described accurately in the manuscript and the original reproduction folder.

Historical outputs and earlier release tags are preserved. The final release uses the tag `final`. No passwords, authentication tokens, private messages, full downloaded article texts or raw Canva template are included in the submission package. The modified slides contain template design elements under Canva's applicable use terms; the raw template is not relicensed as project code.

## Licensing

The original repository MIT notice continues to cover its named analysis files. Original final Python and JavaScript scripts are also available under MIT as specified in `final/LICENSE`. Third-party datasets and models retain upstream rights. SQuAD data are attributed to Rajpurkar et al. and distributed under the dataset's CC BY-SA 4.0 terms, separately from the MIT software licence of the SQuAD explorer website. MiniLM and FLAN-T5 model repositories identify Apache 2.0 model licences. No model weights are bundled. No private study data are withheld.
