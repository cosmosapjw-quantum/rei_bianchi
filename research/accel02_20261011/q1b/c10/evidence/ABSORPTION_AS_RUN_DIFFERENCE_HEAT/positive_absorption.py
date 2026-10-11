"""Positive backward-Euler absorption functional for C10 finite source entry.

Units: N photons/reference cm^3, U eV/reference cm^3, E=R*q eV,
sigma cm^2, lower_cm3 proper absorber densities, h_s seconds. K0 and KE
are c*integral(sigma*Fplus) and c*integral(E*sigma*Fplus). Both species
counters and surviving moments use the same positive fitted measure.

This is a bounded local split-step operator, not a gas solver or admission
of a cosmological history. No Jacobian of the empty photon state is taken.
"""
from dataclasses import dataclass
import math
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from reconstruction import reconstruct,TraceRequired,QuadratureNotConverged
from opacity_native import C_CM_S,THRESHOLDS_EV,CHEMICAL_CHI_EV,NativeOpacity

MOMENT_FIT_RTOL=1e-12
PAIRING_RTOL=1e-12
RESPONSE_COMPONENTS=['N','U','K0_HI','K0_HeI','K0_HeII','KE_HI','KE_HeI','KE_HeII',
                     'photoheat_HI','photoheat_HeI','photoheat_HeII']


@dataclass(frozen=True)
class IncidentMeasure:
    q:np.ndarray
    P:np.ndarray
    sigma:np.ndarray
    diagnostics:dict


@dataclass(frozen=True)
class PreparedIncident:
    q:np.ndarray
    P:np.ndarray
    sigma:np.ndarray
    R:float
    N:float
    U:float
    coarse:IncidentMeasure
    rtol:float
    diagnostics:dict


def _freeze(a):
    a=np.asarray(a,dtype=float)
    a.setflags(write=False)
    return a


def _sum(a):
    return math.fsum(np.asarray(a,dtype=float).ravel())


def _components(N,U,K0,KE):
    K0,KE=np.asarray(K0),np.asarray(KE)
    # Native gas heating uses the small difference KE - chi*K0. Checking
    # only KE and K0 permits cancellation to amplify their accepted errors.
    # Keep the pinned chemical chi (distinct from sigma thresholds), without
    # a clamp or a larger scale borrowed from either constituent rate.
    heat=KE-CHEMICAL_CHI_EV*K0
    return np.concatenate(([N,U],K0,KE,heat))


def _compare(coarse,fine,rtol,label):
    coarse,fine=np.asarray(coarse),np.asarray(fine)
    if not np.all(np.isfinite(coarse)) or not np.all(np.isfinite(fine)):
        raise ArithmeticError(label+': nonfinite response')
    delta=np.abs(coarse-fine)
    scales=np.abs(fine)
    if np.any((scales==0)&(delta!=0)):
        raise QuadratureNotConverged(label+': nonzero difference against exact zero')
    errors=np.divide(delta,scales,out=np.zeros_like(delta),where=scales>0)
    if np.any(errors>rtol):
        raise QuadratureNotConverged(f'{label}: per-component errors={errors.tolist()}, rtol={rtol}')
    return errors


def _kernels(q,P,sigma,R):
    K0=np.array([C_CM_S*_sum(sigma[:,k]*P) for k in range(3)])
    KE=np.array([C_CM_S*_sum((R*q)*sigma[:,k]*P) for k in range(3)])
    if not np.all(np.isfinite(K0)) or not np.all(np.isfinite(KE)):
        raise ArithmeticError('ABSORPTION_RATE_NONFINITE')
    return K0,KE


