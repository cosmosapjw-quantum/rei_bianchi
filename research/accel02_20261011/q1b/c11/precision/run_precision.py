#!/usr/bin/env python3
"""Create-only new C11 source birth checks, same-formula mpmath oracle.
No old completed source scan or native history replay is performed.
"""
from pathlib import Path
import sys,json,hashlib,time,math
from datetime import datetime,timezone
import numpy as np
HERE=Path(__file__).resolve().parent;Q1B=HERE.parent.parent
sys.path[:0]=[str(HERE/'_runtime_deps'),str(HERE),str(Q1B),str(Q1B.parent/'n1')]
import mpmath as mp
from source_precision import integrate_source,advance_source,provider_event_times,StableCellSource,ray_difference,log_ray,SourceEntryError
from source_cells import CellSource
from grid_cells import load_grid
from provider import HistoryProvider
from reference_mp import cell_moments,ray

def dump(path,obj):
    with path.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def rel(a,b):return float(abs(mp.mpf(a)-b)/abs(b)) if b else (0. if a==0 else None)

def main():
    out=HERE/'evidence'/'ACTUAL_NEW_SOURCE';out.mkdir(exist_ok=False)
    p=HistoryProvider(r=0.);s=CellSource(p,load_grid(Q1B/'GRID_C2.json'));stable=StableCellSource(s)
    files=[HERE/'source_precision.py',HERE/'reference_mp.py',HERE/'test_precision.py',Path(__file__),Q1B/'c10/source_entry.py',Q1B/'source_cells.py',Q1B/'GRID_C2.json']
    dump(out/'INPUTS.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':{str(f.relative_to(Q1B)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
        'provider':p.identity,'mpmath_version':mp.__version__,
        'same_formula_reference':'80 decimal digits; exact binary64 constants/table inputs; independent arithmetic, shared physical data and equations',
        'old_replays':0,'criteria_changed':False})
    saved=np.load(Q1B/'evidence/SOURCE_C2.npz');N0=saved['initial_N'];U0=saved['initial_U_eV'];saved.close()
    born=int(np.flatnonzero(s.edges[:-1]==50000.)[0]);results=[]
    start=time.monotonic()
    for h in (5e9,2.5e9):
        t0=time.monotonic()
        try:
            result=integrate_source(stable,0.,h,event_times=provider_event_times(s,0.,h))
            advanced=advance_source(N0,U0,result)
            record={'h_s':h,'pass':True,'diagnostics':result['diagnostics'],'advance_diagnostics':advanced['diagnostics']}
            with (out/('h_'+format(h,'.0f')+'.npz')).open('xb') as f:
                np.savez_compressed(f,**{k:v for k,v in result.items() if isinstance(v,np.ndarray)},N_final=advanced['N'],U_final_eV=advanced['U_eV'])
        except SourceEntryError as error:
            record={'h_s':h,'pass':False,'error':str(error),'diagnostics':error.diagnostics}
            result=None
        record['source_elapsed_s']=time.monotonic()-t0
        # Independently integrate only the actually born source cell (all active
        # old C10 cells are not repeated as a new source-partition validation).
        if result is not None:
            with mp.workdps(80):
                horizon=mp.mpf(h);r1=ray(p.background,horizon)
                refs=[]
                for q in range(5):
                    def integrand(u):
                        t=horizon*u;n,Q,D=cell_moments(s,t,born)
                        rr=ray(p.background,t)
                        return horizon*(n,Q,rr*Q,(rr-r1)*Q,D)[q]
                    refs.append(mp.quad(integrand,[0,1]))
                names=('dN','dQ','injected_energy_eV','radiation_source_work_eV','dD_eV')
                record['born_cell_mp80_reference']={k:{'value_decimal':str(v),'relative_error':rel(result[k][0,born],v)} for k,v in zip(names,refs)}
                naive=float(result['dQ'][0,born]-s.edges[born]*result['dN'][0,born])
                record['offset_cancellation']={'D_direct_eV':float(result['dD_eV'][0,born]),'Q_minus_aN_eV':naive,'naive_relative_error':rel(naive,refs[4]),'direct_relative_error':rel(result['dD_eV'][0,born],refs[4])}
                # Error breakdown at midpoint compares old instantaneous source
                # arithmetic once, NOT old rejected time integration/replay.
                mid=h*.5;legacy=s.source(mid);new=stable.source(mid);ref=cell_moments(s,mp.mpf(mid),born)
                exact_r=ray(p.background,mp.mpf(mid));exact_delta=exact_r-ray(p.background,h)
                lr=legacy['R'][0];nr=new['R'][0]
                old_dr=lr-p.ray(np.ones(len(s.mu)),s.mu,h)[2][0]
                old_span=50000./lr-50000.;new_span=50000.*math.expm1(-log_ray(p.background,mid));ref_span=mp.mpf(50000)/exact_r-50000
                record['midpoint_error_breakdown']={
                    'legacy_R':rel(lr,exact_r),'stable_R':rel(nr,exact_r),
                    'legacy_R_difference':rel(old_dr,exact_delta),'stable_R_difference':rel(ray_difference(p.background,mid,h),exact_delta),
                    'legacy_reachable_q_width':rel(old_span,ref_span),'stable_reachable_q_width':rel(new_span,ref_span),
                    'legacy_source_N':rel(legacy['N'][0,born],ref[0]),'stable_source_N':rel(new['N'][0,born],ref[0]),
                    'legacy_source_Q':rel(legacy['Q_eV'][0,born],ref[1]),'stable_source_Q':rel(new['Q_eV'][0,born],ref[1]),
                    'legacy_source_D_from_Q_minus_aN':rel(legacy['Q_eV'][0,born]-50000.*legacy['N'][0,born],ref[2]),
                    'stable_source_D_direct':rel(new['D_eV'][0,born],ref[2])}
        record['elapsed_s']=time.monotonic()-t0
        dump(out/('h_'+format(h,'.0f')+'.json'),record)
        results.append(record)
        print(json.dumps(record,allow_nan=False),flush=True)
    final={'status':'LOCAL_SOURCE_PRECISION_CHECKED' if all(r['pass'] for r in results) else 'REWORK',
        'results':results,'elapsed_s':time.monotonic()-start,'claim_ceiling':'new source birth arithmetic only; no native mean/opacity or full-history admission','native_calls':0,'old_replays':0}
    dump(out/'RESULT.json',final)
    return 0 if all(r['pass'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
