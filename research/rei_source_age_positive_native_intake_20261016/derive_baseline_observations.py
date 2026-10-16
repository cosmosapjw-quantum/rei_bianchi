"""Reproject saved baseline coordinates; no history/RHS reintegration."""
import argparse,json,subprocess,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('source',type=Path);p.add_argument('out',type=Path);p.add_argument('--q',type=float,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
s=subprocess.Popen([str(a.binary),'server',str(a.q)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1);setup=json.loads(s.stdout.readline());cells=setup['cells'];obs=[]
def physical(active,x,y):
 s.stdin.write(f'P {active} {x:.17e} '+' '.join(format(v,'.17e') for v in y)+'\n');s.stdin.flush();v=s.stdout.readline();assert not v.startswith('ERR'),v;return json.loads(v)
for event,x in enumerate([*setup['births'],setup['x1']]):
 y=np.load(a.source/f'accepted_coordinates_event{event}.npy');state=physical(event,x,y);obs.append(dict(x=x,side='pre',active=event,physical=state))
 if event<len(setup['births']):y[4+2*cells*event:4+2*cells*(event+1)]=setup['encoded_births'][event];state=physical(event+1,x,y)
 obs.append(dict(x=x,side='post',active=min(event+1,8),physical=state))
old=json.loads((a.source/'endpoint.json').read_text());assert np.array_equal(np.array(old['flat']),np.array(state['flat'])),'baseline physical state changed'
(a.out/'endpoint.json').write_text(json.dumps(state)+'\n');(a.out/'observations.json').write_text(json.dumps(obs)+'\n');(a.out/'setup.json').write_text(json.dumps(setup)+'\n')
for filename in ['ledgers.json','solver_return.json']:(a.out/filename).write_bytes((a.source/filename).read_bytes())
(a.out/'BASELINE_REUSE.json').write_text(json.dumps(dict(scope='saved coordinate readback, no RHS/history rerun',source=str(a.source),physical_flat_bytewise_numeric_equal=True,files=[dict(path=v.name,sha256=hashlib.sha256(v.read_bytes()).hexdigest()) for v in sorted(a.source.glob('accepted_coordinates*.npy'))]),indent=2)+'\n')
s.stdin.close();s.wait();assert s.returncode==0
