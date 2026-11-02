"""Run the unchanged experiment with progress and environment evidence."""
import argparse, datetime, hashlib, importlib.metadata, json, os, platform, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
import run_experiment as R
import torch
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--operator',required=True,help='Actual operator of this new run')
parser.add_argument('--output-dir',default='reproduction/new_run',help='New output folder; historical files are not overwritten')
args=parser.parse_args()
OUT=Path(args.output_dir)
if not OUT.is_absolute():OUT=ROOT/OUT
OUT.mkdir(parents=True,exist_ok=True)
if (OUT/'environment.json').exists() or (OUT/'rerun_main.csv').exists():
    raise SystemExit('Output folder already contains run evidence; choose a new --output-dir')
start=time.time()
metadata={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'operator':args.operator,
          'independent_human_test':False,'clean_environment':False,
          'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
          'processor':platform.processor(),'cpu_count':os.cpu_count(),
          'torch_threads':torch.get_num_threads(),
          'dataset_sha256':hashlib.sha256((ROOT/'dev-v1.1.json').read_bytes()).hexdigest(),
          'experiment_sha256':hashlib.sha256((ROOT/'run_experiment.py').read_bytes()).hexdigest()}
(OUT/'environment.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
(OUT/'requirements-inference-observed.txt').write_text('\n'.join(sorted(f'{d.metadata["Name"]}=={d.version}' for d in importlib.metadata.distributions()))+'\n',encoding='utf-8')
original_generate=R.generate
count=0
def logged_generate(*args,**kwargs):
    global count
    result=original_generate(*args,**kwargs)
    count+=1
    if count%25==0:
        progress={'generated_answers':count,'total':1500,'elapsed_seconds':round(time.time()-start,1)}
        (OUT/'progress.json').write_text(json.dumps(progress),encoding='utf-8')
        print('REPRODUCTION_PROGRESS',json.dumps(progress),flush=True)
    return result
R.generate=logged_generate
sys.argv=['run_experiment.py','--n-questions','500','--embedder','minilm','--seed','42',
          '--squad',str(ROOT/'dev-v1.1.json'),'--out',str(OUT/'rerun_main.csv')]
try:
    R.main()
    metadata.update(status='completed',elapsed_seconds=round(time.time()-start,2),generated_answers=count)
except BaseException as exc:
    metadata.update(status='failed',error=repr(exc),elapsed_seconds=round(time.time()-start,2))
    raise
finally:
    metadata['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (OUT/'environment.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
