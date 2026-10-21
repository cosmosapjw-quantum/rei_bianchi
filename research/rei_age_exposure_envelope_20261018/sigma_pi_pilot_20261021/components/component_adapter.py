"""Independent matter/radiation initial controls; unchanged PR147 RHS."""
import os
import sys
sys.dont_write_bytecode = True
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
from pathlib import Path
import math
from functools import lru_cache
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import adapter as original

SIGMAS = original.SIGMAS
MATTER = [-.0003, -.0001, 0., .0001, .0003]
RADIATION = [-.001, -.0003, 0., .0003, .001]
GUARDS = [(.1,.0003,.001), (.1,-.0003,-.001), (0.,.0003,-.0003)]
SOURCE = original.SOURCE
digest = original.digest
verify_source = original.verify_source


@lru_cache(maxsize=2)
def quadrature_q(radial, angular):
    packet = original.momentum(30., 0., radial, angular, 3)
    energy = np.sqrt(30.**2+packet._q**2)
    return float(np.sum(packet._numbers*packet._q**2/energy)/packet.reference_energy_norm)


def calibration(sigma, matter, radiation, guard=False):
    if not all(math.isfinite(v) for v in (sigma,matter,radiation)) or not 0<=sigma<=.1:
        raise ValueError('INVALID_COMPONENT_INITIAL_VALUES')
    source, _ = original.cosmology()
    hi2 = source.href**2/(1-sigma**2/6)
    nr, na = (48,24) if guard else (24,12)
    q = quadrature_q(nr,na)
    km = math.sqrt(6)/5*(source.h0**2/hi2)*(.1*source.omega_m/source.aref**3)*q
    kr = math.sqrt(6)/5*(source.h0**2/hi2)*(source.omega_r/source.aref**4)
    amplitude, k = matter/km, radiation/kr
    if not -1<=amplitude<=2 or abs(k)>.5:
        raise ValueError('COMPONENT_AMPLITUDE_OUTSIDE_SOURCE_DOMAIN')
    return dict(H_i_squared=hi2, Q_M=q, K_m=km, K_r=kr,
                massive_A=amplitude,k_gamma=k,k_nu=k,
                Sigma_half_i=sigma/math.sqrt(2),shear_orientation=1 if sigma else 0,
                Pi_F_signed_target=matter+radiation)


def config(sigma, matter, radiation, guard=False):
    cal = calibration(sigma,matter,radiation,guard)
    # Historical helper constructs only metadata, never an IVP.
    c = original.config(sigma,radiation,guard)
    c.update(P_m_i=matter,P_r_i=radiation,Pi_F_signed_i=matter+radiation,
             massive_A=cal['massive_A'],calibration=cal,
             matter_sign=int(np.sign(matter)),radiation_sign=int(np.sign(radiation)),
             initial_total_stress_cancelled=(matter+radiation==0 and matter!=0),
             true_isotropy_control=(sigma==matter==radiation==0))
    return c


def cases():
    nominal = [config(s,m,r) for s in SIGMAS for m in MATTER for r in RADIATION]
    guards = [config(s,m,r,True) for s,m,r in GUARDS]
    return [{'id':digest(c),'config':c} for c in nominal+guards]


def model(c):
    return original.model(c)


def components(out):
    out = dict(out)
    out['P_m'] = out['Pi_F_signed_matter']
    out['P_r'] = out['Pi_F_signed_gamma']+out['Pi_F_signed_nu']
    out['P_total'] = out['P_m']+out['P_r']
    out['Pi_m'] = abs(out['P_m'])
    out['Pi_r'] = abs(out['P_r'])
    out['Pi_total'] = abs(out['P_total'])
    out['p_m_J_m3'] = out['Pi_matter_J_m3']
    out['p_r_J_m3'] = out['Pi_gamma_J_m3']+out['Pi_nu_J_m3']
    out['p_total_J_m3'] = out['p_m_J_m3']+out['p_r_J_m3']
    out['pi_m_contract_pi_r_J2_m6'] = 6*out['p_m_J_m3']*out['p_r_J_m3']
    out['normalized_cross'] = out['P_m']*out['P_r']
    out['triangle_upper_slack'] = out['Pi_m']+out['Pi_r']-out['Pi_total']
    out['reverse_triangle_slack'] = out['Pi_total']-abs(out['Pi_m']-out['Pi_r'])
    denominator = out['Pi_m']+out['Pi_r']
    out['cancellation_fraction'] = np.divide(out['triangle_upper_slack'],denominator,
                                           out=np.zeros_like(denominator),where=denominator>0)
    return out


def observables(obj,sol):
    return components(original.observables(obj,sol))


def validate(c,sol,out):
    checks = original.validate(c,sol,out)
    # Aggregate zero stress alone must never select the isotropy control.
    checks.pop('isotropic_grid_control',None)
    if c['true_isotropy_control']:
        checks['true_isotropic_control'] = bool(np.max(abs(out['Sigma_F']))<5e-12 and
            np.max(abs(out['P_m']))<5e-12 and np.max(abs(out['P_r']))<5e-12)
    checks['initial_P_m'] = bool(abs(out['P_m'][0]-c['P_m_i'])<=5e-12)
    checks['initial_P_r'] = bool(abs(out['P_r'][0]-c['P_r_i'])<=5e-12)
    checks['component_sum'] = bool(np.array_equal(out['P_total'],out['P_m']+out['P_r']))
    scale = np.maximum(1.,out['Pi_total']**2)
    checks['component_cross_identity'] = bool(np.max(abs(out['Pi_total']**2-
        out['Pi_m']**2-out['Pi_r']**2-2*out['normalized_cross'])/scale)<=1e-15)
    checks['triangle_relations'] = bool(min(out['triangle_upper_slack'].min(),
                                          out['reverse_triangle_slack'].min())>=-1e-15)
    return checks
