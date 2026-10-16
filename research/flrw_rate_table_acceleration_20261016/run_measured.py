#!/usr/bin/env python3
"""Run one prescribed local command and retain actual outputs/resources."""
import argparse, json, pathlib, resource, subprocess, time
p=argparse.ArgumentParser();p.add_argument('--kind',choices=['build','science'],required=True);p.add_argument('--name',required=True);p.add_argument('--timeout',type=float,required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
unit=pathlib.Path(__file__).resolve().parent;out=unit/'evidence';out.mkdir(exist_ok=True)
ledger_path=out/'RUN_LEDGER.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'runs':[]}
science=[r for r in ledger['runs'] if r['kind']=='science'];wall=sum(r['wall_seconds'] for r in science);cpu=sum(r['cpu_seconds'] for r in science)
if a.kind=='science' and (wall>=90 or cpu>=180):raise SystemExit('Root aggregate scientific allowance exhausted')
timeout=min(a.timeout,90-wall) if a.kind=='science' else min(a.timeout,120)
cmd=a.command[1:] if a.command[:1]==['--'] else a.command
start=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
with (out/(a.name+'.stdout')).open('w') as stdout,(out/(a.name+'.stderr')).open('w') as stderr:
 try:r=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=timeout);code=r.returncode
 except subprocess.TimeoutExpired:code=124
elapsed=time.perf_counter()-start;after=resource.getrusage(resource.RUSAGE_CHILDREN)
record={'name':a.name,'kind':a.kind,'command':cmd,'exit_code':code,'wall_seconds':elapsed,'cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'max_rss_kib':after.ru_maxrss,'timeout_seconds':timeout}
(out/(a.name+'.resources.json')).write_text(json.dumps(record,indent=2)+'\n');ledger['runs'].append(record);ledger['scientific_wall_seconds']=wall+(elapsed if a.kind=='science' else 0);ledger['scientific_cpu_seconds']=cpu+(record['cpu_seconds'] if a.kind=='science' else 0);ledger_path.write_text(json.dumps(ledger,indent=2)+'\n');print(json.dumps(record));raise SystemExit(code)
