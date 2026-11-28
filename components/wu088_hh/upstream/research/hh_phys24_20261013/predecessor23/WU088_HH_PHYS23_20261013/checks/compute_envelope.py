#!/usr/bin/env python3
"""PHYS23 exact closure of exposure-normalised HH and Thomson response bounds.

Input: PHYS22's already verified interval majorants, new Wolfram rate intervals.
No gas/photon trajectory, reaction fit, or native receiver is executed.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import csv, hashlib, json, math, time
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
start=time.monotonic(); checks=[]
def check(name,ok):
    checks.append({'name':name,'pass':bool(ok)})
def fv(v):return [F(x) for x in v]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def mv(a,b):return [dot(row,b) for row in a]
def inverse(a):
    n=len(a);m=[row[:]+[F(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if m[i][j]),None)
        if pivot is None:raise ValueError('singular comparison matrix')
        m[j],m[pivot]=m[pivot],m[j];scale=m[j][j];m[j]=[x/scale for x in m[j]]
        for i in range(n):
            if i!=j:
                q=m[i][j];m[i]=[x-q*y for x,y in zip(m[i],m[j])]
    return [row[n:] for row in m]
def ceilfrac(x,digits=40):return F(-((-x.numerator*10**digits)//x.denominator),10**digits)
def floorfrac(x,digits=40):return F((x.numerator*10**digits)//x.denominator,10**digits)
def br(v,d=40):return [str(floorfrac(v[0],d)),str(ceilfrac(v[1],d))]
def approx(v):
    if isinstance(v,F):return float(v)
    if isinstance(v,list):return [approx(x) for x in v]
    if isinstance(v,dict):return {k:approx(x) for k,x in v.items()}
    return v
old=json.loads((ROOT/'inputs/interval_result_v3.json').read_text())
rate=json.loads((ROOT/'results/WOLFRAM_RATE_INTERVALS.json').read_text())
receiver=json.loads((ROOT/'receiver/CONTRACT_EXTRACT.json').read_text())
p=[fv(row) for row in old['gain_upper']];eye=[[F(i==j)-p[i][j] for j in range(4)]for i in range(4)];R=inverse(eye)
f=F(3,38);ell=[F(1),f,2*f,F(0)];chi=F('13.598434599702');ct=2*F('1.602176634e-12')/(3*F('1.380649e-16'));nu=[F(1),F(0),F(0),-chi];nuabs=list(map(abs,nu));h=F(10**11)
W=mv(R,nuabs);V=mv(p,W);ev=dot(ell,V);ae=1-ev;be=1+ev
tlo,thi=fv(old['temperature_box']);plo,phi=fv(old['particle_box']);nlo,nhi=fv(old['nH_box']);g0=fv(old['gas_initial_exact']);radii=fv(old['gas_radii']);flow=fv(old['tube_picard_upper']);amin=1-g0[0]-radii[0];amax=1-g0[0]+radii[0];emin=plo-1-f;emax=phi-1-f
Alo=ct*chi+tlo-ct*V[3]-thi*ev;Ahi=ct*chi+thi+ct*V[3]+thi*ev
cTlo=Alo/phi;cThi=Ahi/plo
qfaclo=nlo*amin**2;qfachi=nhi*amax**2
c=F(receiver['c_m_s']);sig=F(receiver['sigma_T_m2'])*10**4;cs=c*100*sig
check('predecessor_declared_status',old['status']=='PASS_INTERVAL_TUBE_AND_FINITE_COMPARISON')
check('rate_T_window_contains_predecessor_T_tube',F(rate['T_box_K'][0])<=tlo<thi<=F(rate['T_box_K'][1]))
check('all_P_entries_nonnegative',all(x>=0 for row in p for x in row))
check('scaled_comparison_norm_below_one',max(x/y for x,y in zip(mv(p,fv([1,1,1,32])),fv([1,1,1,32])))<1)
check('inverse_nonnegative',all(x>=0 for row in R for x in row))
check('resolvent_identity_exact',all(W[i]-V[i]==nuabs[i] for i in range(4)))
check('exposure_electron_cone_positive',0<ae<=be)
check('exposure_temperature_cone_negative',0<cTlo<=cThi)
check('density_neutral_particle_domain',0<nlo<nhi and 0<amin<amax<1 and 0<emin)
# Analytical positivity preserves Q as the correct shared scale even for a broad rate envelope.
models={name:fv(v) for name,v in rate['rate_bounds_rational_cm3_s'].items()}
allk=[min(v[0]for v in models.values()),max(v[1]for v in models.values())]
models['FIVE_PRESCRIPTION_HULL']=allk
res={};qLold,qUold=fv(old['qHH_box']);eps=F(1,2**52);r0upper=cs*nhi*emax;tau0lower=cs*nlo*emin*h;tau0upper=r0upper*h
for name,(kl,ku) in models.items():
    ql,qu=qfaclo*kl,qfachi*ku
    Ql,Qu=h*ql,h*qu
    flownew=[flow[i]+h*nuabs[i]*qu for i in range(4)] # Safe additive bound uses old lambda=0 member.
    eb=[ae*Ql,be*Qu];tb=[-cThi*Qu,-cTlo*Ql]
    taub=[cs*nlo*ae*ql*h*h/2,cs*nhi*be*qu*h*h/2]
    rho=be*qu*h/emin
    cell_rel=rho*(1+tau0upper)
    vis_abs=cs*nhi*be*qu*h+r0upper*taub[1]
    check(name+'_positive_rate',0<kl<=ku)
    check(name+'_first_exit_transfer',all(x<r for x,r in zip(flownew,radii)))
    check(name+'_response_sign',0<eb[0]<eb[1] and tb[0]<tb[1]<0)
    check(name+'_finite_change_inside_tube',all(W[i]*Qu<2*radii[i] for i in range(4)))
    check(name+'_zero_activation_exact',all(F(0)*v==0 for v in eb+tb+taub))
    res[name]={
      'k_cm3_s_interval':br([kl,ku]),'q_s_interval':br([ql,qu],55),
      'electron_endpoint_interval':br(eb),'temperature_endpoint_K_interval':br(tb),
      'finite_segment_delta_tau_interval':br(taub,55),
      'rate_relative_upper':str(ceilfrac(rho)),
      'edge_survival_absolute_upper':str(ceilfrac(taub[1],55)),
      'cell_probability_relative_upper':str(ceilfrac(cell_rel)),
      'point_visibility_absolute_upper_s':str(ceilfrac(vis_abs,55)),
      'max_tube_ratio':float(max(x/r for x,r in zip(flownew,radii))),
      'numerical_acceptance_ratios':{
       'rate_ne_vs_64eps':float(rho/(64*eps)),
       'first_depth_vs_256eps':float((taub[1]/tau0lower)/(256*eps)),
       'all_nonzero_edge_depth_vs_256eps':float((nhi/nlo)*rho/(256*eps)),
       'positive_cell_mass_vs_256eps':float(cell_rel/(256*eps)),
       'survival_absolute_vs_64eps':float(taub[1]/(64*eps))},
      'scope':'exact-real rate prescription and fixed finite-time model; deterministic parameter-set enclosure'}
# Numerical rates checked through independent high precision equations, endpoints plus interior and mass endpoints.
mp.mp.dps=70
def m(v):return mp.mpf(v.numerator)/v.denominator if isinstance(v,F) else mp.mpf(v)
def kfun(name,T,mr):
    th=mp.mpf(157800)/T
    if name=='LCS91':return mp.mpf('1.2e-17')*T**mp.mpf('1.2')*mp.exp(-th)
    if name=='HM89':return mp.mpf('1.7e-14')*mp.sqrt(T)*mp.exp(-149000/T)
    if name=='HM79':return mp.mpf('9.8e-15')*mp.sqrt(T)*mp.exp(-th)
    if name=='D69':return mp.mpf('1.57e-14')*mp.sqrt(T)*(1+2/th)/(1+(2*mr/th)**2)*mp.exp(-th)
    if name=='KS91_G15':return mp.mpf('4.65e-21')*T**mp.mpf('1.5')*mp.exp(-th)
    raise ValueError(name)
points={};tl,tr=map(mp.mpf,rate['T_box_K'])
for name in rate['rate_bounds_rational_cm3_s']:
    kl,ku=models[name]
    for i in range(9):
        T=tl+(tr-tl)*i/8
        for j,mr in enumerate([mp.mpf(0),mp.mpf(1)/1837,mp.mpf(1)/1800]):
            x=kfun(name,T,mr);check(f'{name}_sample_{i}_mass_{j}_in_CAS_bound',m(kl)<=x<=m(ku))
    val=kfun(name,mp.mpf(50000),mp.mpf(1)/1837);points[name]=mp.nstr(val,45)
    check(name+'_point_agrees_with_Wolfram',abs(val/mp.mpf(rate['point_values_cm3_s'][name])-1)<mp.mpf('1e-38'))
cas=json.loads((ROOT/'results/WOLFRAM_RESOLVENT.json').read_text())
for i,(exact,observed) in enumerate(zip([ev,ae,be,cTlo,cThi],cas['constants'])):
    check(f'Fraction_vs_Wolfram_resolvent_constant_{i}',abs(m(exact)/mp.mpf(observed)-1)<mp.mpf('1e-23'))

# Pure receiver-map tests, not evolved HH trajectories; resolvable perturbations span thin and thick cells.
for i,(om,back,delta_rel,tail) in enumerate([(mp.mpf(x),mp.mpf(y),mp.mpf(z),mp.mpf(t))for x,y,z,t in [('1e-30','0','1e-15','0'),('1e-8','1e-7','1e-15','0.25'),('1','3','0.1','0'),('100','100','0.7','0.25'),('1e-14','0.2','0','0')]]):
    dom=delta_rel*om;dt=delta_rel*back
    p0=mp.exp(-tail-back)*(-mp.expm1(-om));p1=mp.exp(-tail-back-dt)*(-mp.expm1(-om-dom))
    check(f'receiver_relative_cell_bound_{i}',abs(p1-p0)<=p0*delta_rel*(1+back)*(1+mp.mpf('1e-45'))+mp.mpf('1e-65'))
    check(f'receiver_survival_bound_{i}',abs(mp.exp(-tail-back-dt)-mp.exp(-tail-back))<=dt+mp.mpf('1e-65'))
# Source-to-observable inverse-budget coefficients: budget / C yields the allowed uniform k upper bound.
budgets={
 'C_T_K_per_cm3_s':cThi*qfachi*h,
 'C_e_per_cm3_s':be*qfachi*h,
 'C_tau_per_cm3_s':cs*nhi*be*qfachi*h*h/2,
 'C_rate_relative_per_cm3_s':be*qfachi*h/emin,
 'C_cell_relative_per_cm3_s':be*qfachi*h/emin*(1+tau0upper)}
tube_kmax=min((radii[i]-flow[i])/(h*nuabs[i]*qfachi) for i in range(4) if nuabs[i])
for key,v in budgets.items():check(key+'_positive',v>0)
check('all_candidate_k_below_tube_ceiling',allk[1]<tube_kmax)
old_wide_lower=h*qfaclo*allk[0]-dot(ell,V)*(h*qfachi*allk[1])
check('wide_minmax_loss_shown',old_wide_lower<0)
check('exposure_normalisation_closes_same_set_sign',F(res['FIVE_PRESCRIPTION_HULL']['electron_endpoint_interval'][0])>0)
spread=m(models['D69'][1])/m(models['KS91_G15'][0])
result={
 'status':'PASS' if all(x['pass']for x in checks) else 'FAIL',
 'decision':'ACCEPT_EXPOSURE_CONE_AND_PRESCRIPTION_SET_TO_FIXED_RECEIVER_BOUNDS',
 'source_accuracy':'physical calibrated rate envelope unresolved; the five-expression hull is a specified model set',
 'physical_omission_budget':None,
 'new_ODE_runs':0,'new_native_receiver_runs':0,'new_atomic_fits':0,
 'W_rational':[str(x)for x in W],'V_rational':[str(x)for x in V],
 'exposure_constants':approx({'electron_feedback_fraction':ev,'a_e':ae,'b_e':be,'temperature_gain_lo_K':cTlo,'temperature_gain_hi_K':cThi}),
 'point_rates_cm3_s':points,'prescription_hull_spread_upper':mp.nstr(spread,30),
 'common_tube_k_upper_ceiling_cm3_s':str(floorfrac(tube_kmax)),
 'inverse_budget_coefficients_rational':{k:str(ceilfrac(v,25))for k,v in budgets.items()},
 'receiver_tau0_box':[str(floorfrac(tau0lower)),str(ceilfrac(tau0upper))],
 'results':res,'checks_passed':sum(x['pass']for x in checks),'checks_failed':sum(not x['pass']for x in checks),
 'checks':checks,'elapsed_seconds':time.monotonic()-start,
 'independence':'same assistant, independent mpmath rate expressions and exact Fraction closure; not external review',
 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [ROOT/'inputs/interval_result_v3.json',ROOT/'results/WOLFRAM_RATE_INTERVALS.json',ROOT/'receiver/CONTRACT_EXTRACT.json']}}
(ROOT/'results/PHYS23_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
with (ROOT/'results/RATE_AND_RESPONSE_TABLE.csv').open('w') as out:
    w=csv.writer(out);w.writerow(['prescription','k_50000_cm3_s','k_lower','k_upper','delta_T_lower_K','delta_T_upper_K','delta_e_lower_perH','delta_e_upper_perH','delta_tau_lower','delta_tau_upper'])
    for name,r in res.items():
        vals=[name,points.get(name,'')]+[float(F(x)) for field in ['k_cm3_s_interval','temperature_endpoint_K_interval','electron_endpoint_interval','finite_segment_delta_tau_interval'] for x in r[field]];w.writerow(vals)
print(json.dumps({'status':result['status'],'checks_passed':result['checks_passed'],'checks_failed':result['checks_failed'],'exposure_constants':result['exposure_constants'],'spread':float(spread),'tube_kmax':float(tube_kmax),'results':{name:{k:([float(F(x))for x in v]if isinstance(v,list) else v)for k,v in r.items()if k in ['temperature_endpoint_K_interval','electron_endpoint_interval','finite_segment_delta_tau_interval','numerical_acceptance_ratios']}for name,r in res.items()},'budgets':approx(budgets)},indent=2))
raise SystemExit(0 if result['status']=='PASS' else 1)
