"""Bounded composite-log-q positive quadrature for incident order refusal.

The original native-conditioned 64/128 path is attempted first. Only its actual
native INCIDENT_ORDER_PAIR refusal admits this alternative coordinate rule.
Threshold cuts, power-law closure, strict state/support domains, global positive
moment reweighting, fit/pair/response tolerances and native attenuation stay fixed.
No frozen module is patched. A fixed MAX_PANELS bounds work before SIGMA calls;
underflow, unresolved nodes/moment fits, or failed response comparisons stop.
"""
from __future__ import annotations
from pathlib import Path
import copy,math,sys
import numpy as np
from numpy.polynomial.legendre import leggauss
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2]
for path in (Q1B,Q1B/'c10',Q1B/'c11/endpoint'):sys.path.insert(0,str(path))
import native_coordinate_absorption as _base
import positive_absorption as old
from reconstruction import reconstruct,TraceRequired,QuadratureNotConverged
from opacity_native import NativeOpacity,THRESHOLDS_EV,CHEMICAL_CHI_EV

MAX_PANELS=128
MAX_EXPONENT_SPAN=4.
absorb=old.absorb
_REFINEMENTS=[]


def pop_refinement_records():
    """Single-worker per-map receipts. Driver drains in finally, even failure."""
    result=copy.deepcopy(_REFINEMENTS);_REFINEMENTS.clear();return result


def log_panels(cell,splits):
    """Tile log(q/a) exactly at thresholds; |p| Delta(log q) <= 4.

    This conditions exponential density variation, not an error certificate.
    Thresholds are original q=E_threshold/R values, with no physical shift.
    """
    if cell.status!='INTERIOR' or not math.isfinite(cell.p):raise ValueError('LOGQ_INTERIOR_REQUIRED')
    L=math.log1p((cell.b-cell.a)/cell.a)
    cuts=[0.,*sorted(set(math.log1p((float(q)-cell.a)/cell.a) for q in splits if cell.a<float(q)<cell.b)),L]
    panels=[]
    for lo,hi in zip(cuts[:-1],cuts[1:]):
        count=max(1,math.ceil(abs(cell.p)*(hi-lo)/MAX_EXPONENT_SPAN))
        if count+len(panels)>MAX_PANELS:raise QuadratureNotConverged('LOGQ_PANEL_CAP_EXCEEDED')
        points=[lo]+[lo+(hi-lo)*i/count for i in range(1,count)]+[hi]
        if any(not a<b for a,b in zip(points[:-1],points[1:])):raise QuadratureNotConverged('LOGQ_PANEL_CLOCK_UNRESOLVED')
        # Rare ceil-boundary roundoff is handled by one extra panel, never by
        # widening the declared span or modifying a physical endpoint.
        if any(abs(cell.p)*(b-a)>MAX_EXPONENT_SPAN for a,b in zip(points[:-1],points[1:])):
            count+=1
            if count+len(panels)>MAX_PANELS:raise QuadratureNotConverged('LOGQ_PANEL_CAP_EXCEEDED')
            points=[lo]+[lo+(hi-lo)*i/count for i in range(1,count)]+[hi]
        panels.extend(zip(points[:-1],points[1:]))
    maximum=max(abs(cell.p)*(b-a) for a,b in panels)
    if maximum>MAX_EXPONENT_SPAN:raise QuadratureNotConverged('LOGQ_PANEL_SPAN_UNRESOLVED')
    return panels,dict(coordinate='log(q/a)',panels=[list(p) for p in panels],panel_count=len(panels),max_panels=MAX_PANELS,max_exponent_span=MAX_EXPONENT_SPAN,actual_max_exponent_span=maximum,threshold_splits_q=list(map(float,splits)),rigorous_error_bound=False)


