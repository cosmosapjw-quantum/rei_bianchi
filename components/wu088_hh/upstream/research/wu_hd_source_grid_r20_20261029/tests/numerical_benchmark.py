import os
"""R20 DOP853 IVP comparison and matched-accuracy wall timing (not production)."""
from pathlib import Path
import json, math, statistics, time
import numpy as np
from scipy.integrate import solve_ivp
from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid,TEMPERATURES_K
from src.grid_exposure import Segment,evolve_source_grid,clock_from_hubble
ROOT=Path(__file__).resolve().parents[1]
PDF=Path(os.environ.get('WU_R20_SOURCE_PDF', str(ROOT/'parent/ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf')))

def ivp(grid,n0,segments,rtol=2e-12,atol=1e-7):
    N=np.array(n0,dtype=float)
    v=1.0
    nfev=0
    for seg in segments:
        k=float(grid.lookup(seg.temperature_K).nominal_m3_s)
        def rhs(t,y):
            J=k*math.exp(-seg.theta_s*t)/v*y[0]*y[1]
            return np.array([-J,-J,J,J])
        s=solve_ivp(rhs,(0,seg.duration_s),N,method='DOP853',rtol=rtol,atol=atol)
        if not s.success:raise RuntimeError(s.message)
        N=s.y[:,-1];nfev+=s.nfev
        v*=math.exp(seg.theta_s*seg.duration_s)
    return N/v,nfev

def run():
    grid=load_native_grid(PDF)
    n0=(1.2e6,1.9e6,3e5,1e5)
    cases=[]
    for N in (2,8,24,48):
        seg=[Segment(TEMPERATURES_K[(j*3+2)%10],2e8,(-1)**j*2e-11) for j in range(N)]
        exact=evolve_source_grid(grid,n0,seg)
        ref,nfev=ivp(grid,n0,seg)
        err=float(np.max(np.abs(np.array(exact.final_state_m_minus3)-ref)))
        rel=float(np.max(np.abs(np.array(exact.final_state_m_minus3)-ref)/np.maximum(abs(ref),1.)))
        if err>1e-4 and rel>2e-10:raise AssertionError((N,err,rel))
        def time_once(fn,loops):
            start=time.perf_counter()
            for _ in range(loops):fn()
            return (time.perf_counter()-start)/loops
        # Explicitly exclude source-PDF parsing from BOTH timing paths.
        exact_times=[time_once(lambda:evolve_source_grid(grid,n0,seg),200) for _ in range(5)]
        ivp_times=[time_once(lambda:ivp(grid,n0,seg),2) for _ in range(3)]
        cases.append({'segments':N,'nfev':nfev,'max_abs_density_m_minus3':err,
                      'max_rel_density_floor_1':rel,
                      'exact_median_wall_s':statistics.median(exact_times),
                      'DOP853_median_wall_s':statistics.median(ivp_times),
                      'wall_speed_ratio':statistics.median(ivp_times)/statistics.median(exact_times)})
    # Owner-compatible clock quadrature: exact constant-H, FLRW-volume analytic test.
    H=2e-18;a0=.1;a1=.2;k=float(grid.lookup(105).nominal_m3_s)
    exact_E=k*(1-(a0/a1)**3)/(3*H)
    clock=[]
    for n in (2,4,8,16,32):
        c=clock_from_hubble(grid,105,a0,a1,0.,lambda a,q:H,lambda a:(a/a0)**3,nodes=n)
        clock.append({'nodes':n,'exposure_m3':c.exposure_m3,
                      'absolute_error_m3':abs(c.exposure_m3-exact_E),
                      'relative_error':abs(c.exposure_m3-exact_E)/exact_E})
    return {'schema':'wu.r20.numerical_benchmark.v1','method':'DOP853 independent time-dependent comoving IVP vs exact exposure; source PDF parsed once',
            'rtol':2e-12,'atol_density_m_minus3':1e-7,'comparison_threshold':'abs<=1e-4 OR rel<=2e-10',
            'cases':cases,'clock_quadrature':clock,'clock_analytic_exposure_m3':exact_E,
            'benchmark_scope':'local Python wall only; no whole-solver production claim',
            'physical_source_uncertainty':None,'actual_owner_state_bound':False}

if __name__=='__main__':
    r=run();print(json.dumps(r,indent=2))
    (ROOT/'results/NUMERICAL_BENCHMARK.json').write_text(json.dumps(r,indent=2)+'\n')
