"""Transparent diagnostic capture around immutable v3 positive_native_step.

Only the two explicit dependency objects are pass-through proxies. Every actual
prepare/absorb/RHS call occurs once with original arguments and return value;
no global patch, hidden re-evaluation, N/U reconstruction or changed gas solve.
The final converged RHS input/absorption result is retained for output ownership.
"""
from __future__ import annotations
import copy
import math
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import native_step_v3 as _v3
from native_step_v3 import EV_ERG,CHI,COUNTER_NAMES,gas_temperature
from cell_history_fields import physical_state_sha256


def _capture_kernel(state,geometry,cells,direct,gamma,*,owner,native_evaluations):
    cells=np.asarray(cells,float);direct=np.asarray(direct,float)
    scale_factor=float(geometry['a_rel']);volume=scale_factor*scale_factor*scale_factor
    if cells.ndim!=2 or cells.shape[1]!=13 or direct.shape!=(len(cells),3):raise ValueError('OUTPUT24_KERNEL_SHAPE')
    K0=cells[:,7:10];KE=cells[:,10:13]
    if not np.isfinite(cells).all() or not np.isfinite(direct).all():raise ValueError('OUTPUT24_KERNEL_FINITE')
    # Reproduce native Rust per-cell arithmetic/accumulation order. This is the
    # exact same discretized measure, not (sum KE - chi sum K0) reassociation.
    native_gamma=np.zeros(3);heat=np.zeros(3)
    for row in cells:
        for a in range(3):
            native_gamma[a]+=row[7+a]/volume
            heat[a]+=(row[10+a]-CHI[a]*row[7+a])*EV_ERG/volume
    supplied_gamma=np.asarray(gamma,float);gamma_delta=abs(native_gamma-supplied_gamma)
    gamma_scale=abs(supplied_gamma)
    gamma_error=np.divide(gamma_delta,gamma_scale,out=np.zeros(3),where=gamma_scale>0)
    # An arithmetic consistency diagnostic, never a replacement science gate.
    if np.any((gamma_scale==0)&(gamma_delta!=0)) or np.any(gamma_error>64*np.finfo(float).eps):
        raise ArithmeticError('OUTPUT24_NATIVE_GAMMA_OWNER_MISMATCH')
    direct_sum=np.array([math.fsum(direct[:,a])*EV_ERG/volume for a in range(3)])
    delta=abs(heat-direct_sum);scale=abs(direct_sum)
    error=np.divide(delta,scale,out=np.zeros(3),where=scale>0)
    if np.any((scale==0)&(delta!=0)) or np.any(error>1e-7):raise ArithmeticError('OUTPUT24_HEAT_ABI_DIRECT_OWN_COMPONENT')
    return dict(schema='rei.q1b.c12.output24.kernel.v1',owner=owner,time_s=float(state['t_s']),state_sha256=physical_state_sha256(state),gas=np.asarray(state['gas']).tolist(),native_rhs_evaluations=native_evaluations,K0_per_ref_s=K0.tolist(),KE_eV_per_ref_s=KE.tolist(),photoheat_direct_eV_per_ref_s=direct.tolist(),gamma_s=np.asarray(gamma).tolist(),gamma_arithmetic_relative_errors=gamma_error.tolist(),gamma_arithmetic_budget=64*np.finfo(float).eps,gamma_arithmetic_is_science_gate=False,photoheat_per_absorber_erg_s=heat.tolist(),photoheat_direct_per_absorber_erg_s=direct_sum.tolist(),heat_abi_direct_relative_errors=error.tolist(),heat_abi_direct_budget=1e-7,volume_relative=volume,claim='SAME_NATIVE_ENDPOINT_POSITIVE_MEASURE_ONLY')


class _AbsorptionCapture:
    def __init__(self,target):self.target=target;self.pending=[]
    def prepare_incident(self,*args,**kwargs):return self.target.prepare_incident(*args,**kwargs)
    def absorb(self,*args,**kwargs):
        result=self.target.absorb(*args,**kwargs);self.pending.append(result);return result


