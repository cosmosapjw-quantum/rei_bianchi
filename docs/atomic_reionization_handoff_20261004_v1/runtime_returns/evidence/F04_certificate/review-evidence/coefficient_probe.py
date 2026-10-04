import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, platform
from pathlib import Path
from fractions import Fraction
from sage.all import RealIntervalField
root=Path('/home/cosmosapjw/Dropbox/bianchi/rei_bianchi')
p=root/'.cuh/fastest-track/REI-F04-CERT'
scope=json.loads((p/'review-scope.json').read_text())
def hashes():
    return {s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in scope['files']}
before=hashes(); assert before==scope['files']
spec=importlib.util.spec_from_file_location('frozen_checker',p/'checker.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
manifest=json.loads((root/'runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text())
constants=json.loads((p/'model_constants.json').read_text())
model=m.Model(manifest,constants)
candidate=json.loads((p/'candidate.json').read_text())
R=m.R
exact_c=R(float(1.923))*R(float(.470))
rounded_c=R(float(1.923)*float(.470))
dc=exact_c-rounded_c
qdc=Fraction.from_float(1.923)*Fraction.from_float(.470)-Fraction.from_float(1.923*.470)
def separated(a,b):
    return bool(a.upper()<b.lower() or b.upper()<a.lower())
rows=[]
for site in candidate['sites']:
    point=[R(float(v)) for v in site['center']]
    checked=model.rhs(point)
    y=[m.J(v,index=i) for i,v in enumerate(point)]
    t=model.temperature(y)
    ne=model.nh*y[0]+model.nhe*(y[1]+2*y[2])
    upper=[model.nh*y[0],model.nhe*y[1],model.nhe*y[2]]
    correction=m.J(0)
    for a in [0,2]:
        l=R(float([315614,570670,1263030][a]))/t
        u=(l/R(float(.522))).power(.470)
        alpha=R(float(2 if a==2 else 1))*R(float(1.269e-13))*l.power(1.503)/(1+u).power(1.923)
        dg=dc*u/(1+u)
        correction=correction-upper[a]*ne*model.kb*t*alpha*dg/(model.nh*model.ev)
    expected=checked[3]+correction
    disjoint=separated(checked[3].v,expected.v)
    assert dc.lower()>0 or dc.upper()<0
    assert disjoint, 'probe did not discriminate'
    rows.append({'site':site['id'], 'checked_w_rhs':str(checked[3].v),
      'checked_w_interval_diameter':str(checked[3].v.absolute_diameter()),
      'exact_candidate_w_rhs_minus_checker':str(correction.v),
      'exact_candidate_w_rhs_disjoint_from_checker':disjoint,
      'gradient_entries_disjoint':sum(separated(checked[3].g[i],expected.g[i]) for i in range(7)),
      'hessian_entries_disjoint':sum(separated(checked[3].h[i,j],expected.h[i,j]) for i in range(7) for j in range(7))})
after=hashes(); assert before==after
print(json.dumps({'task_id':'REI-F04','run_id':'REI-F04-CERT-REVIEW-20261005',
  'launch_id':'cl_65ce3f36f04cd69e06e8c0d422943453',
  'child_id':'01a1081a-0390-77e2-9a44-77872659ea05',
  'head':'890439782b940af8e9017f65de06f70150669a83',
  'interpreter':sys.executable,'python':platform.python_version(),
  'sage_interval_field':str(R),'checker_sha256':before['.cuh/fastest-track/REI-F04-CERT/checker.py'],
  'coefficient_delta_exact_rational':str(qdc),'coefficient_delta_mpfi':str(dc),
  'source':str(Path(__file__)), 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'rows':rows,'frozen_scope_hashes_before':before,'frozen_scope_hashes_after':after},indent=2))