def measure_logq(cell,opacity,order,splits):
    """Positive Gauss density weights with unchanged global N/U moment fit.

    Existing old._measure's moment-reweighting/root solve and domain gates are
    retained; only node coordinate/base log weights differ. Log normalization
    prevents overflow. A positive weight lost to underflow remains a failure.
    """
    panels,plan=log_panels(cell,splits);nodes,weights=leggauss(order)
    all_x=[];all_logw=[]
    for lo,hi in panels:
        half=.5*(hi-lo);x=lo+half*(nodes+1.)
        if np.any(x<=lo) or np.any(x>=hi):raise TraceRequired('LOGQ_NODE_ROUNDED_TO_PANEL_ENDPOINT')
        all_x.append(x);all_logw.append(np.log(half*weights)+cell.p*x)
    x=np.concatenate(all_x);logw=np.concatenate(all_logw)
    if not np.isfinite(logw).all():raise QuadratureNotConverged('LOGQ_BASE_WEIGHT_NONFINITE')
    q=cell.a+cell.a*np.expm1(x)
    xi=(q-cell.a)/(cell.b-cell.a);target=(cell.mean_q-cell.a)/(cell.b-cell.a)
    if not float(np.min(xi))<target<float(np.max(xi)):
        raise QuadratureNotConverged('MOMENT_TARGET_OUTSIDE_STRICT_NODE_CONVEX_HULL')
    def probabilities(eta):
        terms=logw+eta*xi
        terms=np.exp(terms-float(np.max(terms)))
        return terms/old._sum(terms)
    def residual(eta):return old._sum(probabilities(eta)*xi)-target
    lo,hi=-1.,1.
    for _ in range(80):
        if residual(lo)<=0<=residual(hi):break
        lo*=2.;hi*=2.
    else:raise QuadratureNotConverged('MOMENT_REWEIGHTING_NOT_BRACKETED')
    eta=old.brentq(residual,lo,hi,xtol=2e-14,rtol=1e-14,maxiter=160)
    prob=probabilities(eta);P=cell.N*prob
    if np.any(P<=0) or np.any(~np.isfinite(P)):
        raise QuadratureNotConverged('POSITIVE_MEASURE_UNDERFLOW_OR_NONFINITE')
    number_residual=(old._sum(P)-cell.N)/cell.N
    energy_residual=(old._sum(q*P)*cell.R-cell.U)/cell.U
    relative_mean_residual=(old._sum(prob*xi)-target)/min(target,1.-target)
    if max(abs(number_residual),abs(energy_residual),abs(relative_mean_residual))>old.MOMENT_FIT_RTOL:
        raise QuadratureNotConverged('MOMENT_EXACT_REWEIGHTING_NOT_RESOLVED')
    energy=cell.R*q
    if np.any(q<=cell.a) or np.any(q>=cell.b):raise TraceRequired('QUADRATURE_ROUNDED_TO_SUPPORT_ENDPOINT_NO_TRACE')
    if isinstance(opacity,NativeOpacity) and np.any(energy[:,None]==THRESHOLDS_EV[None,:]):
        raise TraceRequired('NATIVE_QUADRATURE_THRESHOLD_EQUALITY_NO_TRACE')
    callback=opacity.sigma if hasattr(opacity,'sigma') else opacity
    sigma=np.asarray(callback(energy),dtype=float)
    if sigma.shape!=(len(q),3) or np.any(~np.isfinite(sigma)) or np.any(sigma<0):
        raise ValueError('ABSORPTION_SIGMA_SHAPE_NONNEGATIVE_FINITE_DOMAIN')
    if isinstance(opacity,NativeOpacity) and np.any((energy[:,None]-CHEMICAL_CHI_EV)*sigma<0):
        raise ArithmeticError('NATIVE_PHOTOHEAT_NEGATIVE_NO_CLAMP')
    return old.IncidentMeasure(old._freeze(q),old._freeze(P),old._freeze(sigma),dict(order=order,node_count=len(q),eta=float(eta),number_fit_relative_residual=number_residual,energy_fit_relative_residual=energy_residual,mean_fit_cell_relative_residual=relative_mean_residual,moment_fit_rtol=old.MOMENT_FIT_RTOL,minimum_probability=float(np.min(prob)),logq_panel_plan=plan))


