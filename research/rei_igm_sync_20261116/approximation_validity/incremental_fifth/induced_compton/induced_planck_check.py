"""BASS335 induced-Compton kernel on original AXBI directional Planck photons.

Frozen spectral quadrature only; no coupled gas, radiation or geometry evolution.
"""
from pathlib import Path
import json,time,hashlib
import numpy as np
import pandas as pd
from scipy.integrate import quad_vec
from scipy.special import zeta
from numpy.polynomial.legendre import leggauss


def moments(b, nmu, xmax):
    mu,w=leggauss(nmu);w=w/2
    d=(1-mu*mu)*np.exp(-2*b)+mu*mu*np.exp(4*b)
    p2=(3*mu*mu-1)/2
    def f(x):
        n=1/np.expm1(x*np.sqrt(d))
        b0=np.dot(w,n);b2=np.dot(w*p2,n)
        return np.array([x**3*b0,x**4*(b0+b0*b0+.5*b2*b2)])
    value,error=quad_vec(f,0,xmax,epsabs=2e-12,epsrel=2e-12)
    return {'TC_over_Tref':float(value[1]/(4*value[0])),
            'U_over_Uref':float(value[0]/(np.pi**4/15)),
            'quadrature_integral_error_estimate':float(error)}


def main():
    start=time.perf_counter();here=Path(__file__).resolve().parent
    result=[]
    for b in [0.,-.003,.003,-.006,.006]:
        values={f'GL{n}_x{x}':moments(b,n,x) for n,x in [(16,80),(32,80),(16,120),(32,120)]}
        ref=values['GL32_x120']
        result.append({'b':b,'runs':values,
                       'max_TC_refinement_gap':max(abs(v['TC_over_Tref']-ref['TC_over_Tref']) for v in values.values())})
    coefficient=12*np.pi**2/35-6/5
    source=here.parent/'results_five/five_case_abundances.csv.gz'
    d=pd.read_csv(source,float_precision='round_trip')
    case={}
    for name,c in d.groupby('case',sort=False):
        delta=2.7255/c.a.to_numpy()*coefficient*c.b.to_numpy()**2
        i=int(np.argmax(delta))
        case[name]={'sample_rows':len(c),'leading_delta_TC_K_max':float(delta[i]),
                    'zbar_at_sampled_peak':float(c.zbar.iloc[i]),'b_at_sampled_peak':float(c.b.iloc[i]),
                    'leading_delta_TC_over_Tref_max':float(np.max(coefficient*c.b.to_numpy()**2)),
                    'gas_temperature_response_error_bound':None}
    coeff_check={}
    for q in [.003,.006]:
        minus=next(r for r in result if r['b']==-q)['runs']['GL32_x120']['TC_over_Tref']
        plus=next(r for r in result if r['b']==q)['runs']['GL32_x120']['TC_over_Tref']
        coeff_check[str(q)]={'even_quadratic_coefficient':float(((plus+minus)/2-1)/q**2),
                             'difference_from_analytic':float(((plus+minus)/2-1)/q**2-coefficient),
                             'odd_TC_half_difference':float((plus-minus)/2)}
    exact_peaks={}
    for name in ['SHEAR_PLUS','SHEAR_MINUS']:
        c=case[name];ref=2.7255*(1+c['zbar_at_sampled_peak'])
        exact=moments(c['b_at_sampled_peak'],32,120)
        exact_peaks[name]={'a':1/(1+c['zbar_at_sampled_peak']),
            'b':c['b_at_sampled_peak'],'Tref_K':ref,**exact,
            'exact_delta_TC_K_at_leading_sample_peak':ref*(exact['TC_over_Tref']-1),
            'scope':'Exact spectral quadrature at the leading-approximation sampled peak, not a full-history or continuous maximum.'}
    out={'schema':'rei.axbi.bass335-induced-compton-planck-check.v1',
         'status':'DERIVED_AND_NUMERICALLY_CHECKED_FROZEN_PHOTON_FIELD_ONLY',
         'source_method':'BASS PR335 research/typeii_spectral_closure_20261116/DESIGN_AND_THEORY.md; exact head supplied by parent receipt',
         'source_method_commit':'d3ec945c4674d20ae63d4e7f659df24d798630de',
         'units':'E=k_B*Tref*x; h=2*pi*hbar; U=8*pi/(h^3*c^3)*integral E^3*b0 dE; TC=M/(4*k_B*U)',
         'radiation_scope':'Actual Planck photons/CMB with Tref=2.7255 K/a only; U=a_rad*Tref^4*angular_M, a_rad=pi^2*k_B^4/(15*hbar^3*c^3). Effective Omega_r neutrinos are excluded from Compton energy density.',
         'moments':'b_l=1/2 integral n(x,mu)P_l(mu)dmu; n=1/expm1(x*sqrt(D)); b1=b3=0',
         'induced_kernel':'S=b0^2+b2^2/2 for reflection-even input; numerator integral x^4*(b0+S)',
         'analytic_TC_quadratic_coefficient':float(coefficient),
         'analytic_U_quadratic_coefficient':1.6,
         'analytic_integral_K':float(120*(zeta(4)-zeta(6))),
         'analytic_M0':float(24*zeta(4)),
         'coefficient_refinement':coeff_check,'exact_spectral_checks':result,
         'sample_input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'leading_small_b_sampled_results':case,
         'exact_at_leading_sampled_peaks':exact_peaks,
         'limits':['Finite-b exact spectral checks apply only at five listed b values.',
                   'History evaluation uses leading C*b^2, not an exact finite-b spectral integral at every row.',
                   'This photon equilibrium target is not gas temperature or an abundance error bound.',
                   'No HYREC/TypeII state, solver, or model was imported; only the angular collision-kernel method is reused.'],
         'new_IVPs':0,'wall_s':time.perf_counter()-start}
    (here/'RESULT.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'wall_s':out['wall_s'],'C':coefficient,'coefficient_refinement':coeff_check,'cases':case},indent=2))


if __name__=='__main__':main()
