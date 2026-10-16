"""Condense full per-cell optical distributions to per-step summaries for Git."""
import csv, gzip, json, sys
from collections import defaultdict
from pathlib import Path

root=Path(sys.argv[1] if len(sys.argv)>1 else
    '/root/REI_BASS_LONGSTEP_20261016_001/longstep_runs_resume')
for row in csv.DictReader((root/'exits.csv').open()):
    if row['exit_code']!='0': continue
    case_id='_'.join(row[k] for k in ('mode','case','steps'))
    out=root/case_id/'output'
    source=out/'optical_distribution.json.gz'
    dest=out/'optical_compact.json'
    if not source.exists() or dest.exists(): continue
    with gzip.open(source,'rt') as f: full=json.load(f)
    groups=defaultdict(lambda:[0,0.0,0.0,float('inf'),0.0])
    for item in full['groups']:
        key=(item['step'],item['phase'],item['cohort'],item['species'])
        v=groups[key];weight=item['photon_weight_per_h']
        v[0]+=item['nodes'];v[1]+=weight
        if item['tau_weighted_mean'] is not None: v[2]+=weight*item['tau_weighted_mean']
        v[3]=min(v[3],item['tau_min']);v[4]=max(v[4],item['tau_max'])
    compact={'schema':'rei.bass.optical_compact.v1','case_id':case_id,
        'full_distribution_sha256':full['raw_sha256'],'raw_rows':full['raw_rows'],
        'accepted_nodes':full.get('accepted_nodes'),
        'frozen_kernel_counterfactual':full.get('frozen_kernel_counterfactual'),
        'step_species_distributions':[{'step':k[0],'phase':k[1],'cohort':k[2],'species':k[3],
            'nodes':v[0],'photon_weight_per_h':v[1],
            'tau_weighted_mean':v[2]/v[1] if v[1] else None,'tau_min':v[3],'tau_max':v[4]}
            for k,v in sorted(groups.items())]}
    with dest.open('x') as f: json.dump(compact,f,separators=(',',':'))
    with dest.open() as f: assert json.load(f)['full_distribution_sha256']==full['raw_sha256']
    print(case_id,len(compact['step_species_distributions']),flush=True)
