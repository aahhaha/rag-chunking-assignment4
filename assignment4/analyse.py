import csv, json, hashlib, itertools, collections, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
DATA=ROOT.parent
METHODS=['fixed','overlap','semantic']
METRICS=['hit@1','hit@3','hit@5','em','f1','truncated','ctx_chars@5']
def read(name):
    rows=list(csv.DictReader((DATA/name).open(encoding='utf-8')))
    out={m:{r['id']:r for r in rows if r['method']==m} for m in METHODS}
    ids=list(out['fixed'])
    assert all(set(out[m])==set(ids) for m in METHODS)
    assert len(rows)==len(ids)*3
    return out,ids
def ci(x):
    x=np.asarray(x,float); rng=np.random.default_rng(0)
    z=np.array([rng.choice(x,len(x),replace=True).mean() for _ in range(2000)])
    return np.percentile(z,[2.5,97.5]).tolist()
def analyse(name):
    data,ids=read(name); result={'n':len(ids),'methods':{},'comparisons':[]}
    for m in METHODS:
        result['methods'][m]={k:{'mean':float(np.mean([float(data[m][i][k]) for i in ids])), 'ci':ci([data[m][i][k] for i in ids])} for k in METRICS}
    for metric in ['hit@5','em','f1']:
        tests=[]
        for a,b in itertools.combinations(METHODS,2):
            x=np.array([float(data[a][i][metric]) for i in ids]); y=np.array([float(data[b][i][metric]) for i in ids]); d=y-x
            aonly=int(((x==1)&(y==0)).sum()); bonly=int(((x==0)&(y==1)).sum())
            t={'metric':metric,'a':a,'b':b,'difference':float(d.mean()),'ci':ci(d),'a_only':aonly,'b_only':bonly}
            if metric!='f1':
                n=aonly+bonly
                t['p']=min(1.,2*sum(math.comb(n,j) for j in range(min(aonly,bonly)+1))/2**n) if n else 1.
            tests.append(t)
        if metric!='f1':
            prev=0
            for rank,t in enumerate(sorted(tests,key=lambda t:t['p'])):
                prev=max(prev,min(1,(3-rank)*t['p'])); t['holm']=prev
        result['comparisons']+=tests
    result['depth']={m:{'hit5_not3':sum(int(data[m][i]['hit@5']) and not int(data[m][i]['hit@3']) for i in ids),'em_when_hit3':float(np.mean([float(data[m][i]['em']) for i in ids if int(data[m][i]['hit@3'])]))} for m in METHODS}
    return result
out={name:analyse(name) for name in ['results_main.csv','results_budget1500.csv']}
stage_data,stage_ids=read('results_main.csv')
out['failure_stages']={}
for method in METHODS:
    counts=collections.Counter()
    for row in stage_data[method].values():
        if float(row['em'])!=0:continue
        if int(row['truncated']):label='Prompt truncated'
        elif not int(row['hit@5']):label='No answer hit in top 5'
        elif not int(row['hit@3']):label='Answer hit only at ranks 4 or 5'
        elif float(row['f1'])>=.5:label='Hit at 3 and F1 at least 0.5'
        elif float(row['f1'])>0:label='Hit at 3 and F1 below 0.5'
        else:label='Hit at 3 and F1 zero'
        counts[label]+=1
    out['failure_stages'][method]=dict(counts)
out['hashes']={name:hashlib.sha256((DATA/name).read_bytes()).hexdigest() for name in ['dev-v1.1.json','results_main.csv','results_budget1500.csv','results.csv','run_experiment.py','semantic_visibility.json']}
main,ids=read('results_main.csv'); budget,bids=read('results_budget1500.csv')
assert bids==ids[:300]
out['matched_budget']={m:{'main_em':float(np.mean([float(main[m][i]['em']) for i in bids])),'budget_em':float(np.mean([float(budget[m][i]['em']) for i in bids])),'delta_ci':ci([float(budget[m][i]['em'])-float(main[m][i]['em']) for i in bids])} for m in METHODS}
out['sample_ids']=ids
data=json.loads((DATA/'dev-v1.1.json').read_text(encoding='utf-8'))['data']
titles={q['id']:a['title'] for a in data for p in a['paragraphs'] for q in p['qas']}
out['sample_article_counts']=dict(collections.Counter(titles[i] for i in ids))
(ROOT/'analysis.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
with (ROOT/'main_summary.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['method','metric','mean','ci_lower','ci_upper'])
    for m in METHODS:
        for k,v in out['results_main.csv']['methods'][m].items():w.writerow([m,k,v['mean'],*v['ci']])

def chart(filename, groups, series, values, ylabel):
    im=Image.new('RGB',(1440,760),'white');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26); small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
    colors=['#365b82','#d08b41','#6f8f76']; left=120;top=110;bottom=620;right=1380
    d.text((left,35),ylabel,fill='black',font=font)
    for y in range(0,101,20):
        py=bottom-y/100*(bottom-top);d.line((left,py,right,py),fill='#dddddd',width=2);d.text((55,py-13),str(y),fill='black',font=small)
    gw=(right-left)/len(groups);bw=min(90,gw/(len(series)+2))
    for j,s in enumerate(series):
        d.rectangle((left+j*360,75,left+j*360+25,95),fill=colors[j]);d.text((left+35+j*360,69),s,fill='black',font=small)
    for i,g in enumerate(groups):
        center=left+gw*(i+.5)
        for j in range(len(series)):
            val=values[j][i]*100;x=center+(j-(len(series)-1)/2)*bw
            y=bottom-val/100*(bottom-top);d.rectangle((x-bw*.42,y,x+bw*.42,bottom),fill=colors[j]);d.text((x-28,y-32),f'{val:.1f}',fill='black',font=small)
        box=d.multiline_textbbox((0,0),g,font=small,align='center');d.multiline_text((center-(box[2]-box[0])/2,bottom+22),g,fill='black',font=small,align='center')
    im.save(ROOT/filename)
chart('figure1.png',['Fixed','Overlap','Semantic'],['Recall@5','Exact Match','Token F1'],[[out['results_main.csv']['methods'][m][k]['mean'] for m in METHODS] for k in ['hit@5','em','f1']],'Main experiment scores (%)   n = 500 per condition')
vis=json.loads((DATA/'semantic_visibility.json').read_text())['groups']
chart('figure2.png',['Answer visible\n267 questions','Answer beyond window\n228 questions'],['Fixed','Overlap','Semantic'],[[vis[g][m] for g in ['visible','beyond_limit']] for m in METHODS],'Recall@5 (%)   exploratory answer position groups')
print(json.dumps(out['matched_budget'],indent=2))
for t in out['results_main.csv']['comparisons']:print(t)
print('Analysis regenerated and paired sample checks passed')
