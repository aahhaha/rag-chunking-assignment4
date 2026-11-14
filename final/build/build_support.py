import build_documents as b
from pathlib import Path
import json
R=b.ROOT;O=b.OUT
counts=json.loads((R/'generated/content_checks.json').read_text(encoding='utf-8'))
evidence={'checked':'2026-11-14','primary':{'title':'Discover Computing','source_id':'21101228213','eissn':'2948-2992','status':'Active','coverage':'2024-2026','citescore_year':2025,'citescore':2.0,'categories':{'Library and Information Sciences':{'rank':'120/296','percentile':59},'Information Systems':{'rank':'314/519','percentile':39}}},'backup':{'title':'Discover Artificial Intelligence','source_id':'21101215114','eissn':'2731-0809','status':'Active','coverage':'2021-2026','citescore_year':2025,'citescore':6.2,'categories':{'Computer Vision and Pattern Recognition':{'rank':'45/183','percentile':75},'Information Systems':{'rank':'153/519','percentile':70},'Artificial Intelligence':{'rank':'177/570','percentile':69},'Human Computer Interaction':{'rank':'83/196','percentile':57}}},'source_list':'Official October 2026 workbook downloaded from Elsevier content page. Both Active; neither in Discontinued Titles sheet.','hijacked_check':'488 rows of the publicly linked Retraction Watch checker searched by titles and eISSNs; no matches. This does not guarantee absence of undiscovered clones.','credentials':'No password used or retained. No account created.'}
(R/'sources/journal_verification.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
d=b.newdoc('Journal Fit Statement and Submission Readiness')
d.add_paragraph('Aibyn Samat, SE-2415. Final project for the defence on 16 November 2026. Verification date 14 November 2026.')
d.add_heading('Appendix A Journal Fit Statement',1)
d.add_paragraph('The primary target is Discover Computing. Its recent semantic chunking and RAG evaluation articles directly connect to this paired comparison. Discover Artificial Intelligence is the backup because it publishes empirical RAG evaluations and work on evidence use. Journal submission is voluntary after the course; no manuscript has been sent to either journal.')
rows=[
 ['Title and publisher','Discover Computing; Springer Nature','Discover Artificial Intelligence; Springer Nature'],
 ['ISSN and eISSN','Print 2948-2984; electronic 2948-2992','Electronic 2731-0809'],
 ['Scopus source record','https://www.scopus.com/sourceid/21101228213','https://www.scopus.com/sourceid/21101215114'],
 ['Coverage and current status','Active in October 2026 official source list; coverage 2024-2026','Active in October 2026 official source list; coverage 2021-2026'],
 ['CiteScore 2025 and subject percentile','2.0; Library and Information Sciences 59th (120/296); Information Systems 39th (314/519)','6.2; Computer Vision 75th (45/183); Information Systems 70th (153/519); AI 69th (177/570); HCI 57th (83/196)'],
 ['Discontinued and hijacked checks','Not in official October 2026 discontinued sheet. No title or eISSN match in the Retraction Watch checker searched on 14 November','Same checks completed; no matching discontinued or hijacked entry'],
 ['Official publisher website','https://link.springer.com/journal/10791','https://link.springer.com/journal/44163'],
 ['Recent scope evidence with DOIs','Kiss et al. (2025), Max Min semantic chunking, doi:10.1007/s10791-025-09638-7; Upadhyay and Viviani (2025), health information retrieval, doi:10.1007/s10791-025-09505-5; Elkiran and Rasheed (2026), retriever reranker pairings, doi:10.1007/s10791-026-10156-3','Chen (2026), similarity metrics in Chinese RAG, doi:10.1007/s44163-026-02613-1; Ghaywat et al. (2026), conversational RAG survey, doi:10.1007/s44163-026-02373-y; Muthusami and Saritha (2026), hybrid retrieval generation, doi:10.1007/s44163-026-01059-9'],
 ['Article type and word limit','Research. No separate Research Word template or fixed Research word limit specified on the checked page. Word is accepted; the manuscript uses its formatting rules and the course 4,500-7,500 range.','Research. Confirm article type and full formatting rules before retargeting.'],
 ['Formatting and citations','Arial 12 pt; black headings; embedded numbered tables and figures; numbered square bracket citations; DOI links; abstract under 250 words','The backup uses the Discover series guidelines; retargeting requires a final journal specific check'],
 ['APC and open access','Fully OA. Publisher lists discounted EUR 1,140 / USD 1,520 / GBP 1,040 for acceptance through 31 December 2026; standard EUR 1,890 / USD 2,190 / GBP 1,590. Price depends on acceptance date.','Fully OA. Listed APC EUR 1,390 / USD 1,690 / GBP 1,190; taxes may apply. Recheck at submission.'],
 ['Waivers','Publisher offers funding routes and waivers or discounts under stated eligibility rules. No fee waiver or institutional coverage has been obtained.','Country based and discretionary waivers may apply; discretionary requests should accompany submission. No eligibility is claimed.'],
 ['Data and AI policies','Data availability and funding statements required. Contributions and competing interests declared. Substantive AI use disclosed; human authors retain responsibility.','Data and substantive AI assistance require transparent disclosure under the publisher policy.'],
 ['Review timing','Publisher median submission to first decision 22 days, checked 14 November 2026. This includes editorial decisions and is not a guarantee of completed peer review.','Publisher median submission to first decision 16 days, with the same qualification.'],
 ['Fit and limits','The paper provides a traceable empirical comparison and a compact model input limit case relevant to retrieval engineering. It complements, rather than reproduces, the journal\'s semantic algorithm and reranking studies.','The paper evaluates an AI pipeline and diagnoses differences between retrieved evidence and answer matching. Its single dataset and compact model scope are explicitly bounded.'],
]
fit_row=rows.pop()
b.table(d,'Comparison of primary and backup journals',['Item','Primary journal','Backup journal'],rows,[1.35,2.725,2.725])
d.add_heading('Fit and limits',2)
d.add_paragraph('Primary: '+fit_row[1])
d.add_paragraph('Backup: '+fit_row[2])
d.add_heading('Verification evidence and editorial checks',2)
d.add_paragraph('Scopus records were read in the browser without account registration. The publisher sites were reached through the official Springer Nature domain. The October 2026 source workbook lists both titles as Active and neither in its discontinued sheet. Inactive Information Retrieval Journal is the former title continued as Discover Computing, not evidence that the current title is discontinued. The full numerical verification is stored in sources/journal_verification.json and sources/scopus_list_check.json.')
d.add_paragraph('The current official pages identify editorial boards, submission routes and peer review policies. No guaranteed acceptance was found on those pages. A first decision median is distinguished from acceptance speed. The legitimate publisher URLs and matching eISSNs are used throughout. Absence from the hijacked checker is a limited check, not a guarantee against every clone.')
d.add_paragraph('Primary author guidelines: https://link.springer.com/journal/10791/submission-guidelines. Backup guidelines: https://link.springer.com/journal/44163/submission-guidelines. Backup fees: https://link.springer.com/journal/44163/how-to-publish-with-us. AI policy: https://www.nature.com/nature/editorial-policies/ai. Checker: https://retractionwatch.com/the-retraction-watch-hijacked-journal-checker/. Official source list route: https://www.elsevier.com/products/scopus/content.')
d.add_heading('Appendix B Submission Readiness Checklist',1)
d.add_paragraph('This checklist separates completed preparation from external or author actions. A No entry is not silently treated as Yes. Publication readiness after grading has additional requirements, including an external human reproduction.')
checks=[
 ['Journal format and length','Yes',f"Arial 12 pt; IMRaD; main text {counts['main_text_words']:,} words; abstract {counts['abstract_words']} words; numbered references. Discover accepts Word without a mandatory Research Word template."],
 ['Consistent reported results','Yes','Main values and matched comparisons generated from analysis.json and saved CSVs.'],
 ['Traceable numerical results','Yes','Generated table CSVs, hashes, result IDs and evidence map accompany the code. Historical chunk and subgroup summaries are distinguished.'],
 ['References real and formatted','Yes','30 published sources with source links; DOI included where available.'],
 ['All references read by the author','No','Personal reading and approval remain for Aibyn. reference_reading_register.csv supports this check. AI retrieval does not establish author reading.'],
 ['At least 25 and half recent','Yes','30 references; 18 published in 2022 or later, exceeding half even under the stricter recent window.'],
 ['Explicit supported contributions','Yes','Paired comparison, matched context diagnosis and traceable technical reproduction.'],
 ['Validity and limitations','Yes','Internal, construct, external and statistical limitations discussed.'],
 ['Data and code statement','Yes','Repository, data origin, model access and licensing scope stated.'],
 ['CRediT AI interests funding ethics','Yes','Statements included. The author confirms personal declarations before actual journal submission.'],
 ['Prior participant consent and approval','Not applicable','Public benchmark analysis; no new human participants.'],
 ['Similarity check acceptable','No','Requires the university system and its threshold; no score is invented.'],
 ['Reproduction by another person','No','AI operated technical rerun and clean analysis check completed. Course instructor accepted the earlier individual arrangement; no external human rerun is claimed.'],
 ['Final author approval','No','Student must read and approve the final version before upload or journal submission.'],
 ['Final repository release','Yes','The original final tag is retained. The edited package uses final-revised: https://github.com/aahhaha/rag-chunking-assignment4/releases/tag/final-revised.'],
 ['Individual project permission','Yes as reported','Student confirmed on 14 November 2026 that the instructor accepted the individual final project.'],
]
b.table(d,'Readiness status against the course checklist',['Check','Status','Evidence or remaining action'],checks,[2.05,1.0,3.75])
d.add_heading('Course rubric evidence map',1)
for name,pts,where in [
 ('A1 Title abstract introduction contributions',8,'Manuscript title, Abstract and Section 1'),('A2 Related work',7,'Section 2; Table 1; verified references'),('A3 Materials and methods',10,'Section 3; original code and configuration record'),('A4 Results',12,'Section 4; Tables 2-8; Figures 1-2; Supplementary Results'),('A5 Discussion and conclusion',8,'Sections 5 and 6'),('A6 Writing and formatting',5,'Journal formatting, source register and document layout review'),('B Journal fit and cover letter',5,'Appendix A and one page cover letter'),('C Reproducibility',12,'Repository, release final, regeneration command and explicit external reproduction status'),('D1 Presentation',10,'12 slides and timed speaking script'),('D2 Individual defence',23,'Student rehearsal, code demonstration and oral explanations')]:
 d.add_paragraph(f'{name} ({pts} points): {where}.')
d.add_paragraph('Preparation documents support the rubric but do not predetermine a score. The presentation and individual defence require the student\'s own performance. The proposed journal has not approved or accepted this manuscript.')
d.save(O/'Journal_Fit_and_Readiness.docx')

c=b.newdoc('Cover Letter')
for text in ['14 November 2026','Editor, Discover Computing','Dear Editor,',
 'I would like to present the research manuscript "Chunking and Context Limits in Retrieval Augmented Question Answering with Compact Models" for consideration as a Research article.',
 'The paper compares fixed, overlapping and percentile semantic segmentation in a common local question answering pipeline. On the same 500 SQuAD questions, overlap improves Recall at five over fixed segmentation by 6.6 percentage points, with a paired 95% interval of 3.0 to 10.0 points and Holm adjusted p = 0.0008. Its higher Exact Match score is not statistically established. The semantic condition exposes a practical input length failure that we examine with a matched exploratory context cap.',
 'The study compares existing splitters in a local pipeline and examines where long chunks exceed model input limits. It fits the journal\'s work on semantic chunking and RAG evaluation, including Kiss et al. (doi:10.1007/s10791-025-09638-7), Upadhyay and Viviani (doi:10.1007/s10791-025-09505-5), and Elkiran and Rasheed (doi:10.1007/s10791-026-10156-3). The findings apply to the tested models and answer matching measures. They do not establish a general ranking of semantic methods.',
 'The manuscript provides public code, question level outputs and reproducibility evidence. The dataset is an existing public benchmark, with no newly recruited participants. It discloses substantive AI assistance and the limits of the technical rerun. The experiments previously appeared in course assignments and the public repository; this history is disclosed in the manuscript. This workflow has not submitted the manuscript to another journal.',
 'Thank you for considering the study. I would welcome an assessment of its methodological fit and contribution.',
 'Sincerely,','Aibyn Samat','Astana IT University, Astana, Kazakhstan','242187@astanait.edu.kz']:
 c.add_paragraph(text)
c.save(O/'Cover_Letter.docx')
print('Journal Fit, Readiness Checklist and Cover Letter created')
