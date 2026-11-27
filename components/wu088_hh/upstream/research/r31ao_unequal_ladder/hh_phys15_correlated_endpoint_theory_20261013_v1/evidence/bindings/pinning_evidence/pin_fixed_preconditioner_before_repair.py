#!/usr/bin/env python3
"""Pin the original stored Full preconditioner; no source/root execution."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime, timezone
import hashlib, json, struct, zipfile

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
OLD=WORK/'phys14_intake/ncp07/HH_PHYS07_NCP_LOCAL_20261011_v1'
BASE=WORK/'HH_PHYS14_20261012_v1'
ARCHIVE=WORK/'phys14_intake/WU088_HH_PHYS07_NCP_LOCAL_20261011_v1.zip'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qbits(s):return Q(struct.unpack('>d',bytes.fromhex(s))[0])
def iv(x):return qbits(x['lo_bits']),qbits(x['hi_bits'])
def eq(x):return [str(x.numerator),str(x.denominator)]
def scalar(x):
    return {'binary64_value':x,'bits':struct.pack('>d',x).hex(),'exact':eq(Q(x))}
def identity(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}

rel='results/full/UNIFORM_ARITHMETIC.json'
old=OLD/rel
member='HH_PHYS07_NCP_LOCAL_20261011_v1/'+rel
manifest=read(OLD/'MANIFEST.json')
row=next(x for x in manifest['files'] if x['path']==rel)
with zipfile.ZipFile(ARCHIVE) as z:
    matches=[i for i in z.infolist() if i.filename==member]
    assert len(matches)==1
    payload=z.read(matches[0])
assert len(payload)==row['bytes'] and hashlib.sha256(payload).hexdigest()==row['sha256']
assert payload==old.read_bytes()
target=HERE/'extra_inputs'/rel
target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():assert target.read_bytes()==payload
else:
    with target.open('xb') as f:f.write(payload)

arith=read(target)
diag=read(BASE/'inputs/ncp07/results/full/UNIFORM_DIAGNOSTICS.json')
box=read(BASE/'inputs/ncp07/results/full/SOURCE_BOX.json')
centre=read(BASE/'inputs/ncp07/results/full/SOURCE_CENTRE.json')
C=[[Q(v) for v in r] for r in arith['fixed_C']]
scales=[Q(v) for v in arith['radius']]
assert arith['radius']==diag['radius'] and arith['center']==diag['center']
assert arith['status']=='CONDITIONAL_ROOT_ARITHMETIC_PASS'
# Small exact rational recomposition of stored matrix intervals, not a root run.
mag_rows=[]
component_checks=[]
for i in range(4):
    row=[]
    for j in range(4):
        lo=hi=Q(int(i==j))
        for k in range(4):
            a,b=iv(box['A_Gg'][k][j]); products=[C[i][k]*a,C[i][k]*b]
            lo-=max(products);hi-=min(products)
        mag=max(abs(lo),abs(hi)); row.append(mag)
        assert mag<=iv(arith['B'][i][j])[1]
        component_checks.append({'row':i,'column':j,'exact_interval_magnitude_lte_stored_B':True})
    mag_rows.append(sum(row[j]*scales[j]/scales[i] for j in range(4)))
q_exact=max(mag_rows)
q_arith=iv(arith['q'])[1]
q_diag=iv(diag['q'])[1]
assert q_exact<=q_arith<1
stored_B_scaled_rows=[sum(iv(arith['B'][i][j])[1]*scales[j]/scales[i] for j in range(4)) for i in range(4)]
assert max(stored_B_scaled_rows)<=q_arith

midpoints=[]
for rowc in centre['A_Gg']:
    r=[]
    for a in rowc:
        lo=float.fromhex(struct.unpack('>d',bytes.fromhex(a['lo_bits']))[0].hex())
        hi=float.fromhex(struct.unpack('>d',bytes.fromhex(a['hi_bits']))[0].hex())
        r.append(scalar(lo+(hi-lo)/2.0))
    midpoints.append(r)

binding={
 'schema':'WU088_HH_PHYS15_FIXED_PRECONDITIONER_BINDING_V1',
 'created_at_utc':datetime.now(timezone.utc).isoformat(),
 'decision':'REUSE_ORIGINAL_FULL_C_AND_UNIFORM_ARITHMETIC_Q',
 'stored_preconditioner':identity(target),
 'archive_binding':{'archive_path':str(ARCHIVE),'archive_sha256':'4ea6b7dbbc714493ac85f944a65a353a1ee75abf5742c3e7ce65a7df56cc3465','archive_identity_reused_from':'BINDINGS.json/newly_restored_inputs/archive','member':member,'member_sha256':row['sha256'],'member_bytes':row['bytes'],'original_manifest_match':True,'existing_intake_match':True},
 'C':[[scalar(v) for v in r] for r in arith['fixed_C']],
 'S_diagonal':list(map(scalar,arith['radius'])),
 'gas_centre':list(map(scalar,arith['center'])),
 'q_primary':{'source':'extra_inputs/results/full/UNIFORM_ARITHMETIC.json/q','value':arith['q'],'meaning':'sup over original whole X x [0,1]^2, with same fixed alpha: ||S^-1 (I-C D_g H_F) S||_infty <= q <1'},
 'B_primary':{'source':'extra_inputs/results/full/UNIFORM_ARITHMETIC.json/B','value':arith['B'],'meaning':'Component upper bounds for abs(I-C D_g H_F), all entries stored as point intervals at outward magnitudes.'},
 'q_secondary_do_not_substitute':{'source':'HH_PHYS14_20261012_v1/inputs/ncp07/results/full/UNIFORM_DIAGNOSTICS.json/q','value':diag['q'],'reason':'Same C; sourcebox.rs accumulates successive subtractions of each CA contribution. uniform.rs first computes outward CA matrix product then subtracts from I. These two interval arithmetic graphs yield slightly different valid upper bounds.'},
 'residual':'H_F(g;alpha,lambda,b)=g-g0-2h F_F(g;alpha,lambda,b)',
 'domain':{'X_source':'HH_PHYS14_20261012_v1/inputs/ncp07/results/full/C2_DOMAIN.json/X','parameter_rectangle':[[0,1],[0,1]],'coordinates':['x_HII','y_HeII','y_HeIII','w_eV_per_H'],'coefficient_choice':'One underlying fixed-coefficient source family; restrict to PHYS14 linked geometric subfamily without changing C or q.','centre_parameters':'The Jacobian at the fixed gas centre is enclosed over whole Theta; no lambda,b centre source call is used.'},
 'definition':{'sourcebox':'src/sourcebox.rs::uniform defines jc[i][j]=v.lo+(v.hi-v.lo)/2 from center_src.residual[i].gradient[j], then calls FixedC::from_center once.','source_midpoint_matrix':midpoints,'uniform':'src/uniform.rs::FixedC::from_center forms [jc|I], uses partial pivoting with first-row tie preference, normalizes each pivot row left-to-right j=0..7, then eliminates other rows left-to-right. Returned right 4x4 binary64 matrix is exported as fixed_C.','exact_mathematical_C':'Each exported shortest-roundtrip decimal is parsed to the original binary64, then treated as its exact dyadic rational. C is a fixed approximate inverse, not redefined as the exact inverse of jc.','needed_reconstruction':'None: fixed_C is stored. A different rational matrix inverse or reordered floating inverse would define another preconditioner and require its own bound.'},
 'targeted_rational_check':{'status':'pass_scoped','method':'Exact Fraction products of stored C and original whole-X SOURCE_BOX A_Gg intervals; no source callback or root solve.','sixteen_component_B_inclusions':component_checks,'exact_weighted_row_sums':[eq(v) for v in mag_rows],'exact_q_upper_from_stored_A':eq(q_exact),'exact_stored_B_weighted_rows':[eq(v) for v in stored_B_scaled_rows],'bounded_by_primary_q':True},
 'input_identities':[identity(p) for p in [OLD/'src/uniform.rs',BASE/'inputs/ncp07/src/sourcebox.rs',BASE/'inputs/ncp07/results/full/SOURCE_BOX.json',BASE/'inputs/ncp07/results/full/SOURCE_CENTRE.json',BASE/'inputs/ncp07/results/full/UNIFORM_DIAGNOSTICS.json',BASE/'inputs/ncp07/results/full/C2_DOMAIN.json']],
 'execution':{'new_source_calls':0,'new_root_calls':0,'new_history_runs':0,'cloud_writes':0,'work':'One stored member extraction and sixteen exact rational matrix interval products.'}}
(HERE/'FIXED_PRECONDITIONER_BINDING.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'stored_C_sha256':row['sha256'],'q_primary':arith['q']['hi'],'q_secondary':diag['q']['hi'],'B_inclusions':16,'norm_lte_q':True,'files':['extra_inputs/results/full/UNIFORM_ARITHMETIC.json','FIXED_PRECONDITIONER_BINDING.json']},indent=2))
