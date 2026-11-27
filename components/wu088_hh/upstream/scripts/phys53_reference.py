"""Source-bound local CLI or clearly labelled isolated reference diagnostic."""
import argparse,json
from pathlib import Path
from wu088_hh.phys53_coulomb_tail import *
p=argparse.ArgumentParser()
p.add_argument('--source',default=None)
p.add_argument('--out',required=True)
p.add_argument('--dps',type=int,default=68)
a=p.parse_args()
source_status='NOT_CHECKED_IN_ISOLATED_RUNTIME'
if a.source:
    source_status='EXACT_SHA256_VERIFIED:'+verify_original_source(a.source)
rows=[]
for radius in (27,30,43):
    for ell in (21,28,29,40,64,100,128,192,256):
        cf=depth_comparison(ell,radius)
        ref=mp_reference(ell,radius,a.dps)
        rows.append({'cf':cf,'reference':ref,'asymptotic_log10_current':asymptotic_log10_current(ell,radius)})
out={'schema':SCHEMA,'source_status':source_status,'physics':'CENTRAL_COULOMB_ONLY','rows':rows,'screened_DtN':'UNRESOLVED','HH_R10':'OFF'}
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
Path(a.out).write_text(json.dumps(out,indent=2)+'\n')
print('rows',len(rows),'first',rows[0]['reference']['log10_current_per_Bohr'],'last',rows[-1]['reference']['log10_current_per_Bohr'])