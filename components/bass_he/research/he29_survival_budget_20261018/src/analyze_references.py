"""Reference-only output reduction; no solver calls or automatic convergence claim."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from reference_contract import OWNER,JOBS,THREADS,admit_pair


def analyze(root):
    root=Path(root);rows={};missing=[];identities=[]
    for r,nodes in JOBS:
        name=f'm8_r{r}_table{nodes}';folder=root/name
        needed=('RESULT.json','IDENTITY.json','TABLE.json')
        if not all((folder/p).is_file() for p in needed):missing.append(name);continue
        d,i,t=[json.loads((folder/p).read_text()) for p in needed]
        if (i.get('m'),i.get('r'),i.get('q'),i.get('angles'),i.get('table_nodes'))!=(8,r,0.,4,nodes):
            raise ValueError('HE29_ANALYSIS_CASE_IDENTITY')
        if i.get('owner_source')!=OWNER or d.get('status')!='REFERENCE_COMPLETED_SCOPED':
            raise ValueError('HE29_ANALYSIS_OWNER_OR_STATUS')
        if i.get('numerical_thread_environment')!=THREADS:raise ValueError('HE29_ANALYSIS_THREAD_IDENTITY')
        table=d.get('table_sha256')
        if not isinstance(table,str) or not table or t.get('source_table_sha256')!=table:
            raise ValueError('HE29_ANALYSIS_TABLE_IDENTITY')
        if d.get('point_qualification',{}).get('points')!=6:raise ValueError('HE29_ANALYSIS_POINT_QUALIFICATION')
        a=d['results']['Radau'];b=d['results']['DOP853'];pair=admit_pair(a,b)
        rows[r,nodes]={'r':r,'table_nodes':nodes,'temperature_K':a['temperature_K'],
          'method_spread_K':pair['method_temperature_difference_K'],
          'absolute_fraction_difference':pair['absolute_fraction_difference'],
          'error_radius_certified':False,'table_sha256':table,
          'parent_transport_comparisons':d.get('comparisons',[])}
        identities.append(tuple(json.dumps(i[k],sort_keys=True) for k in
             ('binary_sha256','source_files','parent_sources','input_sources','numerical_thread_environment')))
    if identities and any(x!=identities[0] for x in identities):
        raise ValueError('HE29_CROSS_REFERENCE_SOURCE_MISMATCH')
    contrasts=[]
    for a,b,axis in [((2,512),(4,512),'strip'),((4,512),(8,512),'strip'),((4,512),(4,1024),'table')]:
        if a in rows and b in rows:
            contrasts.append({'axis':axis,'from':list(a),'to':list(b),
              'delta_temperature_K':rows[b]['temperature_K']-rows[a]['temperature_K'],
              'sum_method_spreads_K':rows[a]['method_spread_K']+rows[b]['method_spread_K'],
              'interpretation':'matched-source empirical sensitivity, not a rigorous error radius'})
    return {'schema':'he29.reference.analysis.v2','complete':len(rows)==4,'completed':len(rows),
            'requested':4,'missing':missing,'references':list(rows.values()),'contrasts':contrasts,
            'new_solver_calls':0,'continuous_spectral_convergence':'HOLD'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    r=analyze(a.root);p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(r,f,indent=2,allow_nan=False)
    print(json.dumps(r,indent=2))
    if not r['complete']:raise SystemExit(1)