def _prepare_logq(N,U,R,a,b,opacity,orders,rtol):
    cell=reconstruct(N,U,R,a,b)
    if cell.status!='INTERIOR':raise TraceRequired('LOGQ_FALLBACK_INTERIOR_ONLY')
    indicator=32*math.ulp(cell.b)/min(cell.mean_q-cell.a,cell.b-cell.mean_q)
    if indicator>rtol:raise QuadratureNotConverged('LOGQ_FALLBACK_CANNOT_REPLACE_COORDINATE_CERTIFICATE')
    if cell.R*cell.b>50000.:raise ValueError('Q1B_NATIVE_OCCUPIED_SUPPORT_ABOVE_PINNED_DOMAIN')
    splits=[float(E/cell.R) for E in THRESHOLDS_EV if cell.a<E/cell.R<cell.b]
    coarse=measure_logq(cell,opacity,orders[0],splits)
    fine=measure_logq(cell,opacity,orders[1],splits)
    cK0,cKE=old._kernels(coarse.q,coarse.P,coarse.sigma,cell.R)
    fK0,fKE=old._kernels(fine.q,fine.P,fine.sigma,cell.R)
    ch=old._direct_heat(coarse.q,coarse.P,coarse.sigma,cell.R)
    fh=old._direct_heat(fine.q,fine.P,fine.sigma,cell.R)
    ccons=old._heat_consistency(cK0,cKE,ch,rtol,'LOGQ_INCIDENT_COARSE_HEAT_ABI_DIRECT')
    fcons=old._heat_consistency(fK0,fKE,fh,rtol,'LOGQ_INCIDENT_FINE_HEAT_ABI_DIRECT')
    errors=old._compare(old._components(old._sum(coarse.P),cell.R*old._sum(coarse.q*coarse.P),cK0,cKE,ch),old._components(old._sum(fine.P),cell.R*old._sum(fine.q*fine.P),fK0,fKE,fh),rtol,'LOGQ_INCIDENT_ORDER_PAIR')
    return old.PreparedIncident(fine.q,fine.P,fine.sigma,cell.R,cell.N,cell.U,coarse,rtol,dict(status='INTERIOR_POSITIVE_LOGQ_MOMENT_FITTED',coordinate='LOG_Q_COMPOSITE_POSITIVE',orders=list(orders),float_q_coordinate_indicator=indicator,threshold_splits_q=splits,coarse=coarse.diagnostics,fine=fine.diagnostics,order_pair_component_names=old.RESPONSE_COMPONENTS.copy(),heat_direct_abi_component_errors=dict(coarse=ccons.tolist(),fine=fcons.tolist()),order_pair_component_errors=errors.tolist(),order_pair_max_error=float(np.max(errors)),claim='LOCAL_LOGQ_INCIDENT_ONLY_NOT_HISTORY_ADMISSION'))


def prepare_incident(N,U,R,a,b,opacity,orders=(64,128),rtol=1e-7,*,support_cap_ev=None):
    try:
        return _base.prepare_incident(N,U,R,a,b,opacity,orders=orders,rtol=rtol,support_cap_ev=support_cap_ev)
    except QuadratureNotConverged as original:
        if not (isinstance(opacity,NativeOpacity) and tuple(orders)==(64,128) and str(original).startswith('INCIDENT_ORDER_PAIR:')):raise
        record=dict(schema='rei.c12.opacity.logq_refinement.v1',parameters=dict(N=float(N),U=float(U),R=float(R),a=float(a),b=float(b)),requested_orders=list(orders),effective_orders=list(orders),requested_rtol=float(rtol),effective_rtol=None,coordinate='LOG_Q_COMPOSITE_POSITIVE',max_panels=MAX_PANELS,max_exponent_span=MAX_EXPONENT_SPAN,support_cap_ev=support_cap_ev,original_failure=dict(type=type(original).__name__,message=str(original)),status='LOGQ_REFINEMENT_STARTED',tolerance_changed=False,closure_changed=False,threshold_shifted=False,scientific_admission=False)
        _REFINEMENTS.append(record)
        try:prepared=_prepare_logq(N,U,R,a,b,opacity,orders,rtol)
        except Exception as failure:
            record.update(status='LOGQ_REFINEMENT_FAILED_CLOSED',refined_failure=dict(type=type(failure).__name__,message=str(failure)))
            failure.add_note('C12 bounded log-q positive rule failed; original refusal preserved; no tolerance change or further retry.')
            raise
        record.update(status='REFINED_LOGQ_SAME_TOLERANCE',effective_rtol=float(prepared.rtol),incident_order_pair_max_error=float(prepared.diagnostics['order_pair_max_error']),panel_count=prepared.diagnostics['fine']['logq_panel_plan']['panel_count'],node_counts=[len(prepared.coarse.q),len(prepared.q)])
        prepared.diagnostics['quadrature_refinement']=copy.deepcopy(record)
        return prepared
