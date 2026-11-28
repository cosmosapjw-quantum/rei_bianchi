#!/usr/bin/env python3
"""Independent PHYS14 geometry/source audit. Does not import candidate code.

Exact Fraction arithmetic; exponential alternating-series enclosure; integer
square-root enclosure. These are review checks, not a source-kernel rerun.
"""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import hashlib, json, re, struct, time

ROOT = Path('/workspace/scratch/b826cbaab54f/HH_PHYS14_20261012_v1')
OUT = Path(__file__).parent
checks=[]
def ck(label, value):
    checks.append({'check':label,'pass':bool(value)})
    if not value:
        raise AssertionError(label)
def b64(s):
    return F.from_float(struct.unpack('>d',bytes.fromhex(s))[0])
def pair(d):
    return b64(d['lo_bits']), b64(d['hi_bits'])
def bracket_exp_negative(x):
    assert 0<x<1
    term=F(1); partial=term; lo=hi=None
    for k in range(1,33):
        term *= -x/F(k)
        partial += term
        if k==31: lo=partial
        if k==32: hi=partial
    assert lo<hi
    return lo,hi
def sqrt_bracket(q, bits=320):
    n=isqrt((q.numerator<<(2*bits))//q.denominator)
    den=1<<bits
    lo=F(n,den)
    hi=lo if lo*lo==q else F(n+1,den)
    assert lo*lo<=q<=hi*hi
    return lo,hi
def dyad_abs(q, upward, bits=320):
    z=q*(1<<bits)
    n=z.numerator//z.denominator
    if upward and z.denominator!=1: n+=1
    return F(n,1<<bits)
def export(z):
    return {'lo':[str(z[0].numerator),str(z[0].denominator)],
            'hi':[str(z[1].numerator),str(z[1].denominator)],
            'approx':[float(z[0]),float(z[1])]}

started=time.perf_counter()
records={}
for stage,h in [('full',1250000000),('first_half',625000000)]:
    src=ROOT/'inputs/ncp07/results'/stage
    sb=json.loads((src/'SOURCE_BOX.json').read_text())
    pre=json.loads((src/'PREBE.json').read_text())
    trace=(src/'geometry_trace.txt').read_text()
    h_leaf=b64('3d06849b86a12b9b')
    rho=bracket_exp_negative(h_leaf*h)
    ratios=re.findall(r'^ray=(\d+) ratio=([0-9a-f]{16}),([0-9a-f]{16})$',trace,re.M)
    ck(stage+' 128 ray ratio captures',len(ratios)==128)
    ck(stage+' exact-real rho lies in every captured ray interval',
       all(b64(lo)<=rho[0] and rho[1]<=b64(hi) for _,lo,hi in ratios))
    qrows=re.findall(r'^qhat ray=(\d+) .* unit=([0-9a-f]{16}),([0-9a-f]{16}),([0-9a-f]{16})$',trace,re.M)
    qmap={}
    for ray,*bits in qrows:
        q=tuple(b64(x) for x in bits)
        if int(ray) in qmap: ck(stage+' same captured q per call ray '+ray,qmap[int(ray)]==q)
        qmap[int(ray)]=q
    ck(stage+' q vectors available for 128 rays',set(qmap)==set(range(128)))
    raw=[]
    norm_defects=[]
    for ray in range(128):
        q2=sum(x*x for x in qmap[ray]); norm_defects.append(q2-1)
        nlo,nhi=sqrt_bracket(q2)
        raw.append((dyad_abs(1/nhi**3,False),dyad_abs(1/nlo**3,True)))
    total_lo=sum(z[0] for z in raw); total_hi=sum(z[1] for z in raw)
    wb=[pair(z) for z in pre['source_weights']]
    weights=[(lo/total_hi,hi/total_lo) for lo,hi in raw]
    ck(stage+' normalized exact geometry weights in stored intervals',
       all(wb[i][0]<=weights[i][0] and weights[i][1]<=wb[i][1] for i in range(128)))
    energy=[b64(z) for z in sb['energy_bits']]
    sigma=[[b64(a) for a in row] for row in sb['sigma_bits']]
    ck(stage+' 33 increasing energy nodes',len(energy)==33 and all(a<b for a,b in zip(energy,energy[1:])))
    ck(stage+' 17 active HI nodes',sum(row[0]>0 for row in sigma)==17)
    ck(stage+' helium photo channels exactly zero',all(row[1]==row[2]==0 for row in sigma))
    # All actual-rho branch assumptions used by the nonuniform remap theorem.
    rh2=(rho[0]*rho[0],rho[1]*rho[1])
    valid=[]
    for j in range(2,33):
        valid.append(energy[j-1] < rho[0]*energy[j] <= rho[1]*energy[j] < energy[j]
                     and energy[j-1] < rh2[0]*energy[j] <= rh2[1]*energy[j] < energy[j]
                     and energy[j-2] < rho[0]*energy[j-1] <= rho[1]*energy[j-1] < energy[j-1])
    # Symbolic identity is checked with arbitrary rational r satisfying each
    # branch, using actual (slightly nonuniform) captured energy nodes.
    r=F(159999,160000) if stage=='first_half' else F(79999,80000)
    algebra=[]
    for j in range(2,33):
        dj=energy[j]-energy[j-1]; dp=energy[j-1]-energy[j-2]
        aj=(1-r)*energy[j]/dj; ap=(1-r)*energy[j-1]/dp
        sequential=[(1-aj)**2,aj*(2-aj-ap),aj*ap]
        direct=[1-(1+r)*aj,(1+r)*aj,F(0)]
        defect=[sequential[i]-direct[i] for i in range(3)]
        formula=[aj*ap*dp/dj,-aj*ap*(1+dp/dj),aj*ap]
        algebra.append(defect==formula and sum(defect)==0 and sum(energy[j-i]*defect[i] for i in range(3))==0)
    ck(stage+' nonuniform remap defect identity, number and energy moments',all(algebra))
    records[stage]={'rho':export(rho),'max_abs_squared_q_norm_defect':float(max(abs(z) for z in norm_defects)),
        'geometric_weight_bounds_in_original_source':True,
        'remap_theorem_branch_columns_at_stage_rho':[j+2 for j,x in enumerate(valid) if x],
        'remap_formula_checked_columns':31,
        'source_box_sha256':hashlib.sha256((src/'SOURCE_BOX.json').read_bytes()).hexdigest()}

result={'schema':'PHYS14_INDEPENDENT_GEOMETRY_REVIEW_V1','role':'independent decision reviewer',
        'candidate_imports':0,'candidate_executions':0,'source_kernel_replays':0,
        'scope':'inherited source geometry specialization and exact algebra, not next-stage numerical decision',
        'checks':checks,'assertion_count':len(checks),'assertions_are_scientific_cases':False,
        'records':records,'wall_seconds':time.perf_counter()-started}
(OUT/'GEOMETRY_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks),'wall_seconds':result['wall_seconds'],
                  'first_half_remap_branch_columns':records['first_half']['remap_theorem_branch_columns_at_stage_rho']}))
