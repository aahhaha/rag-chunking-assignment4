"""Compare a completed model rerun with preserved historical outputs."""
import argparse, csv, datetime, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--operator',required=True,help='Actual operator of this comparison')
parser.add_argument('--rerun-csv',default='reproduction/rerun_main.csv')
parser.add_argument('--output',default='reproduction/comparison_check.json')
args=parser.parse_args()
rerun=Path(args.rerun_csv)
if not rerun.is_absolute():rerun=ROOT/rerun
output=Path(args.output)
if not output.is_absolute():output=ROOT/output
if output.resolve()==(ROOT/'reproduction/comparison.json').resolve():
    raise SystemExit('Choose a new output path to preserve the historical comparison.json')
output.parent.mkdir(parents=True,exist_ok=True)
def load(path):
    with path.open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    result={(r['method'],r['id']):r for r in rows}
    assert len(result)==len(rows),'Duplicate method/question rows'
    return result
old=load(ROOT/'results_main.csv'); new=load(rerun)
assert old.keys()==new.keys(),'Question/method keys differ'
metrics=['hit@1','hit@3','hit@5','em','f1','truncated','ctx_chars@5']
summary={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'operator':args.operator,
         'scope':'Full inference rerun in existing environment; not independent human or clean-environment validation',
         'paired_rows':len(new),'methods':{},
         'rerun_sha256':hashlib.sha256((rerun).read_bytes()).hexdigest()}
for method in ['fixed','overlap','semantic']:
    keys=[k for k in old if k[0]==method]; n=len(keys)
    rows={}
    for metric in metrics:
        a=sum(float(old[k][metric]) for k in keys)/n
        b=sum(float(new[k][metric]) for k in keys)/n
        rows[metric]={'historical_mean':a,'rerun_mean':b,'difference':b-a,
                      'different_items':sum(abs(float(old[k][metric])-float(new[k][metric]))>1e-12 for k in keys)}
    rows['different_predictions']=sum(old[k]['pred']!=new[k]['pred'] for k in keys)
    summary['methods'][method]=rows
summary['all_numeric_items_match']=all(v['different_items']==0 for m in summary['methods'].values() for k,v in m.items() if k!='different_predictions')
summary['all_predictions_match']=all(m['different_predictions']==0 for m in summary['methods'].values())
output.write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
