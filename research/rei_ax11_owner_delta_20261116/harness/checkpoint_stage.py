#!/usr/bin/env python3
"""Commit this unit only and archive every recorded R/C checkpoint."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
REL = UNIT.relative_to(REPO)
OUT = REPO.parent / 'ax11_work' / 'owner_delta_checkpoints'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()

def main():
    p=argparse.ArgumentParser(); p.add_argument('stage',type=int);p.add_argument('summary');p.add_argument('--evidence',nargs='+',required=True);a=p.parse_args()
    f=UNIT/'STAGE_LEDGER.json'; rows=json.loads(f.read_text()) if f.exists() else []
    if a.stage != len(rows)+1 or not 1<=a.stage<=10: raise ValueError('Nonsequential checkpoint')
    evidence={n:hashlib.sha256((UNIT/n).read_bytes()).hexdigest() for n in a.evidence}
    rows.append({'stage':a.stage,'theory':'R'+str(a.stage),'coding':'C'+str(a.stage),'summary':a.summary,
                 'evidence_sha256':evidence,'previous_local_commit':git('rev-parse','HEAD'),
                 'consumer':'rei_bianchi scientific admission owner / AX11','original_DAG':'10/17','expansion_DAG':'28/88',
                 'publication':'receipts/PUBLICATIONS.json records actual remote readback','backup':'per-stage committed-tree ZIP; native/provider receipt in final closeout'})
    f.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    git('add','--',str(REL)); changed=git('diff','--cached','--name-only').splitlines()
    if not changed or any(not n.startswith(str(REL)+'/') for n in changed): raise ValueError('Unrelated staged changes')
    git('-c','user.name=ChatGPT Research','-c','user.email=chatgpt-research@users.noreply.github.com','commit','-m',f'research(REI AX11): R{a.stage}/C{a.stage} {a.summary} [10/17; 28/88]')
    head=git('rev-parse','HEAD');tree=git('rev-parse','HEAD^{tree}');OUT.mkdir(parents=True,exist_ok=True)
    archive=OUT/f'REI_AX11_OWNER_DELTA_STAGE_{a.stage:02d}.zip'
    subprocess.run(['git','archive','--format=zip','-o',str(archive),head,str(REL)],cwd=REPO,check=True)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None: raise ValueError('Archive CRC failure')
        for n in z.namelist():
            if not n.endswith('/') and z.read(n)!=subprocess.check_output(['git','show',head+':'+n],cwd=REPO): raise ValueError(n)
    receipt={'stage':a.stage,'local_commit':head,'tree':tree,'archive':str(archive),'bytes':archive.stat().st_size,
             'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'all_committed_archive_members_equal':True}
    (OUT/f'STAGE_{a.stage:02d}.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__': main()
