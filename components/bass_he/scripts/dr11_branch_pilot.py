#!/usr/bin/env python3
"""Bounded new-shell spectral probe; every attempt is retained, no runtime promotion.

Fold certificates alone do not identify the second physical sheet. This probe
starts BOTH named states from the real axis, follows a specified vertical chart,
then tests their permutation around a small circle and after two circles.
A pass remains path/CF-depth scoped, not a complete higher-shell collision model.
"""
from pathlib import Path
import argparse,json,time,traceback,os,sys
import numpy as np
from bass_he.spectral import find_exceptional_point
from arseny_reimpl.term_complex import continue_complex_from_real,solve_complex_term

ROOT=Path(__file__).resolve().parents[1]

def enc(x):
    if isinstance(x,complex): return [x.real,x.imag]
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)

def write(path,data):
    path=Path(path)
    if path.exists():raise FileExistsError(path)
    b=(json.dumps(data,indent=2,default=enc)+'\n').encode()
    with path.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())

def decode_ep(ep):
    ep=dict(ep)
    for k in ('R','p','lam'):ep[k]=complex(*ep[k])
    return ep

def named_monodromy(ep,steps=48,radius=.001):
    center=ep['R'];R0=center+radius;depth=ep['depth'];t=time.perf_counter()
    states=[tuple(ep['state_a']),tuple(ep['state_b'])]
    anchors=[continue_complex_from_real(s,R0,depth=depth,tol=2e-12,max_complex_step=.01) for s in states]
    z=np.array([[a.p,a.separation_lambda] for a in anchors]);start=z.copy()
    gap=float(np.linalg.norm(start[0]-start[1]))
    if gap<1e-7:raise RuntimeError('named anchors reached duplicate sheets')
    minimum=gap;swap=None;maxres=max(a.residual for a in anchors) if hasattr(anchors[0],'residual') else None
    for k in range(1,2*steps+1):
        R=center+radius*np.exp(2j*np.pi*k/steps)
        for a,state in enumerate(states):
            point=solve_complex_term(state,R,p0=z[a,0],lam0=z[a,1],depth=depth,tol=2e-12)
            z[a]=[point.p,point.separation_lambda]
        minimum=min(minimum,float(np.linalg.norm(z[0]-z[1])))
        if k==steps:swap=float(np.max(np.linalg.norm(z-start[::-1],axis=1))/gap)
    ret=float(np.max(np.linalg.norm(z-start,axis=1))/gap)
    return dict(path='real_axis_anchor_then_vertical_at_Re(Rc)+radius_then_two_CCW_circles',
        start_R=R0,start_points=start.tolist(),radius=radius,steps_per_loop=steps,
        circle_complex_solves=4*steps,anchor_solves_additional=True,
        one_loop_named_swap_error=swap,two_loop_named_restore_error=ret,
        min_sheet_gap=minimum,anchor_gap=gap,
        passed=bool(swap<2e-6 and ret<2e-6 and minimum>1e-7),
        wall_seconds=time.perf_counter()-t)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lower',type=int,required=True)
    ap.add_argument('--depth',type=int,default=96);ap.add_argument('--cached-fold')
    ap.add_argument('--ell',type=int,default=1);ap.add_argument('--emm',type=int,default=0)
    ap.add_argument('--output',required=True);ap.add_argument('--radius',type=float,default=.001)
    args=ap.parse_args();t=time.perf_counter()
    if not 0 <= args.emm <= args.ell < args.lower: ap.error('require 0 <= m <= l < lower N')
    record={'lower_N':args.lower,'upper_N':args.lower+1,'l':args.ell,'m':args.emm,
        'depth':args.depth,'scientific_role':'S_SERIES_NEW_SHELL_PATH_SCOPED_PILOT',
        'full_nmax_dynamics_executed':False,'stueckelberg_or_cross_section_computed':False}
    try:
        if args.cached_fold:
            ep=decode_ep(json.loads(Path(args.cached_fold).read_text())['result'])
            if ep['depth']!=args.depth or tuple(ep['state_a'])!=(args.lower,args.ell,args.emm):raise ValueError('cache metadata mismatch')
            record['fold_reused_from']=args.cached_fold
        else:
            seed=(args.ell+.5)**2/3*np.exp(1j*np.pi*(args.emm+1)/(2*args.ell+1))
            ep=find_exceptional_point((args.lower,args.ell,args.emm),(args.lower+1,args.ell,args.emm),seed,depth=args.depth)
        record['fold']=ep
        record['named_monodromy']=named_monodromy(ep,radius=args.radius)
        record['execution']='PASS_SCOPED' if record['named_monodromy']['passed'] else 'FAIL_NAMED_PAIR'
    except Exception as e:record.update(execution='FAIL',error=str(e),traceback=traceback.format_exc())
    record['wall_seconds']=time.perf_counter()-t
    write(args.output,record);print(json.dumps(record,indent=2,default=enc))
    return 0 if record['execution']=='PASS_SCOPED' else 1
if __name__=='__main__':sys.exit(main())
