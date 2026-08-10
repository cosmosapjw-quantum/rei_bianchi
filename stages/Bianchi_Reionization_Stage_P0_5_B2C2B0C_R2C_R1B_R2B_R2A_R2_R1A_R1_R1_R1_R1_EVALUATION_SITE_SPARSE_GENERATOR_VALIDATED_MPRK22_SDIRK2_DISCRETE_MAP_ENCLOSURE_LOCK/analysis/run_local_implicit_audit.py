#!/usr/bin/env python3
"""46,080-node frozen-state local implicit audit.

This audit encloses the four branch corners at each population source site while
holding the corresponding material state fixed.  It isolates local MPRK block
conditioning from the still-unclosed cross-site/state-feedback remainder.
"""
from __future__ import annotations
import importlib.util,json,sys,time,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
CORNERS=(('CELL_LOWER_STRICT',0.1),('CELL_LOWER_STRICT',1.0),('CELL_UPPER_STRICT',0.1),('CELL_UPPER_STRICT',1.0))

def load(name,path):
    if name in sys.modules:return sys.modules[name]
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

r1a=next(REPO.glob('stages/*R2_R1A_FOUR_CORNER*'))
trial=load('evalsite_local_parent_trial',r1a/'analysis/uncertainty_trial.py')
cert=load('evalsite_local_certificates',HERE/'implicit_certificates.py')
mprk=trial.fast.base.mprk;sdirk=trial.fast.sdirk

def lhs_from_flux(flux,denominator,dt):
    G=mprk._generator(np.asarray(flux),np.asarray(denominator))
    s=denominator.shape[1]
    return np.eye(s)[None,:,:]-float(dt)*G

def block_certificate(matrices,y0,sl):
    mats=np.asarray(matrices)[:,:,sl,sl]
    lo=np.min(mats,axis=0);hi=np.max(mats,axis=0)
    b=np.asarray(y0)[:,sl]
    c=cert.linear_interval_krawczyk(lo,hi,b,b)
    return {
      'node_count':int(len(b)),'certified_count':int(np.count_nonzero(c.certified)),
      'all_certified':bool(np.all(c.certified)),'max_row_sum_bound':float(np.max(c.row_sum_bound)),
      'p99_row_sum_bound':float(np.quantile(c.row_sum_bound,0.99)),
      'max_radius':float(np.max(c.radius[np.isfinite(c.radius)])) if np.any(np.isfinite(c.radius)) else math.inf,
    },c,lo,hi

def corner_solver(base,lane,vp,fv):
    return trial.UncertaintySecondOrderTrial(base=base,lane=lane,v_policy=vp,f_value=fv)

