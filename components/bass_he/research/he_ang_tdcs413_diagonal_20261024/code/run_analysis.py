"""Frozen13sourcepoints: nominal model, weighted minimax,80digit references."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import sys
import mpmath as mp
import tdcs413 as m

UNIT=Path(__file__).resolve().parents[1]


def prior_kernel():
    p=UNIT.parent/'he_ang_pwbe_spin_azimuth_20261024/code/pwbe.py'
    if hashlib.sha256(p.read_bytes()).hexdigest()!='9485f9a97689d14b819de2bdb3005643e7b1b12b2b321df7695129fa699c4c37':raise RuntimeError('reused source kernel identity changed')
    spec=importlib.util.spec_from_file_location('prior_pwbe_point',p);m0=importlib.util.module_from_spec(spec);spec.loader.exec_module(m0)
    return m0.pwbe_point


def vector_reference(theta):
    # Source vectors/amplitudes computed independently in80decimaldigits.
    k=mp.sqrt(mp.mpf(250)/17);r=mp.sqrt(mp.mpf(517)/17);th=mp.mpf(theta)*mp.pi/180
    A=[k*mp.sin(th),mp.mpf(0),k*mp.cos(th)];B=[-A[0],mp.mpf(0),A[2]];beam=[mp.mpf(0),mp.mpf(0),r]
    q2=sum((beam[i]-A[i]-B[i])**2 for i in range(3))
    da=sum((beam[i]-A[i])**2 for i in range(3));db=sum((beam[i]-B[i])**2 for i in range(3))
    C=8*mp.sqrt(2)/(2*mp.pi)**3
    D=C/da*((1+q2)**-2-(1+sum(x*x for x in B))**-2)
    X=C/db*((1+q2)**-2-(1+sum(x*x for x in A))**-2)
    return (2*mp.pi)**4*k*k/r*(mp.mpf(1)/4*(D+X)**2+mp.mpf(3)/4*(D-X)**2)


def mp_minimax(f,y,s):
    best=mp.mpf(0);pair=None
    for i in range(len(f)):
        for j in range(len(f)):
            q=(y[i]*f[j]-y[j]*f[i])/(s[i]*f[j]+s[j]*f[i])
            if q>best:best=q;pair=(i,j)
    i,j=pair;a=(y[i]*s[j]+y[j]*s[i])/(f[i]*s[j]+f[j]*s[i])
    return a,best,[i+1,j+1]


def main():
    mp.mp.dps=80;obj,source=m.load_source();point=prior_kernel()
    angles=[float(r['theta_deg']) for r in source];y=[float(r['y']) for r in source];s=[float(r['s']) for r in source]
    values=[m.diagonal(t) for t in angles];ref44=vector_reference('44')
    refK=[vector_reference(str(int(t))) for t in angles];refF=[x/ref44 for x in refK]
    f=[v['K']/m.diagonal(44)['K'] for v in values];fit=m.minimax(f,y,s);bis=m.minimax_bisection(f,y,s)
    a80,k80,pair80=mp_minimax(refF,[mp.mpf(str(v)) for v in y],[mp.mpf(str(v)) for v in s])
    rows=[];allpass=True
    for i,(src,v) in enumerate(zip(source,values)):
        mu=math.cos(math.radians(angles[i]));prior=point(float(m.E0),float(m.E),mu,mu,math.pi)
        err80=abs(v['K']-float(refK[i]))/float(refK[i]);errprior=abs(v['K']-prior['K'])/prior['K'];shapeerr=abs(f[i]-float(refF[i]))/float(refF[i])
        allpass &= err80<=1e-11 and errprior<=1e-11 and shapeerr<=1e-11
        rows.append({'theta_deg':str(src['theta_deg']),'source_y':str(src['y']),'source_s':str(src['s']),'printed':src['printed'],
                     'K':v['K'],'shape':f[i],'y':y[i],'s':s[i],'predicted':fit['a']*f[i],'weighted_residual':fit['residuals'][i],
                     'mp80_K':mp.nstr(refK[i],82),'mp80_shape':mp.nstr(refF[i],82),
                     'prior_point_K':prior['K'],'relative_K_error_80digits':err80,'relative_prior_point_error':errprior,'relative_shape_error_80digits':shapeerr})
    k2=mp.mpf(250)/17;r=mp.sqrt(mp.mpf(517)/17);k=mp.sqrt(k2);h=(1+k2)**-2
    def N(z):return r*h*(1+z*z)**3-r*(1+5*z*z)-4*k2*z
    z80=mp.findroot(N,(-mp.mpf('.5'),mp.mpf(0)));theta80=mp.acos((r-z80)/(2*k))*180/mp.pi
    peak=m.peak();errors={'a_abs_80digits':abs(fit['a']-float(a80)),'kappa_abs_80digits':abs(fit['kappa']-float(k80)),
        'a_abs_bisection':abs(fit['a']-bis['a']),'kappa_abs_bisection':abs(fit['kappa']-bis['kappa']),
        'objective_abs_kappa':abs(fit['objective']-fit['kappa']),'peak_angle_abs_80digits':abs(peak['theta_deg']-float(theta80)),
        'peak_root_residual_abs':abs(peak['root_residual'])}
    allpass &= all(errors[k]<=1e-10 for k in ['a_abs_80digits','kappa_abs_80digits','a_abs_bisection','kappa_abs_bisection','objective_abs_kappa'])
    allpass &= errors['peak_angle_abs_80digits']<=1e-9 and errors['peak_root_residual_abs']<=1e-11
    allpass &= fit['active_pair_1based']==pair80 and fit['a']>0
    i,j=[x-1 for x in fit['active_pair_1based']]
    allpass &= abs(fit['residuals'][i]+fit['kappa'])<=1e-10 and abs(fit['residuals'][j]-fit['kappa'])<=1e-10
    #721point saved display grid; no angle/energy integration.
    grid=[32+28*i/720 for i in range(721)];gridpred=[fit['a']*m.shape(t) for t in grid]
    result={'unit':'HE-ANG-TDCS413-DIAGONAL','status':'NUMERICAL_CHECKS_COMPLETE_PENDING_C9','all_numerical_checks_pass':bool(allpass),
        'source_metadata':obj,'model':{'energy_unit_nominal_eV':'27.2','epsilon':'125/17','epsilon0':'517/34','reference_theta_deg':44,
        'geometry':'thetaA=thetaB,relativephi=pi','fixed_center':True,'sourceEq21unpolarizedadopted':False,'spin_extra_count_factor':False},
        'rows':rows,'fit':fit,'independent_interval_bisection':bis,'interval_kappa1':m.feasible_interval(f,y,s,1),
        'mp80_fit':{'a':mp.nstr(a80,82),'kappa':mp.nstr(k80,82),'active_pair_1based':pair80},
        'active_angles_deg':[angles[i],angles[j]],'peak':peak,'mp80_peak':{'z':mp.nstr(z80,82),'theta_deg':mp.nstr(theta80,82)},
        'measured_errors':errors,'plot_grid':{'theta_deg':grid,'predicted':gridpred},
        'interpretation':'Weightedmaxresidual with source1sigma as numericalweights; no pvalue/confidence or covariance assumption; model agreement distinct from implementation PASS.',
        'no_global_event_integral':True,'no_empirical_absolute_scale':True,'old_suite_replays':0,
        'versions':{'Python':sys.version,'mpmath':mp.__version__,'platform':platform.platform()}}
    out=UNIT/'results';out.mkdir(exist_ok=True);(out/'ANALYSIS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'all_numerical_checks_pass':bool(allpass),'fit':fit,'peak':peak,'measured_errors':errors,'interval_kappa1':result['interval_kappa1']},indent=2))
    return 0 if allpass else 1


if __name__=='__main__':raise SystemExit(main())
