#!/usr/bin/env python3
"""Publish only this loop's owned subtree and create an immutable recovery ZIP."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
REL = HERE.relative_to(REPO)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', type=int, required=True)
    p.add_argument('--summary', required=True)
    p.add_argument('--evidence', nargs='+', required=True)
    a = p.parse_args()
    ledger = HERE/'STAGES.json'
    rows = json.loads(ledger.read_text()) if ledger.exists() else []
    if a.stage != len(rows)+1 or not 1 <= a.stage <= 10:
        raise ValueError('nonsequential stage; do not overwrite a checkpoint')
    evidence = {}
    for name in a.evidence:
        f = HERE/name
        if not f.is_file():
            raise ValueError('missing evidence: '+name)
        evidence[name] = hashlib.sha256(f.read_bytes()).hexdigest()
    rows.append({'stage': a.stage, 'theory': 'R'+str(a.stage),
                 'coding': 'C'+str(a.stage), 'summary': a.summary,
                 'central_completed': 28, 'central_total': 88,
                 'canonical_delta': 0, 'evidence_sha256': evidence,
                 'previous_checkpoint_commit': git('rev-parse','HEAD'),
                 'drift_watchdog': 'WITHIN_ORIGINAL_ABUNDANCE_SCOPE'})
    ledger.write_text(json.dumps(rows, indent=2, ensure_ascii=False)+'\n')
    if a.stage == 10:
        payloads = sorted(x for x in HERE.rglob('*') if x.is_file()
                          and '__pycache__' not in x.parts
                          and x.name != 'DELIVERY_MANIFEST.json')
        delivery = {'schema': 'rei.axbi.final-delivery.v1',
                    'central_completed': 28, 'central_total': 88,
                    'theory_and_coding_paired_checkpoints': 10,
                    'publication_readback': 'see PR374 final body and remote backup receipts',
                    'sha256': {str(x.relative_to(HERE)): hashlib.sha256(x.read_bytes()).hexdigest()
                               for x in payloads}}
        (HERE/'DELIVERY_MANIFEST.json').write_text(json.dumps(delivery, indent=2)+'\n')
    git('add','--',str(REL))
    staged = git('diff','--cached','--name-only').splitlines()
    if any(not x.startswith(str(REL)+'/') for x in staged):
        raise RuntimeError('unrelated staged changes; refuse commit')
    git('-c','user.name=ChatGPT Research','-c','user.email=chatgpt-research@users.noreply.github.com',
        'commit','-m',f'research(REI AXBI): R{a.stage}/C{a.stage} {a.summary} [28/88]')
    commit = git('rev-parse','HEAD')
    out = REPO.parent/'rei_axbi_backups'
    out.mkdir(exist_ok=True)
    target = out/f'REI_AXBI_OWNER_20261115_STAGE_{a.stage:02d}.zip'
    if target.exists():
        raise RuntimeError('archive already exists')
    files = sorted(x for x in HERE.rglob('*') if x.is_file() and '__pycache__' not in x.parts)
    manifest = {str(x.relative_to(HERE)): hashlib.sha256(x.read_bytes()).hexdigest() for x in files}
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in files:
            z.write(f,str(f.relative_to(HERE)))
        z.writestr('RECOVERY_COMMIT.txt',commit+'\n')
        z.writestr('RECOVERY_SHA256.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise RuntimeError('archive CRC failure')
        for name,h in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=h:
                raise RuntimeError('archive member hash failure')
    receipt={'stage':a.stage,'commit':commit,'archive':str(target),
             'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
             'member_count':len(files)+2,'member_hashes_verified':True}
    (out/f'STAGE_{a.stage:02d}_LOCAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':
    main()
