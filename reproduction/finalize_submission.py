"""Finish the submission package after the already running inference process ends."""
import datetime, json, os, shutil, subprocess, time, traceback, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'reproduction'; REPO=ROOT/'Assignment4_Repository'
BUNDLED=Path(r'C:\Users\paradise\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
INFERENCE=ROOT/'venv'/'Scripts'/'python.exe'
SAFE='safe.directory='+str(REPO).replace('\\','/')
record={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'waiting_for_full_run'}
def save():
    (OUT/'submission_status.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
def call(args,cwd=ROOT):
    print('Executing',str(args[0]),str(args[1]) if len(args)>1 else '',flush=True)
    return subprocess.run([str(x) for x in args],cwd=cwd,check=True,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
save()
try:
    while True:
        try: env=json.loads((OUT/'environment.json').read_text(encoding='utf-8'))
        except (FileNotFoundError,json.JSONDecodeError):env={}
        if env.get('status') in ['completed','failed']:break
        time.sleep(5)
    record.update(status='building_package',inference_status=env['status']);save()
    if env['status']=='completed':
        (OUT/'comparison.log').write_text(call([INFERENCE,OUT/'compare_reproduction.py']),encoding='utf-8')
    (OUT/'document_build.log').write_text(call([BUNDLED,ROOT/'assignment4'/'build_report.py']),encoding='utf-8')
    for n in ['analyse.py','build_report.py','report.md','analysis.json','error_candidates.json','error_review.json','main_summary.csv','figure1.png','figure2.png']:
        shutil.copy2(ROOT/'assignment4'/n,REPO/'assignment4'/n)
    shutil.copy2(ROOT/'Assignment4_AibynSamat_Final.docx',REPO/'Assignment4_AibynSamat_Final.docx')
    for p in OUT.iterdir():
        if p.is_file() and p.name not in ['submission_status.json','finalize.log','preflight.log','hardware.json']:
            shutil.copy2(p,REPO/'reproduction'/p.name)
    readme=(REPO/'README.md').read_text(encoding='utf-8')
    readme=readme.replace('Assignment4_AibynSamat_Revised.docx','Assignment4_AibynSamat_Final.docx')
    readme=readme.replace('No repository has been published by this preparation step.','Repository: https://github.com/aahhaha/rag-chunking-assignment4 (private). See REPRODUCTION.md for the technical rerun evidence.')
    readme+='\n\n## Repository and technical reproduction\n\nRepository: https://github.com/aahhaha/rag-chunking-assignment4 (private). Release: assignment-4. The instructor needs repository access. See REPRODUCTION.md and Appendix C for the AI-operated full inference rerun in the existing environment. It is not an independent human or clean-environment test. The historical CSVs remain unchanged.\n'
    (REPO/'README.md').write_text(readme,encoding='utf-8')
    guide=(REPO/'Assignment4_Defence_Guide_RU.md').read_text(encoding='utf-8')
    guide+='\n\n## Обновление после технической проверки\n\nРепозиторий создан: https://github.com/aahhaha/rag-chunking-assignment4 (приватный). Текущий результат полного прогона и отличия записаны в reproduction/environment.json и reproduction/comparison.json; Appendix C обновлён по этим файлам. Проверку выполнил Codex на том же компьютере в существующем окружении. Это не проверка другим студентом и не чистая установка. Если преподаватель принимает такую замену, нужно его согласие. Исторические результаты не перезаписаны.\n'
    (REPO/'Assignment4_Defence_Guide_RU.md').write_text(guide,encoding='utf-8')
    shutil.copy2(REPO/'Assignment4_Defence_Guide_RU.md',ROOT/'Assignment4_Defence_Guide_RU.md')
    # Explicit XML validation covers the previously reported title-format defect.
    from xml.etree import ElementTree as ET
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(ROOT/'Assignment4_AibynSamat_Final.docx') as z:
        for name in ['word/styles.xml','word/document.xml']:
            tree=ET.fromstring(z.read(name));assert not tree.findall('.//w:pBdr',ns)
        styles=ET.fromstring(z.read('word/styles.xml'))
        assert all(x.get('{'+ns['w']+'}val')=='000000' for x in styles.findall('.//w:color',ns))
    print(call(['git','-c',SAFE,'add','.'],REPO),flush=True)
    print(call(['git','-c',SAFE,'commit','-m','Record full inference reproduction and complete Assignment 4 submission'],REPO),flush=True)
    print(call(['git','-c',SAFE,'tag','-a','assignment-4','-m','Assignment 4 submission with technical reproduction evidence'],REPO),flush=True)
    print(call(['git','-c',SAFE,'push','origin','main','assignment-4'],REPO),flush=True)
    sha=call(['git','-c',SAFE,'rev-parse','HEAD'],REPO).strip()
    archive=ROOT/'Assignment4_Submission_Package.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in REPO.rglob('*'):
            if p.is_file() and '.git' not in p.relative_to(REPO).parts and '__pycache__' not in p.parts:
                z.write(p,str(p.relative_to(REPO)))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    notes=OUT/'release_notes.md'
    notes.write_text('Assignment 4 report, original results, analysis scripts and AI-operated full inference reproduction evidence.\n\nThe technical rerun uses the existing student environment. It is not an independent classmate test or clean-environment installation. See Appendix C and REPRODUCTION.md.\n',encoding='utf-8')
    print(call(['gh','release','create','assignment-4',str(archive),str(ROOT/'Assignment4_AibynSamat_Final.docx'),'--repo','aahhaha/rag-chunking-assignment4','--verify-tag','--title','Assignment 4','--notes-file',str(notes)]),flush=True)
    release=json.loads(call(['gh','release','view','assignment-4','--repo','aahhaha/rag-chunking-assignment4','--json','url,tagName,isDraft']))
    record.update(status='completed',commit=sha,release=release,archive=str(archive),finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as exc:
    record.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save();raise
