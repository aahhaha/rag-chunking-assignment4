from pathlib import Path
import json,re,collections
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
R=Path(__file__).resolve().parent
A=json.loads((R/'analysis.json').read_text())
D=Document(); sec=D.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=Inches(.8);sec.left_margin=sec.right_margin=Inches(.8)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2']:
    st=D.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
D.styles['Normal'].font.size=Pt(11);D.styles['Normal'].paragraph_format.space_after=Pt(6);D.styles['Normal'].paragraph_format.line_spacing=1.12
D.styles['Title'].font.size=Pt(20);D.styles['Heading 1'].font.size=Pt(14);D.styles['Heading 1'].paragraph_format.space_before=Pt(14)
for st in D.styles:
    if st.type==1:
        st.font.color.rgb=RGBColor(0,0,0)
        if st.font._element.rPr is not None:
            for co in st.font._element.rPr.findall(qn('w:color')):
                for attr in ['themeColor','themeTint','themeShade']:
                    co.attrib.pop(qn('w:'+attr),None)
def p(s,style=None):return D.add_paragraph(s,style)
def heading(s):D.add_heading(s,1)
def table(headers,rows,widths=None):
    t=D.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths:
        for c,w in zip(t.columns,widths):c.width=Inches(w)
    for c,h in zip(t.rows[0].cells,headers):c.text=h
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for c,s in zip(t.add_row().cells,row):c.text=str(s)
    for ri,row in enumerate(t.rows):
        for ci,c in enumerate(row.cells):
            if widths:c.width=Inches(widths[ci])
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=c._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');bd.append(e)
            pr.append(bd);m=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'80');e.set(qn('w:type'),'dxa');m.append(e)
            pr.append(m)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E7ECF2');pr.append(sh)
            for para in c.paragraphs:
                para.paragraph_format.space_after=Pt(3);para.paragraph_format.line_spacing=1.0
                for run in para.runs:run.font.size=Pt(9);run.bold=ri==0
    p('')
    return t
def fmt(v):return f"{v['mean']*100:.1f} [{v['ci'][0]*100:.1f}, {v['ci'][1]*100:.1f}]"
def pv(v):return '<0.0001' if v<.0001 else f'{v:.4f}'
def results(name):
    return [[m.capitalize(),*[fmt(A[name]['methods'][m][k]) for k in ['hit@5','em','f1']]] for m in ['fixed','overlap','semantic']]
for line in (R/'report.md').read_text(encoding='utf-8').splitlines():
    if not line:continue
    if line.startswith('# '):p(line[2:],'Title')
    elif line.startswith('## '):heading(line[3:])
    elif line=='[[SETUP]]':
        p('Table 1 Implemented configurations')
        table(['Condition','Chunk rule','Chunks','Mean chars'],[['Fixed','500 chars; no overlap','3,235','496'],['Overlap','500 chars; 50 overlap','3,585','497'],['Semantic','95th percentile','589','2,720']],[1.1,3.2,1,1.6])
        p('Chunk counts and lengths are preserved from Assignment 3 and corroborated in part by semantic_visibility.json. They were not rebuilt during this reanalysis.')
    elif line=='[[RESULTS]]':
        p('Table 2 Main outcomes in percent with 95 percent bootstrap intervals')
        table(['Condition','Recall@5','Exact Match','Token F1'],results('results_main.csv'),[1.1,1.9,1.9,2])
        table(['Condition','Recall@1','Recall@3','Truncated','Mean chars at 5'],[[m.capitalize(),*[f"{A['results_main.csv']['methods'][m][k]['mean']*100:.1f}" for k in ['hit@1','hit@3','truncated']],f"{A['results_main.csv']['methods'][m]['ctx_chars@5']['mean']:,.0f}"] for m in ['fixed','overlap','semantic']],[1.2,1,1,1,2.7])
    elif line=='[[FAILURESTAGES]]':
        p('Table 4 All EM failures grouped by the first matching rule')
        stages=['Prompt truncated','No answer hit in top 5','Answer hit only at ranks 4 or 5','Hit at 3 and F1 at least 0.5','Hit at 3 and F1 below 0.5','Hit at 3 and F1 zero']
        table(['Saved outcome','Fixed','Overlap','Semantic'],[[s,*[A['failure_stages'][m].get(s,0) for m in ['fixed','overlap','semantic']]] for s in stages]+[['Total EM failures',*[sum(A['failure_stages'][m].values()) for m in ['fixed','overlap','semantic']]]],[4.1,.9,.9,1])
        p('Rules are applied from top to bottom. Truncation takes priority, so truncated prompts may also contain retrieval failures. A hit at 3 indicates answer-string availability before input truncation; it does not verify that the generator received supporting evidence.')
    elif line=='[[TESTS]]':
        p('Table 3 Paired exact McNemar comparisons')
        table(['Metric and A vs B','A only','B only','B minus A pp','Raw p','Holm p'],[[f"{t['metric']} {t['a']} vs {t['b']}",t['a_only'],t['b_only'],f"{t['difference']*100:+.1f}",pv(t['p']),pv(t['holm'])] for t in A['results_main.csv']['comparisons'] if t['metric']!='f1'],[2.1,.65,.65,1,1.25,1.25])
        p('The exact binomial McNemar statistic is the discordant B-only count conditional on the sum of discordant pairs. No chi-square approximation is used.')
        table(['F1 comparison B minus A','Difference pp','Paired 95 percent CI pp'],[[f"{t['b']} minus {t['a']}",f"{t['difference']*100:+.2f}",f"[{t['ci'][0]*100:+.2f}, {t['ci'][1]*100:+.2f}]"] for t in A['results_main.csv']['comparisons'] if t['metric']=='f1'],[3.2,1.3,2.4])
    elif line.startswith('[[FIGURE'):
        n=1 if '1' in line else 2
        D.add_picture(str(R/f'figure{n}.png'),width=Inches(6.8))
        p('Figure 1 Main scores for the same 500 questions. Point estimates are shown; confidence intervals appear in Table 2.' if n==1 else 'Figure 2 Recall by semantic answer position relative to the 254-token usable embedding window. The five unresolved positions are omitted. Groups are exploratory, with membership defined by semantic chunks.')
    else:p(line)
