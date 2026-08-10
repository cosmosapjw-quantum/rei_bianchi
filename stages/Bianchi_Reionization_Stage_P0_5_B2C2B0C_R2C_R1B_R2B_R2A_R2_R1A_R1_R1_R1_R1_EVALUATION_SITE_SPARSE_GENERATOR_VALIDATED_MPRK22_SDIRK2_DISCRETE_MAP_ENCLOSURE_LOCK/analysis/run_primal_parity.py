#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
def load():
 s=importlib.util.spec_from_file_location('evalsite_parity_runtime',HERE/'evaluation_site_trial.py');m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
m=load(); lanes=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
rows=[];start=time.perf_counter()
for lane in lanes:
 r=m.primal_parity_audit(REPO,lane=lane,partition=2048);r['lane']=lane;rows.append(r)
result={'classification':'FOUR_SITE_PRIMAL_PARITY_AUDIT','partition':2048,'rows':rows,
 'all_lanes_pass':all(x['parity_pass'] for x in rows),'elapsed_s':time.perf_counter()-start}
(STAGE/'data/PRIMAL_PARITY_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'all_lanes_pass':result['all_lanes_pass'],'elapsed_s':result['elapsed_s'],
 'rows':[{'lane':x['lane'],'state':x.get('max_state_relative_difference'),'temperature':x.get('max_temperature_relative_difference'),'ledger_equal':x.get('ledger_equal'),'trace_prefix':x.get('site_trace',[])[:4]} for x in rows]},indent=2))
raise SystemExit(0 if result['all_lanes_pass'] else 1)
