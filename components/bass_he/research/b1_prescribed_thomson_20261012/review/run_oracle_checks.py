"""Small independent derivation checks, not a full six-case B1 run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad

from b1_independent_oracles import (
    backward_lrs, collisionless_quadrupole, direct_axisym_collision_matrix,
    direct_axisym_collide, linear_shear_cells, planck_occupation,
    planck_logarithmic_slope,
)


HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
INPUT=ROOT/'inputs/research/broad_history_20261010/evidence/RUN002'
begin=time.perf_counter()
hist={name:{k:v.copy() for k,v in np.load(INPUT/f'{name}_n16384/history.npz').items()}
      for name in ('flrw','rp01')}
b=hist['rp01']['b'][-1]
energies=np.array([0.1,0.3,1.,3.,6.,10.])
exact=collisionless_quadrupole(planck_occupation,energies,b,256)
exact128=collisionless_quadrupole(planck_occupation,energies,b,128)
null=collisionless_quadrupole(lambda x: np.ones_like(x),energies,b,128)

# A generic unequal-axis forward map: independent finite angular derivative.
n0=np.array([.3,-.4,np.sqrt(.75)])
aa=np.array([.7,.9,1.2])
r=np.linalg.norm(aa*n0)
n1=aa*n0/r
etheta=np.array([n0[2]*.6,n0[2]*(-.8),-.5])
ephi=np.cross(n0,etheta)
analytic_j=float(np.prod(aa)/r**3)
derivative_j=[]
for eps in [1e-3,1e-4,1e-5]:
    def moved(v):
        p=n0*np.cos(eps)+v*np.sin(eps)
        m=n0*np.cos(eps)-v*np.sin(eps)
        f=lambda n: aa*n/np.linalg.norm(aa*n)
        return (f(p)-f(m))/(2*eps)
    derivative_j.append(float(np.dot(n1,np.cross(moved(etheta),moved(ephi)))))

mu,weights=leggauss(14)
ii=1+.4*(3*mu*mu-1)/2
ft0=ii/2; fp0=ii/2
tau=.037
ft,fp=direct_axisym_collide(mu,weights,ft0,fp0,tau)
before=float(weights@(ft0+fp0)); after=float(weights@(ft+fp))
q2_before=float((weights*(3*mu*mu-1)/2)@ii/before)
q2_after=float((weights*(3*mu*mu-1)/2)@(ft+fp)/after)
# Matrix first-order solution at zero shear must agree with amplitudes of direct matrix.
from scipy.linalg import expm
cm=np.array([[-.9,-.4],[-.15,-.4]])
amp=expm(tau*cm)@np.array([.4,0.])
predi=1+amp[0]*(3*mu*mu-1)/2
predq=amp[1]*(1-mu*mu)
moment_err=float(max(np.max(abs((ft+fp)-predi)),np.max(abs((ft-fp)-predq))))

# Invert a finite LRS ray and establish small-beta slope numerically.
source_mu,gg=backward_lrs(mu,b)
target_mu,ginv=backward_lrs(source_mu,-b)
roundtrip=max(float(np.max(abs(target_mu-mu))),float(np.max(abs(gg*ginv-1))))
smallbeta=[]
slope=planck_logarithmic_slope(energies)
for eps in [1e-3,1e-4,1e-5]:
    aa=collisionless_quadrupole(planck_occupation,energies,eps,128)['q2']
    expected=2*eps*slope/5
    smallbeta.append({'beta':eps,'max_abs_residual':float(np.max(abs(aa-expected))),
                      'max_abs_residual_over_beta_squared':float(np.max(abs(aa-expected))/eps**2)})

# Fine-cell clock projection by independent explicit background formula.
hh=.6774*1.e5/3.0856775814913673e24
omega_m=.309
ai=1/21.
d=hh**2*(1-omega_m)
bc=hh**2*omega_m
vi=ai**3
hi=np.sqrt((bc/vi+d)/(1-.1**2))
s0=.1*hi*vi
x=hist['rp01']['x']; mid=(x[1:]+x[:-1])/2
v=(ai*np.exp(mid))**3
h_f=np.sqrt(d+bc/v)
h_b=np.sqrt(d+bc/v+s0*s0/v**2)
t_b=np.diff(hist['rp01']['tau'])
t_f_on_b=np.diff(hist['flrw']['tau'])*(h_f/h_b)
db=np.diff(hist['rp01']['b'])
lin_b=linear_shear_cells(db,t_b,-1.)
lin_f=linear_shear_cells(db,t_f_on_b,-1.)

inputs={}
for p in (INPUT/'flrw_n16384/history.npz',INPUT/'rp01_n16384/history.npz',
          ROOT/'inputs/upstream_bass/bianchi/q/modeb.py',HERE/'b1_independent_oracles.py'):
    raw=p.read_bytes();inputs[str(p.relative_to(ROOT))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

checks={
 'role':'INDEPENDENT_THEORY_ORACLE_NOT_FINAL_DECISION_REVIEWER',
 'scope':'small oracle calculations only; no main transport run',
 'input_identities':inputs,
 'planck_no_emission_B0':{'beta_final':float(b),'dimensionless_y':energies.tolist(),
    'q2_exact_one_shot_gl256':exact['q2'].tolist(),
    'max_abs_gl128_vs256':float(max(abs(exact128['q2']-exact['q2']))),
    'polarization_exact':0.,'U_exact':0.,'V_exact':0.},
 'flat_occupation_all_cases_null_max_abs_q2':float(max(abs(null['q2']))),
 'ray_roundtrip_max_abs':roundtrip,
 'forward_solid_angle_jacobian':{'analytic':analytic_j,'central_differences':derivative_j,
    'epsilons':[1e-3,1e-4,1e-5]},
 'dense_collision':{'nmu':14,'depth':tau,'intensity_mu_integral_before':before,
    'intensity_mu_integral_after':after,'relative_conservation':(after-before)/before,
    'q2_before':q2_before,'q2_after':q2_after,'min_ft':float(min(ft)),
    'min_fp':float(min(fp)),'direct_vs_derived_two_amplitudes_max_abs':moment_err},
 'small_beta_asymptotic_residual':smallbeta,
 'producer_constant_unchanged_clock_projection':{
    'sigma_T_cm2':6.6524587321e-25,
    'tau_B':float(sum(t_b)),'tau_F_on_B':float(sum(t_f_on_b)),
    'delta_tau_history_B_minus_F_on_B':float(sum(t_b-t_f_on_b)),
    'linear_order_slope_minus_one_final_B_i2_and_Qamplitude':lin_b[-1].tolist(),
    'linear_order_slope_minus_one_final_F_on_B_i2_and_Qamplitude':lin_f[-1].tolist(),
    'linear_order_q2_history_difference':float((lin_b[-1,0]-lin_f[-1,0])/5),
    'linear_order_equatorial_Q_history_difference':float(lin_b[-1,1]-lin_f[-1,1]),
    'claim_limit':'O(beta) oracle only; not full B1 result; uses producer sigmaT, not consumer-adjusted'},
 'wall_seconds':time.perf_counter()-begin,
}
assert checks['flat_occupation_all_cases_null_max_abs_q2']<2e-14
assert roundtrip<1e-14
assert abs((after-before)/before)<1e-14
assert moment_err<2e-14
assert checks['planck_no_emission_B0']['max_abs_gl128_vs256']<2e-13
assert smallbeta[-1]['max_abs_residual']<smallbeta[-2]['max_abs_residual']/50
checks['evaluated_checks_status']='PASS'
out=HERE/'ORACLE_CHECKS.json'
out.write_text(json.dumps(checks,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(checks,indent=2,ensure_ascii=False))