D.add_page_break();heading('Appendix A Retrospective Configuration Record')
p('Status: retrospective documentation of runs reported in Assignment 3. Moodle upload timestamp and prior protocol approval are not verified. This form must not be backdated.')
table(['Field','Recorded setting'],[['Hypothesis','Semantic exceeds fixed on Recall@5 and EM after Holm correction'],['Primary reporting outcome','Recall@5; designated retrospectively for Assignment 4'],['Secondary outcomes','Recall@1 and @3, EM, token F1, truncation, retrieved characters'],['Dataset','SQuAD v1.1 dev; 48 articles; 10,570 questions'],['Runs','One configuration per method; main n=500; exploratory budget n=300; seed 42'],['Analysis','2,000 question bootstrap resamples; seed 0; exact McNemar; Holm within metric'],['Support rule','Both Recall@5 and EM favour semantic significantly; otherwise H1 not supported'],['Prompt','Answer the question using only the context. Context follows, then Question, then Answer. See generate() for exact newlines.']],[1.6,5.3])
p('Dataset SHA-256: '+A['hashes']['dev-v1.1.json'])
p('Exact sample IDs and per-article counts: analysis.json. SHA-256 hashes for all result inputs and the experiment script are included there.')
heading('Appendix B Review of Thirty Failed Cases')
p('Selection: first 30 fixed-size EM failures in results_main.csv order. Review performed with AI assistance from the saved predictions, gold answers, source passages, and hit flags. Student validation is required. Labels are mutually exclusive descriptions; they are not verified causal diagnoses.')
cases=json.loads((R/'error_candidates.json').read_text(encoding='utf-8'))
labels={1:'Mixed text',6:'Answer span',11:'Wrong entity or explanation',12:'Answer span',17:'Wrong entity or explanation',20:'Answer span',21:'Wrong entity or explanation',22:'Answer span',23:'Wrong entity or explanation',24:'Answer outside top 3',25:'Wrong entity or explanation',28:'Wrong entity or explanation'}
for i,c in enumerate(cases,1):c['review_label']=labels.get(i,'No hit in top 5')
(R/'error_review.json').write_text(json.dumps(cases,indent=2,ensure_ascii=False),encoding='utf-8')
counts=collections.Counter(c['review_label'] for c in cases)
table(['Observed category','Cases'],list(counts.items()),[5.8,1.1])
for i,c in enumerate(cases,1):
    p(f"B{i:02d}  {c['id']}  {c['review_label']}",'Heading 2')
    p(c['question']);p('Gold: '+c['gold'][0]);p('Prediction: '+c['pred'])
    p(f"Hit@3 {c['hit@3']}; Hit@5 {c['hit@5']}; F1 {float(c['f1']):.3f}.")
    if i in [10,20]:D.add_page_break()
