from pathlib import Path
import json,re,csv,collections,hashlib,unicodedata,sys
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent/'Assignment4_Repository'
if (ROOT.parent/'assignment4'/'analysis.json').exists() and ROOT.name=='final':REPO=ROOT.parent
OUT=ROOT/'submission';OUT.mkdir(exist_ok=True)
GEN=ROOT/'generated';GEN.mkdir(exist_ok=True)
A=json.loads((REPO/'assignment4/analysis.json').read_text(encoding='utf-8'))
M=['fixed','overlap','semantic'];MAIN=A['results_main.csv']['methods']
E={r['key']:r for r in json.loads((ROOT/'sources/reference_evidence.json').read_text(encoding='utf-8'))}
TEXT=(ROOT/'manuscript.md').read_text(encoding='utf-8')
KEYS=list(dict.fromkeys(re.findall(r'\{([a-z0-9]+)\}',TEXT.replace('[[RELATED]]','{qu}{kiss}{pairings}'))))
NUM={k:i+1 for i,k in enumerate(KEYS)}
def cite(s):return re.sub(r'\{([a-z0-9]+)\}',lambda m:'['+str(NUM[m[1]])+']',s)
def ascii_clean(s):return s.replace('\u2014',', ').replace('\u2013','-').replace('\ufffd','-')

# Correct bibliographic years use publication year, not the first preprint year.
OV={
 'rag':('Lewis P, Perez E, Piktus A, et al.','Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks','Advances in Neural Information Processing Systems. 2020;33:9459-9474.',2020,'https://arxiv.org/abs/2005.11401'),
 'beir':('Thakur N, Reimers N, Ruckle A, Srivastava A, Gurevych I.','BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models','NeurIPS Datasets and Benchmarks. 2021;1.',2021,'https://arxiv.org/abs/2104.08663'),
 'selfrag':('Asai A, Wu Z, Wang Y, Sil A, Hajishirzi H.','Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection','International Conference on Learning Representations. 2024.',2024,'https://arxiv.org/abs/2310.11511'),
 'faiss':('Johnson J, Douze M, Jegou H.','Billion-scale similarity search with GPUs','IEEE Transactions on Big Data. 2021;7(3):535-547.',2021,'https://doi.org/10.1109/TBDATA.2019.2921572'),
 'efron':('Efron B.','Bootstrap Methods: Another Look at the Jackknife','Annals of Statistics. 1979;7(1):1-26.',1979,'https://doi.org/10.1214/aos/1176344552'),
 'holm':('Holm S.','A Simple Sequentially Rejective Multiple Test Procedure','Scandinavian Journal of Statistics. 1979;6(2):65-70.',1979,'https://www.jstor.org/stable/4615733'),
 'mcnemar':('McNemar Q.','Note on the Sampling Error of the Difference Between Correlated Proportions or Percentages','Psychometrika. 1947;12:153-157.',1947,'https://doi.org/10.1007/BF02295996'),
}
def authorfmt(s):
 s=ascii_clean(s)
 if ',' in s:last,first=s.split(',',1)
 else:
  words=s.split();last=words[-1];first=' '.join(words[:-1])
 return last.strip()+' '+''.join(w[0] for w in first.strip().split() if w)
REF=[]
for k in KEYS:
 m=E[k].get('metadata',{})
 if k in OV:authors,title,venue,year,url=OV[k]
 else:
  aa=m.get('citation_author',[]);authors=', '.join(authorfmt(x) for x in aa[:6])+(', et al.' if len(aa)>6 else '.')
  title=ascii_clean(m['citation_title'][0])
  year=int(re.search(r'\d{4}',str(m.get('citation_publication_date',m.get('citation_date'))))[0])
  venue=m.get('citation_journal_title',m.get('citation_conference_title',['']))[0]+'. '+str(year)
  vol=m.get('citation_volume',[]);issue=m.get('citation_issue',[]);first=m.get('citation_firstpage',[]);last=m.get('citation_lastpage',[])
  if vol:venue+=';'+vol[0]
  if issue:venue+='('+issue[0]+')'
  if first:venue+=':'+first[0]+('-'+last[0] if last and last[0] else '')
  venue+='.'
  url='https://doi.org/'+m['citation_doi'][0] if m.get('citation_doi') else E[k]['url']
 REF.append(dict(number=NUM[k],key=k,authors=authors,title=title,venue=venue,year=year,url=url,author_read='Author confirmation required',verified='Publisher metadata checked; see source URL'))
