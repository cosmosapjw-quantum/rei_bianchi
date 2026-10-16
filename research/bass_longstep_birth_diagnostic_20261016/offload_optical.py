"""Move completed, hash-verified *new* optical traces off bounded NCP staging."""
import csv, hashlib, io, json, subprocess, time
from pathlib import Path

base=Path('/home/cosmosapjw/worktrees/rei-bass-longstep-native-20261016/research/bass_longstep_birth_diagnostic_20261016')
local=base/'optical_raw'
local.mkdir(exist_ok=True)
remote='/root/REI_BASS_LONGSTEP_20261016_001/longstep_runs_resume'
key='/home/cosmosapjw/.ssh/ncp_key'
host='root@49.50.142.2'
ssh=['ssh','-i',key,'-o','BatchMode=yes',host]
receipt=base/'evidence'/'OPTICAL_OFFLOAD.jsonl'
done={json.loads(s)['case_id'] for s in receipt.read_text().splitlines()} if receipt.exists() else set()

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()

idle=0
while idle<6:
    p=subprocess.run(ssh+['cat',remote+'/exits.csv'],capture_output=True,text=True,check=True)
    rows=list(csv.DictReader(io.StringIO(p.stdout)))
    work=0
    for row in rows:
        if row['exit_code']!='0': continue
        case_id='_'.join(row[k] for k in ('mode','case','steps'))
        if case_id in done: continue
        src=f"{remote}/{case_id}/output/optical_nodes.csv.gz"
        exists=subprocess.run(ssh+['test','-f',src]).returncode==0
        if not exists: continue
        dst=local/f'{case_id}.csv.gz'
        if dst.exists(): raise RuntimeError(f'create-only destination exists: {dst}')
        subprocess.run(['rsync','-a','-e',f'ssh -i {key} -o BatchMode=yes',f'{host}:{src}',str(dst)],check=True)
        remote_hash=subprocess.run(ssh+['sha256sum',src],capture_output=True,text=True,check=True).stdout.split()[0]
        local_hash=digest(dst)
        if local_hash!=remote_hash: raise RuntimeError(f'hash mismatch: {case_id}')
        with receipt.open('a') as f:
            f.write(json.dumps({'case_id':case_id,'sha256':local_hash,'bytes':dst.stat().st_size,
                'remote':src,'local':str(dst),'readback':'MATCH'})+'\n')
            f.flush()
        subprocess.run(ssh+['rm','--',src],check=True)
        done.add(case_id);work+=1
        print(case_id,local_hash,dst.stat().st_size,flush=True)
    idle=0 if work else idle+1
    time.sleep(10)
