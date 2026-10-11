"""Independent MP80 positive quadrature for the new upper-offset basis only."""
from pathlib import Path
import sys,json,hashlib
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2]
for p in (HERE,Q1B/'c11/precision/_runtime_deps'):sys.path.insert(0,str(p))
import mpmath as mp
from source_precision_v2 import _negative_exponential_offsets
mp.mp.dps=80
rows=[]
for dx in (4.423544863740858e-17,1e-8,.001,.02,.2,.499):
    v0,v1=_negative_exponential_offsets(dx);d=mp.mpf(dx)
    exact0=mp.quad(lambda u:(1-u)*(-mp.expm1(-d*u)),[0,1])
    exact1=mp.quad(lambda u:u*(-mp.expm1(-d*u)),[0,1])
    errors=[float(abs(mp.mpf(v0)-exact0)/exact0),float(abs(mp.mpf(v1)-exact1)/exact1)]
    assert max(errors)<=1e-12,(dx,errors)
    rows.append(dict(dx=dx,v0=v0,v1=v1,MP80=[str(exact0),str(exact1)],own_component_relative_errors=errors))
result=dict(schema='rei.c12.positive_upper_offset_oracle.v1',dps=80,rows=rows,
   max_relative_error=max(max(r['own_component_relative_errors']) for r in rows),criterion=1e-12,
   native_calls=0,whole_source_MP80_accuracy_claim=False,
   scope='Independent quadrature of NEW positive upper-offset basis; shared source tables not involved',
   source_file_sha256=hashlib.sha256((HERE/'source_precision_v2.py').read_bytes()).hexdigest())
(HERE/'UPPER_OFFSET_ORACLE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'max_relative_error':result['max_relative_error'],'pass':True}))
