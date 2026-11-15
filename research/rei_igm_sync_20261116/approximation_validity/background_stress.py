"""Original AXBI saved-history background-radiation diagnostic, SI units.

No coupled matter/radiation trajectory is evolved. The integral is the first
variation of shear forced on the fixed saved metric. Full effective Omega_r
is a conditional all-massless reference, not a universal upper bound.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, time
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_simpson, cumulative_trapezoid, quad

SOURCE_SHA = 'a568581b7aabbbe3d052d494b283992a90f6ac91ef4e8d289c17632ed99cd3c9'
SOURCE_COMMIT = 'df72fb686a41c3f047bca1a92df8946482948f82'
C = 299792458.0
G = 6.67430e-11
KB = 1.380649e-23
HPLANCK = 6.62607015e-34
HBAR = HPLANCK/(2*np.pi)
TCMB0 = 2.7255
MPC_M = 3.0856775814913673e22
H0 = 67.4e3/MPC_M
OM, OR = .315, .000092
OL = 1-OM-OR
AI = 1/21
RHOCRIT_ENERGY = 3*H0**2*C**2/(8*np.pi*G)
ARAD = np.pi**2*KB**4/(15*HBAR**3*C**3)
OGAMMA = ARAD*TCMB0**4/RHOCRIT_ENERGY

def angular_moments(b, order=64):
    """Return M=<T^4>/Tref^4 and F=(Pparallel-Pperp)/uref.

    mu is the local orthonormal direction, hence its measure is uniform.
    Subtract the exactly zero isotropic P2 moment before quadrature to avoid
    a spurious shear source at q=0 from floating quadrature residue.
    """
    b=np.atleast_1d(np.asarray(b,dtype=float))
    mu,w=leggauss(order); w=w/2; mu2=mu*mu
    D=(1-mu2)*np.exp(-2*b[:,None])+mu2*np.exp(4*b[:,None])
    if not np.all(np.isfinite(D)) or np.any(D<=0):
        raise ValueError('nonpositive/nonfinite angular metric factor')
    d4=np.expm1(-2*np.log(D))
    M=1+d4@w
    F=(d4*((3*mu2-1)/2))@w
    return M,F

def initial_angle_moments(b,order=96):
    """Independent conserved-momentum representation of the same moments."""
    u,w=leggauss(order); w=w/2
    b=np.atleast_1d(np.asarray(b,dtype=float))
    R=np.sqrt(np.exp(2*b[:,None])*(1-u*u)+np.exp(-4*b[:,None])*u*u)
    mu=np.exp(-2*b[:,None])*u/R
    M=R@w
    F=(R*(3*mu*mu-1)/2)@w
    return M,F

def background(a,q):
    hf=H0*np.sqrt(OR/a**4+OM/a**3+OL)
    hfi=H0*np.sqrt(OR/AI**4+OM/AI**3+OL)
    s=q*hfi*(AI/a)**3
    return np.sqrt(hf*hf+s*s),s

def forced_shear(a,b,q,omega,order=64):
    x=np.log(a)
    H,s=background(a,q)
    M,F=angular_moments(b,order)
    # 8piG/(3c^2)*u_ref = H0^2*Omega*a^-4.
    integrand=H0**2*omega*F/(a*H)
    ds=cumulative_simpson(integrand,x=x,initial=0)/a**3
    trap=cumulative_trapezoid(integrand,x=x,initial=0)/a**3
    return M,F,ds/H,trap/H,H,s

def load(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError('source SHA mismatch')
    with gzip.open(path,'rt',newline='') as f: rows=list(csv.DictReader(f))
    if len(rows)!=4004: raise ValueError('expected 4004 pinned source rows')
    cases={}
    for key in sorted({r['case'] for r in rows}):
        rr=[r for r in rows if r['case']==key]
        cols={k:np.array([float(r[k]) for r in rr]) for k in rr[0] if k!='case'}
        if len(rr)!=1001 or np.any(np.diff(cols['a'])<=0):
            raise ValueError('ordered 1001-point case required')
        if not all(np.all(np.isfinite(v)) for v in cols.values()): raise ValueError('nonfinite input')
        if abs(cols['a'][0]-AI)>1e-15 or abs(cols['a'][-1]-.2)>1e-15:
            raise ValueError('wrong represented epoch domain')
        if np.any(cols['q_ref']!=cols['q_ref'][0]): raise ValueError('q changed within case')
        cases[key]=cols
    return cases

def run(source,out):
    start=time.perf_counter(); out.mkdir(parents=True,exist_ok=True)
    cases=load(source); result={}; records=[]
    for name,r in cases.items():
        a,b,q=r['a'],r['b'],float(r['q_ref'][0])
        M,F,ds,dst,H,s=forced_shear(a,b,q,OR)
        M128,F128=angular_moments(b,128)
        Mi,Fi=initial_angle_moments(b)
        # Node decimation changes only this diagnostic quadrature; not original ODE.
        _,_,coarse,_,_,_=forced_shear(a[::2],b[::2],q,OR)
        # Integrate PWL interpolation of the original saved b on a twice-dense grid.
        x=np.log(a); xf=np.linspace(x[0],x[-1],2001)
        af=np.exp(xf); bf=np.interp(xf,x,b)
        _,_,fine,_,_,_=forced_shear(af,bf,q,OR)
        peak=int(np.argmax(np.abs(ds))); epeak=int(np.argmax(np.abs(M-1)))
        radiation_density_ratio=H0**2*OR/a**4/H**2
        thermal_u=1.5*KB*r['temperature_K']*(r['nH_proper_cm3']*1e6*(1+.2454/(4*(1-.2454)))+r['ne_proper_cm3']*1e6)
        thermal_frac=thermal_u/(3*H*H*C*C/(8*np.pi*G))
        result[name]={
            'q_ref':q,'source_rows':len(a),'b_terminal':float(b[-1]),
            'all_effective_radiation_max_abs_delta_s_over_H':float(np.max(np.abs(ds))),
            'all_effective_radiation_signed_delta_s_over_H_at_peak':float(ds[peak]),
            'peak_zbar':float(1/a[peak]-1),
            'CMB_only_max_abs_delta_s_over_H':float(np.max(np.abs(ds))*OGAMMA/OR),
            'all_effective_radiation_terminal_delta_s_over_H':float(ds[-1]),
            'max_abs_delta_s_over_s':float(np.max(np.abs(ds*H/s))) if q else None,
            'max_fractional_background_energy_change':float(np.max(np.abs(M-1))),
            'max_fractional_Thomson_inverse_Compton_cooling_coefficient_change':float(np.max(np.abs(M-1))),
            'background_energy_change_peak_zbar':float(1/a[epeak]-1),
            'max_abs_delta_radiation_energy_over_total_energy':float(np.max(np.abs((M-1)*radiation_density_ratio))),
            'max_thermal_over_total_energy':float(np.max(thermal_frac)),
            'max_GL64_vs_GL128_M_difference':float(np.max(np.abs(M-M128))),
            'max_GL64_vs_GL128_F_difference':float(np.max(np.abs(F-F128))),
            'max_local_vs_initial_angle_M_difference':float(np.max(np.abs(M-Mi))),
            'max_local_vs_initial_angle_F_difference':float(np.max(np.abs(F-Fi))),
            'max_simpson_vs_trapezoid_delta_s_over_H_difference':float(np.max(np.abs(ds-dst))),
            'max_1001_vs_501_delta_s_over_H_difference':float(np.max(np.abs(ds[::2]-coarse))),
            'max_1001_vs_2001_PWL_delta_s_over_H_difference':float(np.max(np.abs(ds-fine[::2]))),
            'original_target_max_abs_delta_s_over_H':1e-4,
            'background_only_threshold_status':'BELOW_TARGET' if np.max(np.abs(ds))<1e-4 else 'EXCEEDS_TARGET',
            'original_approximation_status':'BACKGROUND_ONLY; full source extension in FULL_SUMMARY.json',
            'DAG_mapping':'AX03/AX08 approximation validity; not AX10 optional observables',
            'coupled_abundance_backreaction_error':None,
            'anisotropic_Compton_recoil_stimulated_heating':None,
        }
        for i in range(len(a)):
            records.append([name,q,a[i],1/a[i]-1,r['time_s'][i],b[i],M[i],F[i],ds[i],ds[i]*OGAMMA/OR,(M[i]-1)*radiation_density_ratio[i],thermal_frac[i]])
    with (out/'diagnostic.csv').open('w',newline='') as f:
        wr=csv.writer(f);wr.writerow(['case','q_ref','a','zbar','elapsed_proper_s','b','U_over_Uref','DeltaP_over_Uref','delta_s_over_H_effective_radiation','delta_s_over_H_CMB','delta_U_radiation_over_total','U_thermal_over_total']);wr.writerows(records)
    summary={'schema':'rei.axbi.background-stress-diagnostic.v1','source_commit':SOURCE_COMMIT,'source_sha256':SOURCE_SHA,'source_is':'PR374 reduced 1001 points/case from four complete original histories','constants_SI':{'c':C,'G':G,'k_B':KB,'h':HPLANCK,'hbar':HBAR,'a_rad':ARAD,'H0':H0,'Omega_gamma':OGAMMA,'Omega_r':OR},'cases':result,'new_coupled_IVPs':0,'source_or_tolerance_changes':0,'canonical_DAG_delta':0,'all_effective_Omega_r_status':'CONDITIONAL_ALL_MASSLESS_COLLISIONLESS_REFERENCE_NOT_RIGOROUS_UNIVERSAL_BOUND','runtime_wall_s':time.perf_counter()-start}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.source,a.out),indent=2))
