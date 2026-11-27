"""Actual donor/cubature kernel checks; never calls native chemistry."""
from pathlib import Path
import sys,json,math,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT.parent
sys.path.insert(0,str(RESEARCH/'he28_strip_refinement_20261018/src'))
from refined_source import RefinedSourceModel,GridSpec
from physics import shape,sigma_cm2,Y_HE,C_CM_S,A_BIRTH
from survival_bounds import survival_envelope,distance_interval


def donor(order):
    z,w=np.polynomial.legendre.leggauss(order);e=[];weights=[]
    for a,b in zip((13.6,24.59,54.42),(24.59,54.42,100.)):
        ee=(a+b)/2+(b-a)*z/2;e.extend(ee);weights.extend((b-a)*w/2*shape(ee))
    w=np.array(weights);return np.array(e),w/math.fsum(w)

def rate(e,nh):
    return C_CM_S*nh*(sigma_cm2(e)*np.array([1-1e-5,Y_HE*(1-1e-5),Y_HE*1e-5])).sum(axis=1)

def run():
    start=time.perf_counter();ed,wd=donor(256);er,wr=donor(512);rows=[]
    for q in (-.005,0.,.005):
        for r in (1,2,4,8,16):
            m=RefinedSourceModel(None,GridSpec(m=16,angles=4,q=q,strips=r),tabulate=False)
            for frac in (.1,.37,.9):
                t=frac*m.t_end;x=m.x(t);nh=1.89819845071402689e-7/(A_BIRTH*np.exp(x))**3
                weights,moments=m.source_moments(t);e=m.geometry(t)[0]
                for age in (1e10,1e11):
                    rates=rate(ed,nh);ref=float(wd@np.exp(-age*rates));check=float(wr@np.exp(-age*rate(er,nh)))
                    val=float(weights@np.exp(-age*rate(e,nh))/weights.sum())
                    levels=[];prev=None
                    for depth in (0,2,4,6,8,10,12,14):
                        b=survival_envelope(rates,wd,age,depth)
                        if not b.lower<=ref<=b.upper:raise AssertionError('HE29_DONOR_NOT_ENCLOSED')
                        if prev and (b.lower<prev.lower-2e-14 or b.upper>prev.upper+2e-14):
                            raise AssertionError('HE29_NON_NESTED_BOUNDS')
                        lo,hi=distance_interval(val,b)
                        levels.append({'depth':depth,'groups':b.groups,'lower':b.lower,'upper':b.upper,
                            'width':b.width,'error_lower':lo,'error_upper':hi});prev=b
                    if abs(ref-check)>2e-13:raise AssertionError('HE29_DONOR_QUADRATURE_INSTABILITY')
                    rows.append({'q':q,'m':16,'r':r,'birth_fraction':frac,'age_s':age,'modes':m.K,
                         'donor256_survival':ref,'donor512_survival':check,'reference_difference':abs(ref-check),
                         'cubature_survival':val,'actual_donor_error':abs(val-ref),'envelopes':levels,
                         'moment_defect':moments['max_relative_moment_error']})
    summary={'scope':'finite-positive-donor frozen-opacity bound; not rigorous continuum or gas-temperature error',
      'cases':len(rows),'envelope_evaluations':sum(len(r['envelopes']) for r in rows),'native_calls':0,
      'max_quadrature_reference_difference':max(r['reference_difference'] for r in rows),
      'max_source_moment_defect':max(r['moment_defect'] for r in rows),
      'monotone_nested_bounds':True,'all_donor_survivals_enclosed':True,
      'positive_error_lower_bound_cases':int(sum(r['envelopes'][-1]['error_lower']>0 for r in rows)),
      'max_final_envelope_width':max(r['envelopes'][-1]['width'] for r in rows),
      'per_r_q0_max_error':{str(r):max(x['actual_donor_error'] for x in rows if x['q']==0 and x['r']==r) for r in (1,2,4,8,16)},
      'wall_s':time.perf_counter()-start,'continuous_spectrum':'HOLD_NO_INTERVAL_QUADRATURE'}
    return rows,summary
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();p=Path(a.out);p.mkdir(parents=True,exist_ok=False)
    rows,summary=run()
    for name,obj in (('CASES.json',rows),('SUMMARY.json',summary)):
        with (p/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False)
    print(json.dumps(summary,indent=2))