class _NativeCapture:
    def __init__(self,target,absorption):self.target=target;self.absorption=absorption;self.last=None;self.calls=0
    def rhs(self,t,g,gas,cells):
        output=self.target.rhs(t,g,gas,cells)
        results=self.absorption.pending
        if len(results)!=len(cells):raise ValueError('OUTPUT24_NATIVE_MEASURE_CALL_ALIGNMENT')
        for row,result in zip(cells,results):
            if not np.array_equal(row[7:10],result['K0']) or not np.array_equal(row[10:13],result['KE']):raise ValueError('OUTPUT24_NATIVE_MEASURE_ARGUMENT_IDENTITY')
        self.last=(float(t),dict(g),np.array(gas,copy=True),np.array(cells,copy=True),np.array([r['photoheat_direct'] for r in results]),np.array(output,copy=True))
        self.absorption.pending=[];self.calls+=1
        return output


def positive_native_step(state,t1,source,opacity,native,*,source_api,absorption_api):
    capture=_AbsorptionCapture(absorption_api);rhs=_NativeCapture(native,capture)
    result=_v3.positive_native_step(state,t1,source,opacity,rhs,source_api=source_api,absorption_api=capture)
    if rhs.last is None or capture.pending:raise ValueError('OUTPUT24_NO_FINAL_NATIVE_PAYLOAD')
    t,g,gas,cells,direct,output=rhs.last
    if t!=result['t_s'] or not np.array_equal(gas,result['gas']) or not np.array_equal(cells[:,3],np.asarray(result['N']).ravel()) or not np.array_equal(cells[:,4],np.asarray(result['U_eV']).ravel()):raise ValueError('OUTPUT24_FINAL_NATIVE_STATE_IDENTITY')
    result['diagnostics']['output24_kernel']=_capture_kernel(result,g,cells,direct,output[8:11],owner='ACTUAL_CONVERGED_NATIVE_V3_ATTENUATED_MEASURE',native_evaluations=rhs.calls)
    return result


def initial_output_state(state,source,opacity,*,absorption_api):
    """Output-only h=0 evaluation of original saved IC moments; SIGMA, no RHS.

    Restricted to t=0; cannot masquerade as an evolved map's owned spectrum.
    Original state/counters/arrays unchanged. Root owns one actual invocation.
    """
    if state['t_s']!=0.:raise ValueError('OUTPUT24_H0_INITIAL_ONLY')
    result=dict(state);result['diagnostics']=copy.deepcopy(state.get('diagnostics',{}))
    p=source.provider;g=p.geometry(0.);shape=np.asarray(state['N']).shape
    _,mu,R=p.ray(np.ones(shape[0]),source.mu,0.)
    if not np.array_equal(np.repeat(np.asarray(R)[:,None],shape[1],axis=1),state['R']):raise ValueError('OUTPUT24_INITIAL_R_IDENTITY')
    cells=np.zeros((np.prod(shape),13));direct=[]
    gas=np.asarray(state['gas']);lower=np.array([g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]])
    for a in range(shape[0]):
        for j in range(shape[1]):
            lo,hi=map(float,state['support'][a,j]);i=a*shape[1]+j
            prepared=absorption_api.prepare_incident(float(state['N'][a,j]),float(state['U_eV'][a,j]),float(R[a]),lo,hi,opacity,orders=(64,128),rtol=1e-7,support_cap_ev=(50000. if hi==50000./R[a] and hi<=source.edges[j+1] else None))
            value=absorption_api.absorb(prepared,lower,0.)
            cells[i,:5]=[mu[a],R[a],g['H']+g['s']*(3*mu[a]**2-1),value['N'],value['U']]
            cells[i,7:10]=value['K0'];cells[i,10:13]=value['KE'];direct.append(value['photoheat_direct'])
    gamma=np.zeros(3)
    a_rel=float(g['a_rel']);native_volume=a_rel*a_rel*a_rel
    for row in cells:gamma+=row[7:10]/native_volume
    result['diagnostics']['gamma']=gamma.tolist()
    result['diagnostics']['output24_kernel']=_capture_kernel(result,g,cells,direct,gamma,owner='ORIGINAL_SAVED_C2_H0_OUTPUT_ONLY',native_evaluations=0)
    return result