def run_lane(lane):
    base=trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane)
    parent=base.inputs.state0.mutable_copy();y0=np.asarray(parent.values[:5].T,float)
    duration=base.forcing.duration_seconds(0);dt=duration/2048.0
    p0=base.forcing.point(interval=0,time_s=0.0);p1=base.forcing.point(interval=0,time_s=dt)
    solvers=[corner_solver(base,lane,*c) for c in CORNERS]
    o0=solvers[0]._owner(parent,p0)
    f0s=[];predictors=[];predictor_states=[];thermal_predictors=[]
    for solver in solvers:
        _,f0,photo0,volume0,_,_=solver._rhs_flux(parent,o0,p0)
        pred=mprk.patankar_euler(y0=y0,flux=f0,dt=dt)
        tp=sdirk.solve_backward_euler_fast(
            populations=pred,parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
            volume=volume0,photoheat=photo0.heating,hubble=np.full(parent.node_count,p0.hubble_s_inv),
            dt=np.full(parent.node_count,dt))
        if not np.all(tp.bracketed):raise RuntimeError('predictor thermal root failed')
        st=base.tensor.ArrayState(np.ascontiguousarray(np.vstack([pred.T,tp.energy])),np.ascontiguousarray(tp.temperature))
        f0s.append(f0);predictors.append(pred);predictor_states.append(st);thermal_predictors.append(tp)
    A1=np.stack([lhs_from_flux(f,y0,dt) for f in f0s])
    cross_block_max=float(max(np.max(np.abs(A1[:,:,0:2,2:5])),np.max(np.abs(A1[:,:,2:5,0:2]))))
    stage1_h,c1h,_,_=block_certificate(A1,y0,slice(0,2));stage1_he,c1he,_,_=block_certificate(A1,y0,slice(2,5))

    A2=[];lower_corrector=None;lower_f1=None
    for ia,(f0,pred,st) in enumerate(zip(f0s,predictors,predictor_states)):
        for ib,solver in enumerate(solvers):
            o1=solver._owner(st,p1)
            _,f1,_,_,_,_=solver._rhs_flux(st,o1,p1)
            A2.append(lhs_from_flux(0.5*(f0+f1),pred,dt))
            if ia==0 and ib==0:lower_f1=f1;lower_corrector=mprk.mprk22_corrector(y0=y0,predictor=pred,stage_flux=f0,final_flux=f1,dt=dt)
    A2=np.stack(A2)
    cross_block_max=max(cross_block_max,float(max(np.max(np.abs(A2[:,:,0:2,2:5])),np.max(np.abs(A2[:,:,2:5,0:2])))))
    stage2_h,c2h,_,_=block_certificate(A2,y0,slice(0,2));stage2_he,c2he,_,_=block_certificate(A2,y0,slice(2,5))

    # Tangent parity on a deterministic subset of actual lower-corner corrector matrices.
    lower_A=A2[0];upper_A=A2[-1];indices=np.linspace(0,parent.node_count-1,256,dtype=int)
    A=lower_A[indices];z=np.linalg.solve(A,y0[indices,...,None])[...,0]
    dA=0.5*(upper_A[indices]-lower_A[indices]);db=np.zeros_like(z)
    dz=cert.implicit_linear_tangent(A,z,dA,db);eps=2.0e-6
    zp=np.linalg.solve(A+eps*dA,y0[indices,...,None])[...,0];zm=np.linalg.solve(A-eps*dA,y0[indices,...,None])[...,0]
    tangent_error=float(np.max(np.abs(dz-(zp-zm)/(2*eps))/np.maximum(np.abs(dz),1.0)))

    # Reproduce the lower-corner coupled thermal fixed point and audit root denominators.
    solver=solvers[0];predictor=predictors[0];tp=thermal_predictors[0];corrector=lower_corrector
    pg=base.forcing.point(interval=0,time_s=sdirk.GAMMA*dt)
    gamma_pop=mprk.patankar_euler(y0=y0,flux=f0s[0],dt=sdirk.GAMMA*dt)
    stage_temperature=parent.temperature_K.copy();final_temperature=tp.temperature.copy();thermal=None;ctxg=None;ctxf=None
    for outer in range(24):
        ge=sdirk.energy_from_temperature(gamma_pop,stage_temperature)
        gs=base.tensor.ArrayState(np.ascontiguousarray(np.vstack([gamma_pop.T,ge])),np.ascontiguousarray(stage_temperature))
        og=solver._owner(gs,pg);eg,photog,vg=solver._event_evaluation(gs,og,pg)
        fe=sdirk.energy_from_temperature(corrector,final_temperature)
        fs=base.tensor.ArrayState(np.ascontiguousarray(np.vstack([corrector.T,fe])),np.ascontiguousarray(final_temperature))
        of=solver._owner(fs,p1);ef,photof,vf=solver._event_evaluation(fs,of,p1)
        thermal=sdirk.solve_sdirk2_fast(
            parent_populations=y0,stage_populations=gamma_pop,final_populations=corrector,
            parent_energy=parent.values[5],parent_temperature=parent.temperature_K,
            stage_volume=vg,final_volume=vf,stage_photoheat=photog.heating,final_photoheat=photof.heating,
            stage_hubble=np.full(parent.node_count,pg.hubble_s_inv),final_hubble=np.full(parent.node_count,p1.hubble_s_inv),
            dt=np.full(parent.node_count,dt))
        residual=max(float(np.max(np.abs(np.log(thermal.stage.temperature)-np.log(stage_temperature)))),float(np.max(np.abs(np.log(thermal.final.temperature)-np.log(final_temperature)))))
        stage_temperature=thermal.stage.temperature.copy();final_temperature=thermal.final.temperature.copy()
        if residual<=1e-10:break
    if thermal is None:raise RuntimeError('thermal solve missing')
    ctxg=sdirk.ThermalContext.build(gamma_pop,vg,photog.heating,np.full(parent.node_count,pg.hubble_s_inv))
    ctxf=sdirk.ThermalContext.build(corrector,vf,photof.heating,np.full(parent.node_count,p1.hubble_s_inv))
    rg,drg=ctxg.rhs_and_derivative(np.log(thermal.stage.temperature));rf,drf=ctxf.rhs_and_derivative(np.log(thermal.final.temperature))
    dEg=ctxg.energy_coefficient*thermal.stage.temperature;dEf=ctxf.energy_coefficient*thermal.final.temperature
    denom_g=dEg-sdirk.GAMMA*dt*drg;denom_f=dEf-sdirk.GAMMA*dt*drf
    res_g=sdirk.energy_from_temperature(gamma_pop,thermal.stage.temperature)-parent.values[5]-sdirk.GAMMA*dt*rg
    res_f=sdirk.energy_from_temperature(corrector,thermal.final.temperature)-parent.values[5]-dt*((1-sdirk.GAMMA)*rg+sdirk.GAMMA*rf)
    thermal_audit={
      'stage_denominator_min_abs':float(np.min(np.abs(denom_g))),
      'final_denominator_min_abs':float(np.min(np.abs(denom_f))),
      'stage_denominator_min_relative_to_dE':float(np.min(np.abs(denom_g)/np.maximum(np.abs(dEg),np.finfo(float).tiny))),
      'final_denominator_min_relative_to_dE':float(np.min(np.abs(denom_f)/np.maximum(np.abs(dEf),np.finfo(float).tiny))),
      'stage_denominator_nonpositive_count':int(np.count_nonzero(denom_g<=0)),
      'final_denominator_nonpositive_count':int(np.count_nonzero(denom_f<=0)),
      'stage_balance_max_relative':float(np.max(np.abs(res_g)/np.maximum(np.abs(parent.values[5]),1.0))),
      'final_balance_max_relative':float(np.max(np.abs(res_f)/np.maximum(np.abs(parent.values[5]),1.0))),
      'outer_iterations':int(outer+1),
      'interval_derivative_certificate':False,
      'claim':'POINT_TRAJECTORY_DENOMINATOR_MARGIN_ONLY',
    }
    return {
      'lane':lane,'node_count':parent.node_count,'partition':2048,'dt_s':dt,
      'cross_element_block_max_abs':cross_block_max,
      'stage1_H':stage1_h,'stage1_He':stage1_he,'stage2_H':stage2_h,'stage2_He':stage2_he,
      'implicit_tangent_max_relative_error':tangent_error,'thermal':thermal_audit,
      'all_local_population_blocks_certified':bool(stage1_h['all_certified'] and stage1_he['all_certified'] and stage2_h['all_certified'] and stage2_he['all_certified']),
    }

