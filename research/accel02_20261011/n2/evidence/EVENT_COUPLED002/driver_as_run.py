#!/usr/bin/env python3
"""Event-bounded consumer of the root's actual native coupled H/He driver.

No duplicate gas/RHS implementation: load the exact supplied root driver and N1
provider; reduce dormant photon coordinates algebraically until source entry.
At event endpoints, rate evaluation takes the open segment's one-sided spectral
limit within64 binary64eps. This is a threshold convention, not clipping a state.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time,traceback,types
from pathlib import Path
import numpy as np
from scipy.integrate import BDF
from events import crossing_events,restart_boundaries,native_jump_energies
import characteristics


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-driver',type=Path,required=True)
    parser.add_argument('--n1',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--energy',type=int,default=128)
    parser.add_argument('--angle',type=int,default=2)
    parser.add_argument('--shear',type=float,default=0.)
    parser.add_argument('--rtol',type=float,default=1e-9)
    parser.add_argument('--max-step',type=float,default=1/256)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    import importlib.util
    spec=importlib.util.spec_from_file_location('n2_root_coupled',args.base_driver)
    base=importlib.util.module_from_spec(spec);sys.modules[spec.name]=base;spec.loader.exec_module(base)
    n1=base.load('n2_event_n1',args.n1/'provider.py')
    provider=n1.HistoryProvider(args.shear)
    native=n1.Native(args.n1/'native/target/release/rei_n1_native')
    p=base.Coupled(provider,native,characteristics,args.energy,args.angle,coordinate='energy')
    knots=np.array(sorted(set([10.,13.60,24.59,54.42,50000.]+native_jump_energies(provider.tables['emissivity']))))
    eventlist=crossing_events(p.q,p.mu,provider.geometry,p.end,knots)
    boundaries=restart_boundaries(eventlist)
    # Derivative kinks in native redshift interpolation are also explicit stops.
    ztimes=[provider.background.time_of_redshift(float(z))/p.end for z in provider.tables['emissivity'].redshifts
            if provider.z_final<z<provider.z_initial]
    boundaries=np.unique(np.r_[boundaries,ztimes])
    identity=dict(base_driver=str(args.base_driver),base_sha=sha(args.base_driver),driver_sha=sha(__file__),
                  events_sha=sha(Path(__file__).with_name('events.py')),n1_sha=sha(args.n1/'provider.py'),
                  native_sha=native.binary_sha256,input_identity=provider.identity,
                  args={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},
                  event_count=len(eventlist),segment_count=len(boundaries)-1,
                  semantics='current-energy open-segment one-sided limits; dormant=analytic zero; no state clipping')
    (args.output/'IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n')
    (args.output/'EVENTS.json').write_text(json.dumps(dict(events=eventlist,boundaries=boundaries.tolist()),indent=2)+'\n')
    context={};max_shift=0.
    def coefficients(self,t):
        nonlocal max_shift
        if t!=self.cache_t:
            g=self.provider.geometry(t);e,mu,ratio=self.char.geometry_nodes(self.q,self.mu,g)
            ee=e.copy();lower=context['lower'];upper=context['upper']
            lo=ee<=lower;hi=ee>=upper
            ee[lo]=np.nextafter(lower[lo],np.inf);ee[hi]=np.nextafter(upper[hi],0.)
            relative=np.max(abs(ee-e)/e)
            if relative>64*np.finfo(float).eps:raise ValueError(f'EVENT_SPECTRAL_CELL_MISMATCH:{relative}')
            max_shift=max(max_shift,float(relative))
            inside=context['source_inside'];source=np.zeros(self.n)
            source[inside]=self.provider.tables['emissivity'].photon_emission_log(ee[inside],g['z'])*self.weights[inside]/ratio[inside]**3
            sigma=np.zeros((self.n,3));active=context['active']
            sigma[active]=self.native.call('SIGMA',ee[active]).reshape(-1,3)
            self.cache=(g,ee,mu,source,sigma);self.cache_t=t
        return self.cache
    p.coefficients=types.MethodType(coefficients,p)
    full=p.y0/p.scales; samples=np.linspace(0,1,129);si=0;rows=[];sample_v=[];sample_u=[]
    accepted_min=np.inf;accepted_energy=accepted_number=0.;completed_segments=0
    started=time.monotonic();failure=None;solver=None;status='RUNNING'
    try:
        for segment,(u0,u1) in enumerate(zip(boundaries[:-1],boundaries[1:])):
            em=characteristics.geometry_nodes(p.q,p.mu,provider.geometry(float(.5*(u0+u1)*p.end)))[0]
            cell=np.searchsorted(knots,em,side='right')
            extended=np.r_[0.,knots,np.inf]
            context.update(lower=extended[cell],upper=extended[cell+1],active=np.flatnonzero(em<50000.),
                           source_inside=(em>10.)&(em<50000.))
            p.cache_t=None
            active=context['active']
            keep=np.r_[np.arange(4),4+active,np.arange(4+p.n,10+p.n)]
            # Omitted variables have analytic N=0 on this whole segment. Newly
            # entering nodes inherit their untouched exact-zero initial state.
            dormant=np.setdiff1d(np.arange(p.n),active)
            if np.any(full[4+dormant]!=0):raise ValueError('NONZERO_DORMANT_STATE_NOT_DISCARDED')
            def expand(reduced):
                out=np.zeros_like(full);out[keep]=reduced;return out
            def rhs(u,v):return p.rhs(u,expand(v))[keep]
            def jac(u,v):return p.jac(u,expand(v))[keep][:,keep]
            if si==0:
                rows.append(p.output(0.,full));sample_u.append(0.);sample_v.append(full.copy());si=1
            solver=BDF(rhs,float(u0),full[keep],float(u1),rtol=args.rtol,atol=args.rtol*1e-8,
                       jac=jac,max_step=args.max_step)
            while solver.status=='running':
                msg=solver.step()
                if solver.status=='failed':raise RuntimeError(msg)
                current=expand(solver.y)
                physical=current*p.scales
                accepted_min=min(accepted_min,float(physical[4:4+p.n].min()))
                # All full numerical states are retained in restart artifacts;
                # strict accepted positivity is a gate, never a clip operation.
                if physical[4:4+p.n].min()<0:raise ValueError('ACCEPTED_NEGATIVE_ACTIVE_PHOTON')
                dense=solver.dense_output()
                while si<len(samples) and samples[si]<=solver.t:
                    u=float(samples[si]);v=expand(dense(u));row=p.output(u,v)
                    rows.append(row);sample_u.append(u);sample_v.append(v);si+=1
                # Assess accepted ledger at each segment endpoint below, and
                # retain requested common epochs without extra native calls.
            full=expand(solver.y);completed_segments+=1
            endpoint=p.output(float(u1),full)
            accepted_energy=max(accepted_energy,abs(endpoint['energy_ledger_scaled']))
            accepted_number=max(accepted_number,abs(endpoint['number_ledger_scaled']))
            progress=dict(completed_segments=completed_segments,total_segments=len(boundaries)-1,
                          u=float(u1),z=endpoint['z'],rhs_calls=p.calls,elapsed_s=time.monotonic()-started,
                          energy_ledger_max=accepted_energy,number_ledger_max=accepted_number)
            (args.output/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
            if segment%16==0:
                np.savez_compressed(args.output/'RESTART.npz',u=u1,scaled_y=full,scales=p.scales)
        status='COMPUTED_NOT_REVIEWED'
    except Exception as exc:
        status='FAILED_PRESERVED'
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
                     completed_segments=completed_segments,last_accepted_u=None if solver is None else float(solver.t))
        (args.output/'FIRST_FAILURE.json').write_text(json.dumps(failure,indent=2)+'\n')
        if solver is not None:np.savez_compressed(args.output/'LAST_ACCEPTED.npz',u=solver.t,scaled_y=expand(solver.y),scales=p.scales)
    finally:native.close()
    np.savez_compressed(args.output/'history.npz',u=sample_u,scaled_states=np.array(sample_v),scales=p.scales,q=p.q,mu=p.mu,weights=p.weights)
    checks=dict(whole_interval=status=='COMPUTED_NOT_REVIEWED',sampled_positive=all(row['min_N_ref']>=0 for row in rows),
                accepted_positive=accepted_min>=0,energy_ledger=accepted_energy<=1e-9,number_ledger=accepted_number<=1e-9)
    result=dict(status=status,checks=checks,completed_segments=completed_segments,elapsed_s=time.monotonic()-started,
                rhs_calls=p.calls,jac_calls=p.jcalls,n_nodes=p.n,max_local_number=p.max_local_number,max_local_energy=p.max_local_energy,
                max_endpoint_energy_ledger=accepted_energy,max_endpoint_number_ledger=accepted_number,
                min_accepted_photon_energy=accepted_min,max_one_sided_relative_energy_shift=max_shift,history=rows,failure=failure)
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['history','failure']},indent=2),flush=True)
    return 0 if all(checks.values()) else 1


if __name__=='__main__':raise SystemExit(main())
