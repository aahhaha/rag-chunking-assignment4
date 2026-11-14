"""Regenerate the final article Results tables and figures from saved outputs."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys,re
R=Path(__file__).resolve().parent
REPO=R.parent if (R.parent/'assignment4/analysis.json').exists() and R.name=='final' else R.parent/'Assignment4_Repository'
ap=argparse.ArgumentParser();ap.add_argument('--documents',action='store_true',help='also rebuild the manuscript and support DOCX files');args=ap.parse_args()
raw=['results_main.csv','results_budget1500.csv','results.csv','dev-v1.1.json','run_experiment.py','semantic_visibility.json']
hashes={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in raw}
subprocess.run([sys.executable,str(REPO/'assignment4/analyse.py')],cwd=REPO,check=True)
cmd=[sys.executable,str(R/'build/build_documents.py')]
if not args.documents:cmd+=['--tables-only']
subprocess.run(cmd,cwd=REPO,check=True)
if args.documents:subprocess.run([sys.executable,str(R/'build/build_support.py')],cwd=REPO,check=True)
assert hashes=={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in raw},'Historical input modified'
A=json.loads((REPO/'assignment4/analysis.json').read_text());assert A['results_main.csv']['n']==500;assert A['results_budget1500.csv']['n']==300
expected={'fixed':(376,274),'overlap':(409,290),'semantic':(332,7)}
for m,(hit,em) in expected.items():
 rows=[r for r in csv.DictReader((REPO/'results_main.csv').open(encoding='utf-8')) if r['method']==m]
 assert len(rows)==500 and sum(int(r['hit@5']) for r in rows)==hit and sum(float(r['em']) for r in rows)==em
log=(REPO/'reproduction/full_run.log').read_text(encoding='utf-8')
counts={m:tuple(map(int,re.search(r'\['+m+r'\] chunks=(\d+) mean_len=(\d+)',log).groups())) for m in expected}
assert counts=={'fixed':(3235,496),'overlap':(3585,497),'semantic':(589,2720)}
for name in ['related','config','main','depth','tests','f1','errors','budget']:assert (R/'generated'/f'{name}.csv').exists()
for name in ['Fig1.png','Fig2.png']:assert (R/'generated'/name).exists()
out={'status':'passed','main_n':500,'matched_n':300,'raw_inputs_unchanged':True,'eight_tables_and_two_figures_regenerated':True,'exact_counts_checked':expected,'chunk_log_counts_checked':counts,'raw_sha256':hashes}
(R/'generated/reproduction_check.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('FINAL RESULTS REPRODUCTION PASSED: eight tables, two figures, unchanged raw inputs.')
