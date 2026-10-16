"""Bounded per-step/cell/species optical distributions from completed native traces.

Operates only on new longstep_runs_resume files. After an atomic JSON summary
with raw SHA-256 is reread, the large regenerable CSV.gz may be removed on NCP.
"""
import csv, gzip, hashlib, json, math, sys
from collections import defaultdict
from pathlib import Path

root=Path(next((arg for arg in sys.argv[1:] if not arg.startswith('--')),
    '/root/REI_BASS_LONGSTEP_20261016_001/longstep_runs_resume'))
done=[r for r in csv.DictReader((root/'exits.csv').open()) if r['exit_code']=='0']
for row in done:
    case_id='_'.join(row[k] for k in ('mode','case','steps'))
    out=root/case_id/'output'
    source=out/'optical_nodes.csv.gz'
    summary=out/'optical_distribution.json.gz'
    if summary.exists() or not source.exists(): continue
    h=hashlib.sha256()
    with source.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    groups=defaultdict(lambda:[0,0.0,0.0,float('inf'),0.0])
    bias={'old_be_minus_exponential_number_per_h':0.0,
          'newborn_be_minus_uniform_number_per_h':0.0,
          'old_be_minus_exponential_energy_ev_per_h':0.0,
          'newborn_be_minus_uniform_energy_ev_per_h':0.0}
    accepted_nodes=0
    count=0
    with gzip.open(source,'rt',newline='') as f:
        for r in csv.DictReader(f):
            count+=1
            weight=float(r['number_per_h'])
            for species in ('hi','hei','heii'):
                tau=float(r['tau_'+species]);key=(r['step'],r['opacity_phase'],r['cohort'],r['cell'],species)
                v=groups[key];v[0]+=1;v[1]+=weight;v[2]+=weight*tau;v[3]=min(v[3],tau);v[4]=max(v[4],tau)
            if r['opacity_phase']=='accepted':
                accepted_nodes+=1
                tau=sum(float(r['tau_'+j]) for j in ('hi','hei','heii'))
                phi=(1+tau*(-0.5+tau*(1/6+tau*(-1/24+tau/120))) if tau<1e-5
                     else -math.expm1(-tau)/tau)
                label='old_be_minus_exponential' if r['cohort']=='old' else 'newborn_be_minus_uniform'
                d=weight*(1/(1+tau)-(math.exp(-tau) if r['cohort']=='old' else phi))
                bias[label+'_number_per_h']+=d
                bias[label+'_energy_ev_per_h']+=d*float(r['energy_physical_ev'])
    distribution=[{'step':int(k[0]),'phase':k[1],'cohort':k[2],'cell':int(k[3]),'species':k[4],
        'nodes':v[0],'photon_weight_per_h':v[1],'tau_weighted_mean':v[2]/v[1] if v[1] else None,
        'tau_min':v[3],'tau_max':v[4]} for k,v in groups.items()]
    record={'schema':'rei.bass.optical_distribution.v1','case_id':case_id,'raw_sha256':h.hexdigest(),
        'raw_bytes':source.stat().st_size,'raw_rows':count,'groups':distribution,
        'accepted_nodes':accepted_nodes,'frozen_kernel_counterfactual':bias,
        'scope':'per-step per-cell species weighted mean and range, pre and accepted opacity'}
    temporary=out/'optical_distribution.json.gz.tmp'
    with gzip.open(temporary,'xt',compresslevel=1) as f: json.dump(record,f,separators=(',',':'))
    temporary.rename(summary)
    with gzip.open(summary,'rt') as f: assert json.load(f)['raw_sha256']==h.hexdigest()
    print(case_id,count,len(distribution),h.hexdigest(),flush=True)
    if '--release-ncp-raw' in sys.argv: source.unlink()