(ROOT/'references.json').write_text(json.dumps(REF,indent=2,ensure_ascii=False),encoding='utf-8')
with (ROOT/'reference_reading_register.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(REF[0]));w.writeheader();w.writerows(REF)

def newdoc(title=None):
 d=Document();s=d.sections[0];s.page_width=Inches(8.27);s.page_height=Inches(11.69)
 s.top_margin=s.bottom_margin=Inches(.72);s.left_margin=s.right_margin=Inches(.73)
 for st in d.styles:
  if st.type in [1,2]:
   st.font.name='Arial';st.font.size=Pt(12);st.font.color.rgb=RGBColor(0,0,0)
   for c in st.element.iter(qn('w:color')):c.attrib.clear();c.set(qn('w:val'),'000000')
   for b in list(st.element.iter(qn('w:pBdr'))):b.getparent().remove(b)
 normal=d.styles['Normal'];normal.paragraph_format.space_after=Pt(7);normal.paragraph_format.line_spacing=1.12
 d.styles['Title'].font.size=Pt(20);d.styles['Title'].font.bold=True
 for n,sz in [('Heading 1',15),('Heading 2',13)]:
  d.styles[n].font.size=Pt(sz);d.styles[n].font.bold=True;d.styles[n].paragraph_format.space_before=Pt(13);d.styles[n].paragraph_format.space_after=Pt(6)
 foot=s.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
 run=foot.add_run();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');run._r.append(fld)
 d.core_properties.author='Aibyn Samat';d.core_properties.title=title or 'Final Research Project'
 if title:d.add_paragraph(title,'Title')
 return d

def table(d,title,heads,rows,widths=None):
 cap=d.add_paragraph(title);cap.paragraph_format.keep_with_next=True
 for r in cap.runs:r.bold=True
 t=d.add_table(rows=1,cols=len(heads));t.autofit=False
 if widths:
  for col,w in zip(t.columns,widths):col.width=Inches(w)
 for c,x in zip(t.rows[0].cells,heads):c.text=str(x)
 for row in rows:
  for c,x in zip(t.add_row().cells,row):c.text=str(x)
 for i,row in enumerate(t.rows):
  trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
  if i==0:trpr.append(OxmlElement('w:tblHeader'))
  for j,c in enumerate(row.cells):
   if widths:c.width=Inches(widths[j])
   pr=c._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    b=OxmlElement('w:'+edge);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');bd.append(b)
   pr.append(bd);mar=OxmlElement('w:tcMar')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');mar.append(e)
   pr.append(mar)
   if i==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8ECE9');pr.append(sh)
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.0;p.paragraph_format.keep_with_next=(i==0 or (len(t.rows)<=5 and i<len(t.rows)-1))
    if j>0 and all(len(str(x))<35 for x in rows[0]):p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:r.font.size=Pt(12);r.bold=i==0
 d.add_paragraph('')
 return t

def csvwrite(name,heads,rows):
 with (GEN/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(heads);w.writerows(rows)

def percent(v,digits=1):return f'{100*v:.{digits}f}'
def interval(v):return f"{percent(v['mean'])} [{percent(v['ci'][0])}, {percent(v['ci'][1])}]"
T={}
T['RELATED']=('Table 1 Related studies and comparison with this experiment',['Study','Intervention and evidence','Relation to this study'],[
 [cite('Qu et al. {qu}'),'Semantic versus fixed segmentation across retrieval and generation tasks','Mixed benefits; different benchmark and cost evaluation'],
 [cite('Kiss et al. {kiss}'),'Max Min semantic method; clustering and multiple choice RAG','Different semantic algorithm and answer task'],
 [cite('Elkiran and Rasheed {pairings}'),'Retriever and reranker pairings; quality and efficiency','Pipeline interactions; no matching chunking comparison'],
 ['Present study','Three splitters; 500 paired questions; matched context check','Compact models; explicit input limits and saved outputs']], [1.25,2.7,2.85])
T['CONFIG']=('Table 2 Chunking settings and recorded fragment sizes',['Method','Rule','Chunks','Mean chars'],[['Fixed','500 chars; no overlap',3235,496],['Overlap','500 chars; 50 overlap',3585,497],['Semantic','95th percentile',589,2720]],[1.1,2.7,1.2,1.8])
T['MAIN']=('Table 3 Main results on 500 questions in percent with 95% bootstrap intervals',['Method','Recall at 5','Exact Match','Token F1'],[[m.capitalize(),*[interval(MAIN[m][k]) for k in ['hit@5','em','f1']]] for m in M],[1.0,1.9,1.9,2.0])
T['DEPTH']=('Table 4 Retrieval depth and prompt diagnostics on 500 questions',['Method','Recall at 1 %','Recall at 3 %','Truncated %','Mean chars at 5'],[[m.capitalize(),*[percent(MAIN[m][k]['mean']) for k in ['hit@1','hit@3','truncated']],f"{MAIN[m]['ctx_chars@5']['mean']:,.0f}"] for m in M],[1.05,1.35,1.35,1.35,1.7])
T['TESTS']=('Table 5 Paired McNemar comparisons and differences in percentage points',['Metric A vs B','A only','B only','B minus A pp','Holm p'],[[t['metric']+' '+t['a']+' vs '+t['b'],t['a_only'],t['b_only'],f"{t['difference']*100:+.1f}",'<0.0001' if t['holm']<.0001 else f"{t['holm']:.4f}"] for t in A['results_main.csv']['comparisons'] if t['metric']!='f1'],[2.3,.75,.75,1.55,1.45])
T['F1']=('Table 6 Paired F1 differences in percentage points with 95% intervals',['B minus A','Difference pp','95 percent CI pp'],[[t['b']+' minus '+t['a'],f"{100*t['difference']:+.2f}",f"[{100*t['ci'][0]:+.2f}, {100*t['ci'][1]:+.2f}]"] for t in A['results_main.csv']['comparisons'] if t['metric']=='f1'],[2.8,1.55,2.45])
stages=['Prompt truncated','No answer hit in top 5','Answer hit only at ranks 4 or 5','Hit at 3 and F1 at least 0.5','Hit at 3 and F1 below 0.5','Hit at 3 and F1 zero']
T['ERRORS']=('Table 7 Exact Match failures grouped by the first matching rule',['Failure category','Fixed','Overlap','Semantic'],[[s,*[A['failure_stages'][m].get(s,0) for m in M]] for s in stages]+[['Total',*[sum(A['failure_stages'][m].values()) for m in M]]],[3.6,1,1.05,1.15])
T['BUDGET']=('Table 8 Exact Match before and after the context cap on the same 300 questions',['Method','Main EM %','Capped EM %','Change pp and 95 percent CI'],[[m.capitalize(),percent(v['main_em'],2),percent(v['budget_em'],2),f"{100*(v['budget_em']-v['main_em']):+.2f} [{100*v['delta_ci'][0]:+.2f}, {100*v['delta_ci'][1]:+.2f}]"] for m,v in A['matched_budget'].items()],[1.0,1.35,1.45,3.0])
for key,(title,heads,rows,widths) in T.items():csvwrite(key.lower(),heads,rows)
(GEN/'tables.json').write_text(json.dumps({k:dict(caption=v[0],headers=v[1],rows=v[2]) for k,v in T.items()},indent=2),encoding='utf-8')

# High resolution 600 dpi figures with no embedded titles; captions are in Word.
def fig(name,groups,series,values,limits=None):
 W,H=3900,1900;im=Image.new('RGB',(W,H),'white');dr=ImageDraw.Draw(im)
 candidates=['C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/System/Library/Fonts/Supplemental/Arial.ttf']
 fontpath=next((f for f in candidates if Path(f).exists()),None)
 font=ImageFont.truetype(fontpath,65) if fontpath else ImageFont.load_default(size=65)
 small=ImageFont.truetype(fontpath,56) if fontpath else ImageFont.load_default(size=56)
 colors=['#285749','#A07643','#666F79'];left,top,right,bottom=260,250,3780,1570
 for y in range(0,101,20):
  yy=bottom-y/100*(bottom-top);dr.line((left,yy,right,yy),fill='#D9D9D9',width=3);dr.text((90,yy-35),str(y),font=small,fill='black')
 dr.text((80,100),'%',font=font,fill='black')
 for j,s in enumerate(series):
  x=left+j*1100;dr.rectangle((x,90,x+50,140),fill=colors[j]);dr.text((x+75,80),s,font=font,fill='black')
 gw=(right-left)/len(groups);bw=min(230,gw/(len(series)+1.7))
 for i,g in enumerate(groups):
  cx=left+gw*(i+.5)
  for j in range(len(series)):
   v=values[j][i]*100;x=cx+(j-(len(series)-1)/2)*bw;y=bottom-v/100*(bottom-top)
   dr.rectangle((x-bw*.37,y,x+bw*.37,bottom),fill=colors[j])
   if limits:
    lo,hi=limits[j][i];yl=bottom-lo*(bottom-top);yh=bottom-hi*(bottom-top)
    dr.line((x,yl,x,yh),fill='black',width=5)
    for yy in [yl,yh]:dr.line((x-30,yy,x+30,yy),fill='black',width=5)
    labely=yh-80
   else:labely=y-80
   dr.text((x,labely),f'{v:.1f}',font=small,fill='black',anchor='mt')
  box=dr.multiline_textbbox((0,0),g,font=font,align='center',spacing=15)
  dr.multiline_text((cx-(box[2]-box[0])/2,bottom+65),g,font=font,fill='black',align='center',spacing=15)
 im.save(GEN/name,dpi=(600,600))
fig('Fig1.png',['Fixed','Overlap','Semantic'],['Recall at 5','Exact Match','Token F1'],[[MAIN[m][k]['mean'] for m in M] for k in ['hit@5','em','f1']],[[MAIN[m][k]['ci'] for m in M] for k in ['hit@5','em','f1']])
V=json.loads((REPO/'semantic_visibility.json').read_text())['groups']
fig('Fig2.png',['Answer inside window\n267 questions','Answer beyond window\n228 questions'],['Fixed','Overlap','Semantic'],[[V[g][m] for g in ['visible','beyond_limit']] for m in M])

if '--tables-only' in sys.argv:
 print('Regenerated eight tables and both figures from saved evidence.');sys.exit(0)

d=newdoc();
for line in TEXT.splitlines():
 if not line.strip():continue
 if line.startswith('# '):d.add_paragraph(line[2:],'Title')
 elif line.startswith('### '):d.add_heading(line[4:],2)
 elif line.startswith('## '):d.add_heading(line[3:],1)
 elif line.startswith('[['):
  key=line[2:-2]
  if key in T:
   title,heads,rows,widths=T[key];table(d,title,heads,rows,widths)
  else:
   n=int(key[-1]);d.add_picture(str(GEN/f'Fig{n}.png'),width=Inches(6.8));d.paragraphs[-1].paragraph_format.keep_with_next=True
   d.add_paragraph('Fig. 1 Main results on 500 questions. Error bars show 95% question bootstrap intervals.' if n==1 else 'Fig. 2 Recall at five by answer position relative to the 254-token embedding window. Each group contains the same questions for all three methods. Five questions with unresolved positions are omitted.')
 else:d.add_paragraph(cite(ascii_clean(line)))
d.add_heading('References',1)
for r in REF:
 p=d.add_paragraph(f"{r['number']}. {r['authors']} {r['title']}. {r['venue']} {r['url']}");p.paragraph_format.keep_together=True
d.save(OUT/'Final_Manuscript_Aibyn_Samat.docx')
(GEN/'manuscript_with_references.txt').write_text(cite(TEXT)+'\n\nReferences\n'+'\n'.join(f"[{r['number']}] {r['authors']} {r['title']}. {r['venue']} {r['url']}" for r in REF),encoding='utf-8')

supp=newdoc('Supplementary Results and Numerical Provenance')
table(supp,'Table S1 Results with capped context on 300 questions in percent with 95% intervals',['Method','Recall at 5','EM','F1'],[[m.capitalize(),*[interval(A['results_budget1500.csv']['methods'][m][k]) for k in ['hit@5','em','f1']]] for m in M],[1,1.9,1.9,2])
table(supp,'Table S2 Paired binary comparisons with unadjusted p values and difference intervals',['Metric and pair','Raw p','Difference pp and CI'],[[t['metric']+' '+t['a']+' vs '+t['b'],f"{t['p']:.8g}",f"{t['difference']*100:+.1f} [{t['ci'][0]*100:+.2f}, {t['ci'][1]*100:+.2f}]"] for t in A['results_main.csv']['comparisons'] if t['metric']!='f1'],[2.5,1.35,2.95])
for key in ['results_main.csv','results_budget1500.csv','dev-v1.1.json','run_experiment.py']:
 supp.add_paragraph(key+': '+A['hashes'][key])
supp.add_paragraph('The main and capped outputs were reported in the earlier course work. No new inference outcomes were generated for the final manuscript. Tables 2 and the subgroup figure use the historical chunk record and semantic_visibility.json. Question level membership for the visibility groups is unavailable.')
supp.save(OUT/'Supplementary_Results.docx')

body=TEXT[TEXT.index('## 1 Introduction'):TEXT.index('## Declarations')]
stats={'main_text_words':len(re.findall(r'\b\w+\b',body)),'abstract_words':len(re.findall(r'\b\w+\b',TEXT[TEXT.index('## Abstract'):TEXT.index('Keywords:')]))-1,'references':len(REF),'references_2022_onward':sum(r['year']>=2022 for r in REF),'tables':8,'figures':2,'main_n':500,'matched_n':300}
assert 4500<=stats['main_text_words']<=7500,stats
assert 200<=stats['abstract_words']<250,stats
assert len(REF)>=25 and stats['references_2022_onward']>=len(REF)/2,stats
(GEN/'content_checks.json').write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats))