heading('Appendix C Reproduction Test Record')
table(['Check','Outcome'],[['Saved result reanalysis','Completed locally: analyse.py regenerated JSON, CSV, and figures; paired IDs and 300-question subset assertions passed.'],['Full model rerun in clean environment','Pending independent classmate test. No successful outcome is claimed.'],['Tester and date','To be entered by the actual independent tester.'],['Repository URL and release','Pending publication and assignment-4 tag.'],['Environment fidelity','Assignment 3 lists versions, but a verified historical lockfile, model revision pins, hardware and timing logs are absent.']],[2,4.9])
p('Record after the actual independent test: tester, date, OS/hardware, installation command, experiment command, dataset hash, generated output hash, numerical differences, and error logs. Use README.md. Do not mark this test passed based only on reanalysis of existing CSVs.')
heading('Appendix D Exploratory Checks and Run Inventory')
p('Table D1 Budget check n equals 300 with 95 percent question bootstrap intervals')
table(['Condition','Recall@5','Exact Match','Token F1'],results('results_budget1500.csv'),[1.1,1.9,1.9,2])
p('Table D2 Matched first 300 questions from the main run versus budget check')
table(['Condition','Main EM percent','Budget EM percent','Change pp and 95 percent CI'],[[m,f"{v['main_em']*100:.2f}",f"{v['budget_em']*100:.2f}",f"{(v['budget_em']-v['main_em'])*100:+.2f} [{v['delta_ci'][0]*100:+.2f}, {v['delta_ci'][1]*100:+.2f}]"] for m,v in A['matched_budget'].items()],[1.1,1.5,1.5,2.8])
p('All budget prompts have truncated=0. The context is still cut to 1,500 characters before tokenisation. This is an exploratory within-sample intervention.')
import csv
pilot=list(csv.DictReader((R.parent/'results.csv').open(encoding='utf-8')))
table(['Saved pilot condition','Questions','Recall@5','EM','Truncated'],[[m,len([r for r in pilot if r['method']==m]),*[f"{sum(float(r[k]) for r in pilot if r['method']==m)/len([r for r in pilot if r['method']==m])*100:.1f}%" for k in ['hit@5','em','truncated']]] for m in ['fixed','overlap','semantic']],[1.8,1,1.2,1.2,1.7])
p('The retrieval-only run is documented in Assignment 3, but its separate raw output was not available for this package. Historical generation-library versions are reported in that document and remain unverified against a saved environment export.')
heading('Appendix E Numerical Provenance')
p('Main outcomes and paired statistics: results_main.csv to analyse.py to analysis.json and main_summary.csv. Budget outcomes: results_budget1500.csv through the same analysis. Pilot: results.csv. Embedding-window groups: semantic_visibility.json, originally produced by semantic_visibility.py. Chunk lengths: Assignment3_AibynSamat.docx, Table 0. Error examples: saved result IDs joined to dev-v1.1.json, reviewed in error_review.json.')
# Explicitly override both paragraph and linked character styles. Some viewers
# resolve TitleChar/HeadingChar even when the paragraph style is already black.
for st in D.styles:
    for border in list(st.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
    for color in list(st.element.iter(qn('w:color'))):
        color.attrib.clear();color.set(qn('w:val'),'000000')
    if st.name=='Title' or 'Heading' in st.name or 'heading' in st.name:
        st.font.color.rgb=RGBColor(0,0,0)
        st.font.underline=False
for para in D.paragraphs:
    for border in list(para._p.iter(qn('w:pBdr'))):border.getparent().remove(border)
    for run in para.runs:
        run.font.color.rgb=RGBColor(0,0,0)
        run.font.underline=False
out=R.parent/'Assignment4_AibynSamat_Final.docx';D.save(out)
text=(R/'report.md').read_text(encoding='utf-8');body=text[text.index('## 4 Main Results'):text.index('## 8 Reproducibility Statement')]
print('Results and Discussion narrative words:',len(re.findall(r"\b[\w-]+\b",body)))
print(out)
