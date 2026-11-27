"""Bounded optical-input sampling, not a scattering or thermal-rate source.

Length R in a0, energies in Eh. Nuclear repulsion is excluded from electronic
energies and added once to V. Derivatives are of finite numerical models.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from bass_he_prolate_variational.core import ContractError, NumericalFailure, moments
from bass_he_two_state import core as cf
from . import _endpoint_scope as ep

ANCHOR_SHA='d8f7ad09e8c16b0c2445168ebe0c36a43fc9183f8ef6f2461fc37e0d053b3b42'
CONTRACT_SHA='a16033dd62a7f0d4f5dfce962b40ec199a57419c8cbdf0d9fa94e104784148af'

def _finite(x,name,lo=None):
    return ep.real(x,name,lo=lo)

def validate_path(path):
    if not isinstance(path,(tuple,list)) or len(path)!=17:
        raise ContractError('exact registered17-point R8..10 path required')
    vals=[_finite(x,'path point') for x in path]
    if vals!=[8+i/8 for i in range(17)]:
        raise ContractError('path differs from preregistration')
    return vals

def load_contract(path):
    p=Path(path)
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=CONTRACT_SHA:
        raise ContractError('contract identity mismatch; amendment required')
    v=json.loads(p.read_text());validate_path(v['path']);return v

def _state(row):
    g=np.array(row['radial_g'],dtype=float);f=np.array(row['angular_f'],dtype=float)
    g.setflags(write=False);f.setflags(write=False)
    return cf.State(row['R_a0'],row['label'],row['center'],row['p'],row['Aprime'],row['energy_Eh'],row['order'],g,f,
                    tuple(row['CF_residual']),*row['nodes_observed'],row['root_evaluations'],row['root_message'],cf.DERIVED)

def load_R8(path):
    p=Path(path)
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=ANCHOR_SHA:
        raise ContractError('fixed approved R8 anchor bytes required')
    obj=json.loads(p.read_text());ss=tuple(_state(x) for x in obj['states'])
    if len(ss)!=2 or any(s.R!=8. for s in ss) or [s.label for s in ss]!=['1s_sigma','2p_sigma']:
        raise ContractError('invalid R8 two-state anchor')
    for s in ss:
        F=cf.cf_residual(s.R,s.p,s.aprime,s.order,center=s.center,convention=cf.DERIVED)
        if max(abs(F))>1e-9:raise NumericalFailure('anchor algebraic check failed')
    return ss,np.asarray(obj['continuous_real_phase'],dtype=int)

def energy_slope(state):
    F,J=ep.cf_jacobian(state.R,state.p,state.aprime,state.order,center=state.center)
    cond=float(np.linalg.cond(J[:,1:]))
    if max(abs(F))>1e-9 or not math.isfinite(cond) or cond>1e10:
        raise NumericalFailure('finite-CF derivative conditions failed')
    dp,dap=np.linalg.solve(J[:,1:],-J[:,0])
    slope=math.fsum([4*state.p**2/state.R**3,-4*state.p*dp/state.R**2])
    return {'dE_dR_Eh_per_a0':slope,'dp_dR':float(dp),'dAprime_dR':float(dap),
            'jacobian_condition':cond,'full_H_derivative_certified':False}

def derivative_matrices(R,nr,na,beta):
    R=ep.real(R,'R',.5,10.);m=moments(nr,na,beta);a=R/2
    T=np.kron(m['Kr'],m['A0'])+np.kron(m['R0'],m['Ka'])
    U=3*np.kron(m['R1'],m['A0'])+np.kron(m['R0'],m['A1'])
    M=np.kron(m['R2'],m['A0'])-np.kron(m['R0'],m['A2'])
    return T/4-a*U,1.5*a*a*M

def solve_R10(R,nr,na,beta):
    result=ep.solve_endpoint(R,nr,na,beta)
    Hp,Sp=derivative_matrices(R,nr,na,beta)
    result['dE_dR_fixed_beta_Eh_per_a0']=np.array([
        float(c@(Hp-e*Sp)@c) for e,c in zip(result['energies_Eh'],result['coefficients'].T)])
    result['dV_dR_Eh_per_a0']=float(result['dE_dR_fixed_beta_Eh_per_a0'][1]-2/R**2)
    result['derivative_uses_CF']=False
    return result

def hermite(a,b,ya,yb,da,db,x):
    a,b,x=(_finite(z,n) for z,n in ((a,'a'),(b,'b'),(x,'x')))
    y0,y1,d0,d1=(_finite(z,n) for z,n in ((ya,'ya'),(yb,'yb'),(da,'da'),(db,'db')))
    if not a<b or not a<=x<=b:raise ContractError('ordered nodes and no extrapolation required')
    t=(x-a)/(b-a);h=b-a
    val=math.fsum([(2*t**3-3*t*t+1)*y0,(-2*t**3+3*t*t)*y1,
                   h*(t**3-2*t*t+t)*d0,h*(t**3-t*t)*d1])
    if not math.isfinite(val):raise NumericalFailure('Hermite arithmetic range')
    return val

def sampling_bounds(h,*,M4,M2,node_error,slope_error):
    h=_finite(h,'h',0.);M4=_finite(M4,'M4',0.);M2=_finite(M2,'M2',0.)
    e=_finite(node_error,'node error',0.);d=_finite(slope_error,'slope error',0.)
    if h==0:raise ContractError('positive cell width required')
    vh=M4*h**4/384+e+h*d/4;lf=M2*h*h/8+e
    if not all(math.isfinite(x) for x in (vh,lf)):raise NumericalFailure('bound arithmetic range')
    return {'hermite_absolute':vh,'log_linear_absolute':lf,
            'meaning':'conditional on supplied uniform derivative and nodal error bounds',
            'bounds_proved_from_sampled_differences':False,'physical_accuracy_certified':False}

def polarization(R):
    R=_finite(R,'R',1e-4)
    return {'R_a0':R,'leading_C4':9.,'second_order_C6':30.,'V_C4_Eh':-9/R**4,
            'V_C4_C6_Eh':math.fsum([-9/R**4,-30/R**6]),'remainder_bound':None,
            'origin':'formal H1s nondegenerate multipole perturbation; not fitted',
            'may_replace_full_potential_at_R':False}

def optical_record(states,phases):
    pair=cf.pair_observables(*states,radial_points=96,angular_points=96)
    dip=pair['dipole_z_length_a0']*int(np.prod(phases));R=states[0].R
    slopes=[energy_slope(s) for s in states]
    out=ep.optical_diagnostic(R,states[0].energy_Eh,states[1].energy_Eh,dip)
    out['dV_dR_Eh_per_a0']=math.fsum([slopes[1]['dE_dR_Eh_per_a0'],-2/R**2])
    out['finite_CF_energy_slopes']=slopes;out['pair']=pair
    return out

def sampling_diagnostics(rows,config):
    pts={r['R_a0']:r for r in rows}
    if sorted(pts)!=[8+i/8 for i in range(17)]:raise ContractError('complete declared optical samples required')
    results=[]
    for width in config['mesh_widths']:
        for i in range(round(2/width)):
            a=8+i*width;b=a+width;m=(a+b)/2;x,y,z=(pts[t] for t in (a,b,m))
            lin=(x['V_entrance_Eh']+y['V_entrance_Eh'])/2
            cub=hermite(a,b,x['V_entrance_Eh'],y['V_entrance_Eh'],x['dV_dR_Eh_per_a0'],y['dV_dR_Eh_per_a0'],m)
            logs=[math.log(q['A_ta_div_alpha3']) for q in (x,y,z)];dlog=(logs[0]+logs[1])/2-logs[2]
            tol=config['V_atol_Eh']+config['V_rtol']*abs(z['V_entrance_Eh'])
            results.append({'a':a,'b':b,'midpoint':m,'linear_V_abs_defect_Eh':abs(lin-z['V_entrance_Eh']),
              'Hermite_V_abs_defect_Eh':abs(cub-z['V_entrance_Eh']),
              'log_rate_defect':dlog,'rate_relative_defect':abs(math.expm1(dlog)),
              'V_tolerance_Eh':tol,'Hermite_midpoint_accept':abs(cub-z['V_entrance_Eh'])<=tol,
              'log_rate_midpoint_accept':abs(dlog)<=config['log_rate_tolerance'],
              'uniform_interpolation_error_bound':None,'physical_accuracy_certified':False})
    return results

def plain(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    return x
