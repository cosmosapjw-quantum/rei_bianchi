#!/usr/bin/env python3
"""New PILOT01 map005 diagnostic; no native coupled step or old trial replay.

Recomputes changed source only for a newly requested exact failed boundary.
Moment measure uses a constant manufactured sigma to inspect q/P arithmetic;
it is NOT physical opacity evaluation or authorization to bypass its guard.
"""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np
H=Path(__file__).resolve().parent;Q=H.parent.parent
sys.path[:0]=[str(H/'_runtime_deps'),str(H),str(Q),str(Q/'c10'),str(Q.parent/'n1')]
import mpmath as mp
from provider import HistoryProvider
from source_cells import CellSource
from grid_cells import load_grid
from source_precision import integrate_source,advance_source,provider_event_times
from reference_mp import cell_moments,ray
from reconstruction import reconstruct
from positive_absorption import _measure


def main():
    inp=H.parent/'integration/evidence/PILOT01';out=H/'evidence/PILOT01_FAILED_MEAN';out.mkdir(exist_ok=False)
    request=json.loads((inp/'TRIAL_MAP_005_REQUEST.json').read_text());t1=request['t1_s'];t0=request['t0_s']
    p=HistoryProvider(r=0.);s=CellSource(p,load_grid(Q/'GRID_C2.json'))
    with np.load(inp/'TRIAL_MAP_005_INPUT.npz') as f:N0,U0=f['N'].copy(),f['U_eV'].copy()
    birth=int(np.flatnonzero(s.edges[:-1]==50000.)[0]);a=float(s.edges[birth])
    result=integrate_source(s,t0,t1,event_times=provider_event_times(s,t0,t1));advanced=advance_source(N0,U0,result)
    R=float(result['R1'][0]);N=float(advanced['N'][0,birth]);U=float(advanced['U_eV'][0,birth]);b=min(float(s.edges[birth+1]),50000./R)
    c=reconstruct(N,U,R,a,b)
    data={'scope':'new exact failed-boundary mean diagnostic only; no native calls; generic guard remains unrevised','input_request':request,
      'source_sha256':hashlib.sha256((H/'source_precision.py').read_bytes()).hexdigest(),
      'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'input_npz_sha256':hashlib.sha256((inp/'TRIAL_MAP_005_INPUT.npz').read_bytes()).hexdigest(),
      'born_cell':birth,'h_s':t1-t0,'N':N,'U_eV':U,'R':R,'support_q_eV':[a,b],
      'reconstructed_mean_q_eV':c.mean_q,'reconstructed_p':c.p,
      'unchanged_generic_indicator':32*math.ulp(b)/min(c.mean_q-a,b-c.mean_q),
      'source_time_diagnostics':result['diagnostics']}
    np.savez_compressed(out/'SOURCE_ARITHMETIC.npz',**{k:v for k,v in result.items() if isinstance(v,np.ndarray)},N=advanced['N'],U_eV=advanced['U_eV'])
    with mp.workdps(80):
        tt=mp.mpf(t1); nn=mp.quad(lambda u:tt*cell_moments(s,tt*u,birth)[0],[0,1]);qq=mp.quad(lambda u:tt*cell_moments(s,tt*u,birth)[1],[0,1])
        exact_mean=qq/nn; exact_b=mp.mpf(50000)/ray(p.background,tt)
        stored_mean=mp.mpf(U)/(mp.mpf(R)*mp.mpf(N)); recon_mean=mp.mpf(c.mean_q)
        data['mp80']={'source_N_decimal':str(nn),'source_Q_decimal':str(qq),'source_mean_decimal':str(exact_mean),'source_support_b_decimal':str(exact_b),'stored_rational_mean_decimal':str(stored_mean),
          'recon_minus_source_mean_abs_eV':float(recon_mean-exact_mean),'stored_minus_source_mean_abs_eV':float(stored_mean-exact_mean),'recon_minus_stored_mean_abs_eV':float(recon_mean-stored_mean),
          'recon_mean_source_offset_relative_error':float(abs(recon_mean-exact_mean)/(exact_mean-a)),
          'stored_source_offset_relative_error':float(abs(stored_mean-exact_mean)/(exact_mean-a)),
          'provider_support_b_minus_mp_source_eV':float(mp.mpf(b)-exact_b)}
        # Same SUPPORT mean sensitivity: monotone exponential power-law family
        # has W1 distance=abs(delta mean) under its quantile coupling.
        dm=abs(recon_mean-stored_mean)
        L=mp.mpf('8.8');Lheat=mp.mpf('24303.5');width=mp.log(mp.mpf(b)/a)
        bound=lambda slope: float(slope*mp.exp(slope*width)*dm/a)
        data['same_support_mean_rounding_bound']={
          'comparison':'binary64 reconstructed mean vs exact rational mean of authoritative stored N,U,R; same support',
          'assumptions':'positive smooth native kernel throughout this50keV cell; power-law closure stochastic ordering; known log-slope bounds supplied by endpoint lane',
          'sigma_log_slope_bound':float(L),'heat_log_slope_bound_conservative':float(Lheat),
          'K0_relative_bound':bound(L),'KE_relative_bound':bound(L+1),'heat_relative_bound':bound(Lheat),
          'does_not_cover':'source model accuracy, changing support, threshold crossing, native floating arithmetic, absorption propagation or newhistory admission'}
        data['measures']={}
        for order in (64,128):
            measure=_measure(c,lambda E:np.ones((len(E),3)),order,[])
            sn=mp.fsum(mp.mpf(float(x)) for x in measure.P)
            sq=mp.fsum(mp.mpf(float(x))*mp.mpf(float(y)) for x,y in zip(measure.q,measure.P))
            mm=sq/sn
            data['measures'][str(order)]={'scope':'manufactured constantsigma used only to construct identical q/probability rule; no physical opacity gate passed',
              'diagnostics':measure.diagnostics,
              'mp_number_vs_authoritative_relative':float(abs(sn-N)/N),
              'mp_energy_vs_authoritative_relative':float(abs(mp.mpf(R)*sq-U)/U),
              'mp_mean_minus_stored_rational_eV':float(mm-stored_mean),
              'mp_mean_minus_reconstructed_eV':float(mm-recon_mean),
              'mp_mean_vs_reconstructed_offset_relative':float(abs(mm-recon_mean)/(recon_mean-a)),
              'strict_q_support':bool(np.all((measure.q>a)&(measure.q<b)))}
            np.savez_compressed(out/('MEASURE_'+str(order)+'.npz'),q=measure.q,P=measure.P)
    data['interpretation']='No evidence authoritative D is needed solely to represent this50keV boundary kernel at1e-7; source offset loses about1e-9 relative but authoritative-energy mean rounding is about1e-16 relative and smooth-kernel bound far below1e-7. This cannot clear endpoint crossing/trace or nonlinear wholehistory accuracy; generic refusal unchanged until separately justified provider-specific implementation.'
    with (out/'RESULT.json').open('x') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(data,indent=2,allow_nan=False))
if __name__=='__main__':main()
