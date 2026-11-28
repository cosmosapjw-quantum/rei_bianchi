"""Independent source/jet checks: scalar evaluations and formal coefficients only."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, '/workspace/scratch/198b9c7581be/deps')
ROOT = Path('/workspace/scratch/198b9c7581be/HH_PHYS02_20261010_v1')
sys.path.insert(0, str(ROOT/'src'))
from flint import arb, ctx
import mpmath as mp
import sympy as sp
from frozen_source import FrozenSource
from jet_algebra import HD, flow_jet

ctx.prec = 256
mp.mp.dps = 110
checks = []

def f(x):
    p, q = float(x).as_integer_ratio()
    return mp.mpf(p)/q

def check(test_id, condition, details=None):
    checks.append({'id':test_id, 'pass':bool(condition), 'details':details})
    assert condition, test_id

def close_ball(got, ref):
    # Compare the independent 110-digit scalar to exact Arb dyadic endpoints.
    # Re-enclosing the scalar in Arb at the same 256-bit precision needlessly
    # tests containment of a second roundoff ball, rather than the reference.
    ml,el=(int(a) for a in got.lower().man_exp())
    mu,eu=(int(a) for a in got.upper().man_exp())
    return mp.mpf(ml)*mp.power(2,el) <= ref <= mp.mpf(mu)*mp.power(2,eu)

def independent_rates(t):
    """Direct literal transcription of ft03_rates.rs, independent of candidate."""
    lam = [f(315614)/t, f(570670)/t, f(1263030)/t]
    al, gg, be = [mp.mpf(0)]*3, [mp.mpf(0)]*3, []
    for a in range(3):
        if a == 1:
            al[a] = f(3e-14)*mp.power(lam[a],f(.654))
            gg[a] = f(-.654)
        else:
            u = mp.power(lam[a]/f(.522),f(.470))
            al[a] = f(2 if a==2 else 1)*f(1.269e-13)*mp.power(lam[a],f(1.503))/mp.power(1+u,f(1.923))
            gg[a] = f(-1.503)+f(1.923)*f(.470)*u/(1+u)
        be.append(f([21.11,32.38,19.95][a])*mp.power(t,f(-1.5))*mp.exp(-lam[a]/2)
            *mp.power(lam[a],f([-1.089,-1.146,-1.089][a]))
            /mp.power(1+mp.power(lam[a]/f([.354,.416,.553][a]),f([.874,.987,.735][a])),f([1.101,1.056,1.275][a])))
    kinetic = [f(1.380649e-16)*t*al[a]*(f(1.5)+gg[a]) for a in range(3)]
    amp = f(1.54e-9)*mp.power(f(11605),f(1.5))
    b1, b2 = f(40.49664394833662)*f(11605), f(8.099328789667)*f(11605)
    dr = [amp*mp.power(t,f(-1.5))*mp.exp(-b1/t), f(.3)*amp*mp.power(t,f(-1.5))*mp.exp(-(b1+b2)/t)]
    de = [f(1.380649e-16)*b1, f(1.380649e-16)*(b1+b2)]
    return al,kinetic,be,dr,de

def independent_rhs(d,z,lam,s):
    """Evaluate per-cm3 gas events first, then normalize (original Rust route)."""
    nh,nhe,c,kb,ev = f(d['n_h_cm3']),f(d['n_he_cm3']),f(29979245800),f(1.380649e-16),f(1.602176634e-12)
    x,a,b,w = z[:4]
    ne = nh*x+nhe*(a+2*b)
    thermal_vol = w*nh*ev
    t = 2*thermal_vol/(3*kb*(nh+nhe+ne))
    al,kin,be,dr,de = independent_rates(t)
    low = [nh*(1-x),nhe*(1-a-b),nhe*a]
    high = [nh*x,nhe*a,nhe*b]
    ci = [low[k]*ne*be[k] for k in range(3)]
    rr = [high[k]*ne*al[k] for k in range(3)]
    j = [ci[k]-rr[k] for k in range(3)]
    thresholds = list(map(f,[13.598434599702,24.587389011,54.41776]))
    du = -sum(ci[k]*thresholds[k]*ev+high[k]*ne*kin[k] for k in range(3))
    for k in range(2):
        event = high[1]*ne*dr[k]
        j[1] -= event
        du -= event*de[k]
    out = [j[0]/nh,(j[1]-j[2])/nhe,j[2]/nhe,du/(nh*ev)-2*f(d['h_mean_per_s'])*w]
    active = [k for k,sig in enumerate(d['sigma_cm2']) if sig[0] != 0]
    dp=[]
    for p,k in zip(z[4:],active):
        rate = c*nh*(1-x)*f(d['sigma_cm2'][k][0])*p
        out[0] += rate
        out[3] += rate*(f(d['energies_ev'][k])-thresholds[0])
        dp.append(-rate+(s*f(5e-15) if k==d['varied_energy_index'] else 0))
    q=nh*(1-x)*(1-x)*f(1.2e-17)*mp.power(t,f(1.2))*mp.exp(-f(157800)/t)
    out[0] += lam*q
    out[3] -= thresholds[0]*lam*q
    return [v*1250000000 for v in out+dp],t

model=FrozenSource(ROOT/'inputs/SELECTED_SOURCE.json')
d=model.data
check('SOURCE_ALL_25_PHOTON_BINS_ACCOUNTED', len(model.active)==9 and len(model.inert)==16 and sorted(model.active+model.inert)==list(range(25)))
check('SOURCE_RECORDED_NHE_BINARY64_PRODUCT', d['n_he_cm3']==d['n_h_cm3']*d['f_he'])
source_files=['SELECTED_SOURCE.json']+['source/'+p for p in ['ft03_rates.rs','ft03_controlled.rs','hhe_events.rs','coupled_primary.rs','hh_primary_extension.rs']]
parent=Path('/workspace/scratch/198b9c7581be/inputs/phys01/HH_PHYS01_20261010_v1/inputs')
for p in source_files:
    check('SOURCE_IDENTITY_'+p,(ROOT/'inputs'/p).read_bytes()==(parent/p).read_bytes())

for i,(fractions,temp,scale,lam,s) in enumerate([
    ([.1,.2,.3],35050,.7,.25,.1),
    (d['old_gas'][:3],49489.0775,1,.7,.3),
    ([.75,.1,.85],59950,1.3,1,.9)]):
    nh,nhe=f(d['n_h_cm3']),f(d['n_he_cm3'])
    x,a,b=map(f,fractions)
    ne=nh*x+nhe*(a+2*b)
    w=float(f(1.5)*f(1.380649e-16)*f(temp)*(nh+nhe+ne)/(nh*f(1.602176634e-12)))
    vals=list(fractions)+[w]+[d['old_point_photons'][k]*scale for k in model.active]
    reference,t=independent_rhs(d,list(map(f,vals)),f(lam),f(s))
    obtained=model.rhs(list(map(arb,vals)),arb(lam),arb(s))
    for j,(got,want) in enumerate(zip(obtained,reference)):
        check(f'RHS_PER_CM3_ROUTE_STATE{i}_COMPONENT{j}', close_ball(got,want))
    wanted_rates=independent_rates(t)
    got_rates=model.coefficients(model.thermal(list(map(arb,vals)))[0])
    for k,(got_group,ref_group) in enumerate(zip(got_rates,wanted_rates)):
        for j,(got,want) in enumerate(zip(got_group,ref_group)):
            # Candidate represents kinetic and DR energies in eV; original is erg.
            if k in [1,4]: want /= f(1.602176634e-12)
            check(f'RATE_STATE{i}_GROUP{k}_COMPONENT{j}',close_ball(got,want))

# Generic nonlinear 2-vector formal flow with nonzero initial sensitivity seeds.
y0,y1,L,S=sp.symbols('y0 y1 L S')
F=sp.Matrix([L*y0+y0*y1+S, -y1**2+L*S])
flow=[sp.Matrix([y0,y1])]
for n in range(4):
    flow.append(sp.simplify(flow[-1].jacobian([y0,y1])*F/(n+1)))
init=[sp.Rational(1,2)+2*L+3*S+5*L*S,sp.Rational(2,3)-L+2*S-3*L*S]
where={L:sp.Rational(1,3),S:sp.Rational(2,5)}
def ar(q):
    q=sp.Rational(q)
    return arb(int(q.p))/arb(int(q.q))
seeds=[]
for expr in init:
    seeds.append(HD(ar(expr.subs(where)),ar(sp.diff(expr,L).subs(where)),ar(sp.diff(expr,S).subs(where)),ar(sp.diff(expr,L,S).subs(where))))
def field(y,l,s):
    return [l*y[0]+y[0]*y[1]+s,-y[1]**2+l*s]
got=flow_jet(field,seeds,HD(ar(where[L]),1),HD(ar(where[S]),0,1),4)
for n in range(5):
    for j in range(2):
        expr=flow[n][j].subs({y0:init[0],y1:init[1]},simultaneous=True)
        wants=[expr,sp.diff(expr,L),sp.diff(expr,S),sp.diff(expr,L,S)]
        for k,want in enumerate(wants):
            check(f'FORMAL_FLOW_ORDER{n}_COMPONENT{j}_DERIVATIVE{k}',(got[j].a[n].c[k]-ar(want.subs(where))).contains(0))

v=sp.symbols('v')
expr=sp.exp(v)*v**sp.Rational(*float(1.7).as_integer_ratio())/(1+v)
hd=HD(arb(2),3,5,7)
got=hd.exp()*hd**arb(1.7)/(1+hd)
vals=[expr.subs(v,2),3*sp.diff(expr,v).subs(v,2),5*sp.diff(expr,v).subs(v,2),7*sp.diff(expr,v).subs(v,2)+15*sp.diff(expr,v,2).subs(v,2)]
for k,want in enumerate(vals):
    check(f'HD_COMPOSITE_NONZERO_SEED_DERIVATIVE{k}',got.c[k].contains(arb(str(sp.N(want,100)))))

result={'status':'ALL_INDEPENDENT_BOUNDED_CHECKS_PASSED','checks':checks,'count':len(checks),
    'source_reference':'independent 110-digit mpmath per-cm3 route from Rust source, not a native run or interval certificate',
    'formal_reference':'SymPy exact rational Lie derivatives; nonzero initial lambda/source/mixed seeds',
    'candidate_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/frozen_source.py','src/jet_algebra.py','bound_remainder.py','SCIENTIFIC_CONTRACT.md']},
    'scientific_native_runs':0,'IVP_trajectories':0,'BE_roots':0,'parent_cubic_reaudited':False}
(Path(__file__).parent/'SOURCE_AUDIT_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','count','candidate_sha256']},indent=2))