def _measure(cell,opacity,order,splits):
    nodes,weights=leggauss(order)
    edges=[0.]+[cell.cdf(q) for q in splits]+[1.]
    all_x,all_w=[],[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        if hi==lo:continue
        v=lo+(hi-lo)*(nodes+1.)/2.
        all_x.append(cell.quantile_log(v))
        all_w.append((hi-lo)*weights/2.)
    x,w=np.concatenate(all_x),np.concatenate(all_w)
    q=cell.a+cell.a*np.expm1(x)
    xi=(q-cell.a)/(cell.b-cell.a)
    target=(cell.mean_q-cell.a)/(cell.b-cell.a)
    if not float(np.min(xi))<target<float(np.max(xi)):
        raise QuadratureNotConverged('MOMENT_TARGET_OUTSIDE_STRICT_NODE_CONVEX_HULL')
    logw=np.log(w)
    def probabilities(eta):
        terms=logw+eta*xi
        terms=np.exp(terms-float(np.max(terms)))
        return terms/_sum(terms)
    def residual(eta):
        return _sum(probabilities(eta)*xi)-target
    lo,hi=-1.,1.
    for _ in range(80):
        if residual(lo)<=0<=residual(hi):break
        lo*=2.;hi*=2.
    else:raise QuadratureNotConverged('MOMENT_REWEIGHTING_NOT_BRACKETED')
    eta=brentq(residual,lo,hi,xtol=2e-14,rtol=1e-14,maxiter=160)
    prob=probabilities(eta)
    P=cell.N*prob
    if np.any(P<=0) or np.any(~np.isfinite(P)):
        raise QuadratureNotConverged('POSITIVE_MEASURE_UNDERFLOW_OR_NONFINITE')
    number_residual=(_sum(P)-cell.N)/cell.N
    energy_residual=(_sum(q*P)*cell.R-cell.U)/cell.U
    relative_mean_residual=(_sum(prob*xi)-target)/min(target,1.-target)
    if max(abs(number_residual),abs(energy_residual),abs(relative_mean_residual))>MOMENT_FIT_RTOL:
        raise QuadratureNotConverged('MOMENT_EXACT_REWEIGHTING_NOT_RESOLVED')
    energy=cell.R*q
    if np.any(q<=cell.a) or np.any(q>=cell.b):
        raise TraceRequired('QUADRATURE_ROUNDED_TO_SUPPORT_ENDPOINT_NO_TRACE')
    if isinstance(opacity,NativeOpacity) and np.any(energy[:,None]==THRESHOLDS_EV[None,:]):
        raise TraceRequired('NATIVE_QUADRATURE_THRESHOLD_EQUALITY_NO_TRACE')
    callback=opacity.sigma if hasattr(opacity,'sigma') else opacity
    sigma=np.asarray(callback(energy),dtype=float)
    if sigma.shape!=(len(q),3) or np.any(~np.isfinite(sigma)) or np.any(sigma<0):
        raise ValueError('ABSORPTION_SIGMA_SHAPE_NONNEGATIVE_FINITE_DOMAIN')
    return IncidentMeasure(_freeze(q),_freeze(P),_freeze(sigma),{
        'order':order,'node_count':len(q),'eta':float(eta),
        'number_fit_relative_residual':number_residual,
        'energy_fit_relative_residual':energy_residual,
        'mean_fit_cell_relative_residual':relative_mean_residual,
        'moment_fit_rtol':MOMENT_FIT_RTOL,
        'minimum_probability':float(np.min(prob))})


def prepare_incident(N,U,R,a,b,opacity,orders=(64,128),rtol=1e-7):
    """Freeze a moment-fitted incident distribution for a four-gas solve.

    Endpoints require a distinct, unimplemented certified native trace.
    The existing arbitrary-q coordinate admission indicator is unchanged.
    Coarse/fine comparisons are diagnostics, not rigorous error bounds.
    """
    if not math.isfinite(rtol) or rtol<=0:raise ValueError('Positive finite rtol required')
    if len(orders)!=2 or any(type(n) is not int or n<2 for n in orders) or orders[0]>=orders[1]:
        raise ValueError('Two increasing integer quadrature orders required')
    cell=reconstruct(N,U,R,a,b)
    if cell.status in ('EMPTY','ZERO_WIDTH_EMPTY'):
        empty=IncidentMeasure(_freeze([]),_freeze([]),_freeze(np.zeros((0,3))),{'status':'EMPTY_EXACT_ZERO'})
        return PreparedIncident(empty.q,empty.P,empty.sigma,cell.R,0.,0.,empty,rtol,
            {'status':'EMPTY_EXACT_ZERO','orders':list(orders),'native_calls':0})
    if cell.status!='INTERIOR':
        raise TraceRequired('ABSORPTION_ENDPOINT_NATIVE_TRACE_NOT_IMPLEMENTED')
    indicator=32*math.ulp(cell.b)/min(cell.mean_q-cell.a,cell.b-cell.mean_q)
    if indicator>rtol:
        raise QuadratureNotConverged(f'FLOAT_Q_COORDINATE_UNRESOLVED: indicator={indicator}, rtol={rtol}')
    if isinstance(opacity,NativeOpacity) and cell.R*cell.b>50000.:
        raise ValueError('Q1B_NATIVE_OCCUPIED_SUPPORT_ABOVE_PINNED_DOMAIN')
    splits=[float(E/cell.R) for E in THRESHOLDS_EV if cell.a<E/cell.R<cell.b]
    coarse=_measure(cell,opacity,orders[0],splits)
    fine=_measure(cell,opacity,orders[1],splits)
    cK0,cKE=_kernels(coarse.q,coarse.P,coarse.sigma,cell.R)
    fK0,fKE=_kernels(fine.q,fine.P,fine.sigma,cell.R)
    errors=_compare(_components(_sum(coarse.P),cell.R*_sum(coarse.q*coarse.P),cK0,cKE),
        _components(_sum(fine.P),cell.R*_sum(fine.q*fine.P),fK0,fKE),rtol,'INCIDENT_ORDER_PAIR')
    return PreparedIncident(fine.q,fine.P,fine.sigma,cell.R,cell.N,cell.U,coarse,rtol,{
        'status':'INTERIOR_POSITIVE_MOMENT_FITTED','orders':list(orders),
        'float_q_coordinate_indicator':indicator,'threshold_splits_q':splits,
        'coarse':coarse.diagnostics,'fine':fine.diagnostics,
        'order_pair_component_names':RESPONSE_COMPONENTS.copy(),
        'order_pair_component_errors':errors.tolist(),'order_pair_max_error':float(np.max(errors)),
        'claim':'LOCAL_INCIDENT_MEASURE_ONLY_NOT_HISTORY_ADMISSION'})


def _attenuate(q,P,sigma,R,lower,h):
    if not len(P):
        return {'N':0.,'U':0.,'K0':np.zeros(3),'KE':np.zeros(3),
            'number_absorbed_species':np.zeros(3),'energy_absorbed_species':np.zeros(3),
            'pointwise_pairing_relative_max':0.}
    rates=(C_CM_S*sigma)*lower[None,:]
    total=np.sum(rates,axis=1)
    if np.any(~np.isfinite(total)) or np.any(total<0):
        raise ArithmeticError('ABSORPTION_RATE_ARITHMETIC_UNRESOLVED')
    if h==0:
        survived=P.copy();events=np.zeros_like(sigma)
    else:
        # inv(h) normalization avoids h*kappa overflow. Scale each denominator
        # before adding; loss counters never subtract nearly equal moments.
        invh=1./h
        if not math.isfinite(invh) or invh<=0:
            raise ArithmeticError('ABSORPTION_TIME_RECIPROCAL_UNRESOLVED')
        scale=np.maximum(invh,total)
        denominator=invh/scale+total/scale
        survived=P*((invh/scale)/denominator)
        events=P[:,None]*((rates/scale[:,None])/denominator[:,None])
    if np.any(survived<=0) or np.any(~np.isfinite(survived)) or np.any(~np.isfinite(events)):
        raise ArithmeticError('POSITIVE_SURVIVAL_UNDERFLOW_OR_NONFINITE')
    pointwise=float(np.max(np.abs(survived+np.sum(events,axis=1)-P)/P))
    if pointwise>PAIRING_RTOL:raise ArithmeticError('ABSORPTION_POINTWISE_PAIRING_FAILURE')
    K0,KE=_kernels(q,survived,sigma,R)
    return {'N':_sum(survived),'U':R*_sum(q*survived),'K0':K0,'KE':KE,
        'number_absorbed_species':np.array([_sum(events[:,k]) for k in range(3)]),
        'energy_absorbed_species':np.array([_sum(R*q*events[:,k]) for k in range(3)]),
        'pointwise_pairing_relative_max':pointwise}


def absorb(prepared,lower_cm3,h_s):
    """Return nonnegative endpoint moments and paired native gas inputs."""
    lower=np.asarray(lower_cm3,dtype=float)
    h=float(h_s)
    if lower.shape!=(3,) or np.any(~np.isfinite(lower)) or np.any(lower<0):
        raise ValueError('Three finite nonnegative absorber densities required')
    if not math.isfinite(h) or h<0:raise ValueError('Finite nonnegative step required')
    c=prepared.coarse
    coarse=_attenuate(c.q,c.P,c.sigma,prepared.R,lower,h)
    fine=_attenuate(prepared.q,prepared.P,prepared.sigma,prepared.R,lower,h)
    errors=_compare(_components(coarse['N'],coarse['U'],coarse['K0'],coarse['KE']),
        _components(fine['N'],fine['U'],fine['K0'],fine['KE']),prepared.rtol,'ATTENUATED_ORDER_PAIR')
    nres=fine['N']+_sum(fine['number_absorbed_species'])-prepared.N
    ures=fine['U']+_sum(fine['energy_absorbed_species'])-prepared.U
    nrel=nres/prepared.N if prepared.N else nres
    urel=ures/prepared.U if prepared.U else ures
    if max(abs(nrel),abs(urel))>PAIRING_RTOL:
        raise ArithmeticError('ABSORPTION_STORED_MOMENT_PAIRING_FAILURE')
    # Independently check the counters against the returned native inputs.
    # Extended-range products avoid manufacturing infinity in stiff cases.
    links=[]
    for key,ratekey in (('number_absorbed_species','K0'),('energy_absorbed_species','KE')):
        actual=np.asarray(fine[key],dtype=np.longdouble)
        expected=np.longdouble(h)*lower.astype(np.longdouble)*np.asarray(fine[ratekey],dtype=np.longdouble)
        delta=np.abs(actual-expected)
        scale=np.maximum(np.abs(actual),np.abs(expected))
        err=np.divide(delta,scale,out=np.zeros_like(delta),where=scale>0)
        if np.any(~np.isfinite(err)) or np.any(err>PAIRING_RTOL):
            raise ArithmeticError('ABSORPTION_NATIVE_COUNTER_LINK_FAILURE')
        links.extend(np.asarray(err,dtype=float).tolist())
    fine['diagnostics']={'status':'POSITIVE_IMPLICIT_ABSORPTION_LOCAL_CHECKED',
        'order_pair_component_names':RESPONSE_COMPONENTS.copy(),
        'order_pair_component_errors':errors.tolist(),'order_pair_max_error':float(np.max(errors)),
        'number_pairing_residual':nres,'energy_pairing_residual_eV':ures,
        'number_pairing_relative_residual':nrel,'energy_pairing_relative_residual':urel,
        'native_counter_link_component_errors':links,
        'pairing_rtol':PAIRING_RTOL,'rtol':prepared.rtol,
        'claim':'LOCAL_ABSORPTION_FUNCTIONAL_NOT_GAS_OR_HISTORY_ADMISSION'}
    return fine
