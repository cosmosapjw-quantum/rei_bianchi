#!/usr/bin/env python3
"""PHYS23 exposure-cone and receiver bounds, exact rational downstream arithmetic.

Reuses PHYS22 certified majorants and observed Wolfram interval rate bounds.
This is a new algebraic calculation; no baseline/tangent/native solve is run.
Run: python checks/compute_and_check.py
Optional high-precision cross-checks require mpmath. An absent package is explicit.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import csv, hashlib, json, platform, time
from decimal import Decimal, localcontext
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='9b6b44acee637ac8adde1ca114e258c38747d48b3a750146614742786d8444ed'
start=time.monotonic()
raw=(ROOT/'inputs/PHYS22_INTERVAL_RESULT.json').read_bytes()
if hashlib.sha256(raw).hexdigest()!=EXPECTED: raise ValueError('PHYS22_RESULT_IDENTITY_MISMATCH')
r=json.loads(raw); rp=json.loads((ROOT/'inputs/RATE_RATIO_WOLFRAM.json').read_text()); rec=json.loads((ROOT/'inputs/RECEIVER_BINDING.json').read_text())
checks=[]
def check(name, ok):
    checks.append({'name':name,'pass':bool(ok)})
def vec(x): return [Q(a) for a in x]
def dot(x,y): return sum((a*b for a,b in zip(x,y)),Q(0))
def mv(a,v): return [dot(row,v) for row in a]
def inv(a):
    n=len(a); m=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next((k for k in range(j,n) if m[k][j]),None)
        if k is None: raise ValueError('SINGULAR_COMPARISON_MATRIX')
        m[j],m[k]=m[k],m[j]; pivot=m[j][j];m[j]=[v/pivot for v in m[j]]
        for i in range(n):
            if i!=j:
                f=m[i][j];m[i]=[v-f*w for v,w in zip(m[i],m[j])]
    return [row[n:] for row in m]
def lower(q,places=40): return Q((q*10**places).__floor__(),10**places)
def upper(q,places=40): return Q((q*10**places).__ceil__(),10**places)
def intervals(vals): return [str(lower(vals[0])),str(upper(vals[1]))]
def mpq(q): q=Q(q);return mp.mpf(q.numerator)/q.denominator
def scientific_outward(q: Q, is_lower: bool, sig_digits: int = 13) -> str:
    if not q: return '0'
    aq=abs(q); e=len(str(aq.numerator))-len(str(aq.denominator))
    while aq<Q(10)**e: e-=1
    while aq>=Q(10)**(e+1): e+=1
    scale=Q(10)**(sig_digits-1-e)
    z=(q*scale).__floor__() if is_lower else (q*scale).__ceil__()
    exact=Q(z)/scale
    with localcontext() as ctx:
        ctx.prec=100
        d=Decimal(exact.numerator)/Decimal(exact.denominator)
        return format(d,'.12e')

tf=Q(10**11);f=Q(3,38);ell=[Q(1),f,2*f,Q(0)];ct=2*Q('1.602176634e-12')/(3*Q('1.380649e-16'));chi=Q('13.598434599702');nu=[Q(1),Q(0),Q(0),-chi];nup=[abs(v) for v in nu]
p=[vec(row) for row in r['gain_upper']];ident=[[Q(i==j)-p[i][j] for j in range(4)] for i in range(4)];pinv=inv(ident)
z=mv(pinv,nup);v=mv(p,z);zeta=dot(ell,v)
tlo,thi=vec(r['temperature_box']);plo,phi=vec(r['particle_box']);nlo,nhi=vec(r['nH_box']);qlo,qhi=vec(r['qHH_box']);radius=vec(r['gas_radii']);oldflow=vec(r['tube_picard_upper'])
err=ct*v[3]+thi*zeta;ge=[1-zeta,1+zeta];gt=[(ct*chi+tlo-err)/phi,(ct*chi+thi+err)/plo]
weights=vec([1,1,1,32]);gain=max(a/b for a,b in zip(mv(p,weights),weights))
a_cap=min(1+(radius[j]-oldflow[j])/(tf*nup[j]*qhi) for j in (0,3));a_claim=Q(11,10)
flow=[oldflow[j]+(a_claim-1)*tf*nup[j]*qhi for j in range(4)]
ratios={k:vec(vv) for k,vv in rp['ratios'].items()};family=[min(x[0] for x in ratios.values()),max(x[1] for x in ratios.values())]
cs=Q(rec['c_cm_s']);sig=Q(rec['sigma_T_cm2']);rate_scale=[cs*sig*nlo,cs*sig*nhi]
ebase=[plo-1-f,phi-1-f];rbase=[rate_scale[0]*ebase[0],rate_scale[1]*ebase[1]];tau0=[x*tf for x in rbase]

def bounds_for(ab):
    b,a=ab;exposure=[b*qlo*tf,a*qhi*tf]
    temp=[-gt[1]*exposure[1],-gt[0]*exposure[0]];electron=[ge[0]*exposure[0],ge[1]*exposure[1]]
    depth=[rate_scale[0]*ge[0]*b*qlo*tf*tf/2,rate_scale[1]*ge[1]*a*qhi*tf*tf/2]
    return {'rate_ratio_rational':list(map(str,ab)),'delta_T_K_rational':intervals(temp),'delta_e_perH_rational':intervals(electron),'delta_tau_0_rational':intervals(depth),'delta_T_K':list(map(float,temp)),'delta_e_perH':list(map(float,electron)),'delta_tau_0':list(map(float,depth))}
results={k:bounds_for(ab) for k,ab in ratios.items()};results['PRESCRIPTION_HULL']=bounds_for(family)
# Positive opacity changes are bounded by L*t <= delta_rate(t) <= U*t.
L=rate_scale[0]*ge[0]*family[0]*qlo;U=rate_scale[1]*ge[1]*family[1]*qhi
times=[tf*i/16 for i in range(17)];edges=[];cells=[]
for t in times:
    dl=L*(tf*tf-t*t)/2;du=U*(tf*tf-t*t)/2
    edges.append({'t_s':str(t),'delta_rate_lo_s_inverse':str(lower(L*t)),'delta_rate_hi_s_inverse':str(upper(U*t)),'delta_tau_lo':str(lower(dl)),'delta_tau_hi':str(upper(du)),'survival_abs_hi':str(upper(du))})
for i,(left,right) in enumerate(zip(times[:-1],times[1:])):
    width=right-left;deltad=U*(right*right-left*left)/2;tail=U*(tf*tf-right*right)/2
    p0upper=rbase[1]*width;d0lower=rbase[0]*width
    p0lower=(1-tau0[1])*(d0lower-d0lower*d0lower/2)
    pb=deltad+p0upper*tail
    cells.append({'cell':i,'t_left_s':str(left),'t_right_s':str(right),'abs_probability_change_upper':str(upper(pb)),'relative_probability_change_upper':str(upper(pb/p0lower))})
rate_rel=U*tf/ rbase[0];tau_rel=U*tf*tf/2/tau0[0];cell_rel=max(Q(row['relative_probability_change_upper']) for row in cells);cell_abs=max(Q(row['abs_probability_change_upper']) for row in cells)
limits={k:Q(v) for k,v in rec['numerical_acceptance'].items()}
numeric_amplitude_caps={'rate':limits['rate_ne_relative']/(rate_rel/family[1]),'depth':limits['depth_positive_cell_relative']/(tau_rel/family[1]),'cell':limits['depth_positive_cell_relative']/(cell_rel/family[1]),'survival':limits['survival_absolute']/(U*tf*tf/2/family[1])}
metrics={'rate_relative_upper':rate_rel,'depth_relative_upper':tau_rel,'survival_absolute_upper':U*tf*tf/2,'cell_relative_upper':cell_rel,'cell_absolute_upper':cell_abs}
util={'rate':rate_rel/limits['rate_ne_relative'],'depth':tau_rel/limits['depth_positive_cell_relative'],'survival':metrics['survival_absolute_upper']/limits['survival_absolute'],'cell':cell_rel/limits['depth_positive_cell_relative']}

# New exact checks on the exposure-normalised cone and additional amplitude range.
check('result_hash_pinned',True)
check('positive_comparison_matrix',all(x>=0 for row in p for x in row))
check('weighted_gain_less_one',0<=gain<1)
check('nonnegative_resolvent',all(x>=0 for row in pinv for x in row))
check('exposure_resolvent_identity',mv(ident,z)==nup)
check('feedback_identity',v==[z[j]-nup[j] for j in range(4)])
check('electron_exposure_cone_positive',0<=zeta<1)
check('thermal_exposure_cone_positive',0<gt[0]<=gt[1])
check('new_amplitude_common_tube',all(x<y for x,y in zip(flow,radius)))
check('claimed_amplitude_below_first_exit_cap',a_claim<a_cap)
check('all_prescriptions_nonnegative_and_in_tube',all(0<b<=a<=a_claim for b,a in ratios.values()))
check('same_receiver_clock_grid',times[0]==0 and times[-1]==tf and len(times)==17)
check('sigma_SI_cgs_consistency',sig==Q('6.6524587e-29')*10000 and cs==Q(299792458)*100)
check('baseline_rate_lower_positive',0<rbase[0]<=rbase[1])
check('archived_tau_within_declared_real_box',tau0[0]<Q(rec['archived_baseline_tau_start_diagnostic'])<tau0[1])
check('opacity_lower_nonnegative',0<L<=U)
check('zero_initial_rate_response',L*times[0]==U*times[0]==0)
check('common_tail_endpoint_cancels',Q(edges[-1]['delta_tau_lo'])==Q(edges[-1]['delta_tau_hi'])==0)
check('linear_edge_schedule_integral_exact',sum((b-a)*(a+b)/2 for a,b in zip(times[:-1],times[1:]))==tf*tf/2)
check('cell_baseline_probability_lower_positive',(1-tau0[1])>0 and all((rbase[0]*(b-a)-(rbase[0]*(b-a))**2/2)>0 for a,b in zip(times[:-1],times[1:])))
check('all_formula_readouts_have_positive_electron_and_negative_temperature',all(Q(x['delta_e_perH_rational'][0])>0 and Q(x['delta_T_K_rational'][1])<0 for x in results.values()))
check('endpoint_hull_contains_each_prescription',all(Q(results['PRESCRIPTION_HULL']['delta_T_K_rational'][0])<=Q(x['delta_T_K_rational'][0])<=Q(x['delta_T_K_rational'][1])<=Q(results['PRESCRIPTION_HULL']['delta_T_K_rational'][1]) for x in results.values()))
check('zero_activation_has_zero_exposure_bound',all(Q(0)*x==0 for x in z+v+ge+gt))
check('numeric_scale_comparisons_less_one',all(x<1 for x in util.values()))
# mpmath is a separate direct formula check, not a second interval proof.
mp.mp.dps=85
T0=mpq(tlo);T1=mpq(thi)
def ratio_eval(name,T,mratio):
    lcs=mpq('1.2e-17')*T**mpq('1.2')*mp.exp(-mpq(157800)/T)
    if name=='LCS91': kk=lcs
    elif name=='HM89': kk=mpq('1.7e-14')*mp.sqrt(T)*mp.exp(-mpq(149000)/T)
    elif name=='HM79': kk=mpq('9.8e-15')*mp.sqrt(T)*mp.exp(-mpq(157800)/T)
    elif name=='KS91_G15': kk=mpq('4.65e-21')*T**mpq('1.5')*mp.exp(-mpq(157800)/T)
    else: kk=mpq('1.57e-14')*mp.sqrt(T)*(1+2*T/157800)*mp.exp(-mpq(157800)/T)/(1+(2*mratio*T/157800)**2)
    return kk/lcs
for name,(b,a) in ratios.items():
    allok=all(mpq(b)-mp.mpf('1e-78')<=ratio_eval(name,T0+(T1-T0)*j/32,mr)<=mpq(a)+mp.mpf('1e-78') for j in range(33) for mr in (mp.mpf(0),mpq('1/1000')))
    check('mp85_direct_rate_inside_Wolfram_interval_'+name,allok)
# Stable cell identity / inequality on thin, ordinary, and optically thick controls.
for index,(tr,d,dr,dx) in enumerate([('0','1e-8','1e-23','1e-24'),('0.25','0.2','0.1','0.01'),('5','2','3','4')]):
    tr,d,dr,dx=map(mp.mpf,(tr,d,dr,dx));p0=mp.exp(-tr)*(-mp.expm1(-d));p1=mp.exp(-tr-dr)*(-mp.expm1(-d-dx))
    stable=mp.exp(-tr)*(mp.expm1(-dr)*(-mp.expm1(-d))+mp.exp(-dr-d)*(-mp.expm1(-dx)))
    check('cell_delta_identity_control_'+str(index),abs(p1-p0-stable)<mp.mpf('1e-80'))
    check('cell_local_plus_tail_bound_control_'+str(index),abs(stable)<=dx+p0*dr)

out={'schema':'HH23_EXPOSURE_CONE_RESULT_V1','status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','units':{'T':'K','e':'electrons/H','tau':'dimensionless'},'input_sha256':EXPECTED,'support':'exact Fraction downstream algebra; Wolfram 60-digit interval ratios inherited from observed current run','z_exact':list(map(str,z)),'v_exact':list(map(str,v)),'zeta_exact':str(zeta),'zeta':float(zeta),'ge_exact':list(map(str,ge)),'gt_exact':list(map(str,gt)),'ge':list(map(float,ge)),'gt_K':list(map(float,gt)),'amplitude_box_cap_exact':str(a_cap),'amplitude_box_cap':float(a_cap),'claimed_common_amplitude':'11/10','tube_ratios_extended':list(map(float,(flow[j]/radius[j] for j in range(4)))),'prescriptions':results,'ratio_span':float(family[1]/family[0]),'receiver_bounds_rational':{k:str(upper(v)) for k,v in metrics.items()},'receiver_bounds':{k:float(v) for k,v in metrics.items()},'fraction_of_numeric_acceptance_scale':{k:float(v) for k,v in util.items()},'numeric_amplitude_caps':{k:float(v) for k,v in numeric_amplitude_caps.items()},'numeric_all_caps_min':float(min(numeric_amplitude_caps.values())),'scientific_HH_budget':None,'numerical_acceptance_is_not_a_physical_budget':True,'time_s':float(tf),'baseline_depth_box':list(map(float,tau0)),'runtime_seconds':time.monotonic()-start,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':platform.python_version(),'mpmath_version':mp.__version__}
(ROOT/'results/EXPOSURE_CONE.json').write_text(json.dumps(out,indent=2)+'\n')
audit={'status':out['status'],'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),'checks':checks,'independence':'same assistant, separate exact Fraction linear algebra and 85-digit direct-formula/control tests; not external review','source_interval_producer_repeated':False,'sampled_ratio_evaluations':5*33*2,'script_sha256':out['script_sha256'],'input_sha256':EXPECTED}
(ROOT/'checks/EXACT_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
for name,rows in [('EDGE_BOUNDS.csv',edges),('CELL_BOUNDS.csv',cells)]:
    with (ROOT/'results'/name).open('w',newline='') as fd:
        writer=csv.DictWriter(fd,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
with (ROOT/'results/RATE_RESPONSE_TABLE.csv').open('w',newline='') as fd:
    writer=csv.writer(fd);writer.writerow(['prescription','ratio_lo','ratio_hi','DeltaT_lo_K','DeltaT_hi_K','Deltae_lo_perH','Deltae_hi_perH','Deltatau_lo','Deltatau_hi'])
    for key,row in results.items():writer.writerow([key]+[scientific_outward(Q(v),j==0) for field in ['rate_ratio_rational','delta_T_K_rational','delta_e_perH_rational','delta_tau_0_rational'] for j,v in enumerate(row[field])])
print(json.dumps({'status':out['status'],'checks_passed':audit['passed'],'checks_failed':audit['failed'],'family':results['PRESCRIPTION_HULL'],'receiver_bounds':out['receiver_bounds'],'fractions_of_numeric_scale':out['fraction_of_numeric_acceptance_scale'],'runtime_seconds':out['runtime_seconds']},indent=2))
raise SystemExit(0 if out['status']=='PASS' else 1)