def main():
    started=time.perf_counter();rows=[run_lane(x) for x in LANES]
    result={'classification':'FROZEN_STATE_LOCAL_IMPLICIT_CERTIFICATE_AUDIT','rows':rows,
      'all_lanes_population_pass':all(r['all_local_population_blocks_certified'] for r in rows),
      'thermal_interval_certificate_closed':False,
      'full_discrete_map_enclosure_closed':False,
      'claim_boundary':'Population Krawczyk hulls freeze each site material state; thermal results are point-trajectory denominator margins. Cross-site/state-feedback remainder remains unclosed.',
      'elapsed_s':time.perf_counter()-started}
    (STAGE/'data/LOCAL_IMPLICIT_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'population_pass':result['all_lanes_population_pass'],'thermal_interval':False,'elapsed_s':result['elapsed_s'],
      'rows':[{'lane':r['lane'],'s1H':r['stage1_H']['max_row_sum_bound'],'s1He':r['stage1_He']['max_row_sum_bound'],'s2H':r['stage2_H']['max_row_sum_bound'],'s2He':r['stage2_He']['max_row_sum_bound'],'tangent':r['implicit_tangent_max_relative_error'],'thermal_stage_rel_margin':r['thermal']['stage_denominator_min_relative_to_dE'],'thermal_final_rel_margin':r['thermal']['final_denominator_min_relative_to_dE']} for r in rows]},indent=2))
    return 0 if result['all_lanes_population_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
