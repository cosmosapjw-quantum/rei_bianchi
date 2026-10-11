"""Native-only thin smooth-support value certificate; C10 operator unchanged.

For old generic-q admission use the frozen code verbatim. Only when that
indicator rejects, a positive-measure Taylor bound may replace that indicator
for the pinned native fit (no Jacobians). All original fitting, positivity,
source, opacity, heat, pairing and absorbed-counter gates remain in force.
The extra bound is SUBTRACTED from the original 1e-7 response budget.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,math,sys
import numpy as np
HERE=Path(__file__).resolve().parent
Q1B=HERE.parent.parent;C10=Q1B/'c10';REPO=Q1B.parents[2]
sys.path.insert(0,str(Q1B));sys.path.insert(0,str(C10))
import positive_absorption as old
from reconstruction import reconstruct,TraceRequired,QuadratureNotConverged
from opacity_native import NativeOpacity,EXPECTED_BINARY_SHA256,THRESHOLDS_EV,CHEMICAL_CHI_EV
from endpoint_trace import SOURCE_PINS

# Exact imported attenuation, including own-scale direct/ABI heat and pairing.
absorb=old.absorb


def _support(cell):
    lo=F(cell.R)*F(cell.a);hi=F(cell.R)*F(cell.b);cap=F(50000.)
    provenance='EXACT_REPRESENTED_SUPPORT_INSIDE_PROVIDER_BAND'
    endpoint_excess=F(0)
    if hi>cap:
        if cell.b!=50000./cell.R or cell.R*cell.b!=50000.:
            raise TraceRequired('DECLARED_SOURCE_CAP_PROVENANCE_REQUIRED')
        # b records the declared sourcecap quotient. It is not modified.
        # Actual nodes and target mean must lie in the exact physical domain.
        endpoint_excess=hi-cap;hi=cap
        provenance='DECLARED_50000_EV_CAP_QUOTIENT_METADATA'
    if not 0<lo<hi<=cap:raise TraceRequired('NATIVE_PHYSICAL_SUPPORT_DOMAIN')
    target=F(cell.U)/F(cell.N)
    if not lo<target<hi:raise TraceRequired('AUTHORITATIVE_MEAN_OUTSIDE_PHYSICAL_INTERIOR')
    branches=[]
    for threshold in THRESHOLDS_EV:
        t=F(float(threshold))
        if hi<t:branches.append('EXACT_ZERO')
        elif lo>t:branches.append('SMOOTH_ACTIVE')
        else:raise TraceRequired('NATIVE_SAME_BRANCH_SUPPORT_REQUIRED')
    return lo,hi,target,branches,provenance,endpoint_excess


def _certificate(cell,measures,indicator,rtol):
    lo,hi,target,branches,provenance,excess=_support(cell)
    width=float((hi-lo)/lo)
    active=[k for k,b in enumerate(branches) if b=='SMOOTH_ACTIVE']
    # D=E*d/dE. Source-derived active fit: |D log sigma|<=8.8,
    # |D^2 log sigma|<=32. For d=1+h*c*sum(n*sigma), log d is
    # a logsumexp including constant1: |D log d|<=8.8 and
    # |D^2 log d|<=32+8.8^2, independent of h and nonnegative n.
    # This common envelope covers survivor1/d,E/d, K0=sigma/d,
    # KE=E*sigma/d, heat=(E-chi)*sigma/d, and species counters.
    if active:
        chi=max(F(float(CHEMICAL_CHI_EV[k])) for k in active)
        L=17.6+float(lo/(lo-chi))
        M=64.+8.8**2+float(lo*chi/(lo-chi)**2)
    else:L,M=1.,0.
    K=M+L*L+L
    span=math.log1p(width)
    ratio=math.exp(L*span)
    details=[];emax=F(0)
    for measure in measures:
        pairs=[(F(float(q)),F(float(p))) for q,p in zip(measure.q,measure.P)]
        mass=sum((p for _,p in pairs),F(0))
        if mass<=0:raise QuadratureNotConverged('CERTIFICATE_POSITIVE_MASS_REQUIRED')
        actual=[];delta_round=F(0)
        for q,p in pairs:
            exact=F(cell.R)*q;native=F(float(cell.R*float(q)))
            if p<=0 or not lo<exact<hi or not lo<native<hi:
                raise TraceRequired('EXACT_NATIVE_NODE_OUTSIDE_PHYSICAL_INTERIOR')
            for k,threshold in enumerate(THRESHOLDS_EV):
                threshold=F(float(threshold))
                if (branches[k]=='EXACT_ZERO' and not(exact<threshold and native<threshold)) or \
                   (branches[k]=='SMOOTH_ACTIVE' and not(exact>threshold and native>threshold)):
                    raise TraceRequired('EXACT_NATIVE_NODE_THRESHOLD_SIDE_MISMATCH')
            actual.append((exact,p));emax=max(emax,exact,native)
            delta_round=max(delta_round,abs(native-exact)/min(native,exact))
        mean=sum((e*p for e,p in actual),F(0))/mass
        nerr=float(abs(mass-F(cell.N))/F(cell.N))
        meanerr=float(abs(mean-target)/lo)
        # Comparing normalized positive measures with same prescribed moments:
        # constant cancels; linear term sees exact measured mean defect;
        # both Taylor remainders bounded by K*(width/lo)^2.
        shape=ratio*(nerr+(1+nerr)*(L*meanerr+K*width*width))
        rounded=(1+nerr)*ratio*math.expm1(L*math.log1p(float(delta_round)))
        # Conservative arithmetic slack for evaluating this analytic envelope.
        bound=(shape+rounded)*(1.+1e-12)+1e-30
        details.append({'order':measure.diagnostics['order'],'exact_mass_relative_error':nerr,
            'exact_mean_error_over_lower_energy':meanerr,'max_native_energy_rounding_relative':float(delta_round),
            'positive_measure_shape_bound':shape,'native_energy_coordinate_bound':rounded,
            'combined_bound':bound})
    total=2.*max(d['combined_bound'] for d in details)
    if not math.isfinite(total) or total>rtol/16.:
        raise QuadratureNotConverged(f'NATIVE_COORDINATE_CERTIFICATE_BUDGET: {total}, rtol={rtol}')
    return {'schema':'rei.c11.native_coordinate_certificate.v1',
        'scope':'VALUE_ONLY_POSITIVE_MEASURES_NO_ENDPOINT_OR_JACOBIAN',
        'old_generic_indicator':indicator,'sigma_log_slope_bound':8.8,'sigma_second_log_derivative_bound':32.,
        'attenuated_common_log_slope_bound':L,'attenuated_common_second_log_derivative_bound':M,
        'attenuated_common_relative_curvature_bound':K,'relative_support_width':width,
        'physical_energy_interval_eV':[float(lo),float(hi)],'support_cap_provenance':provenance,
        'rounded_endpoint_product_excess_eV':float(excess),'exact_node_energy_max_eV':float(emax),
        'threshold_branches':branches,'orders':details,'combined_coordinate_bound':total,
        'original_response_rtol':rtol,'remaining_response_rtol':rtol-total,
        'native_formula_evaluation_error_bound':'not newly certified; pinned provider unchanged',
        'state_or_node_modified':False,'gas_density_and_step_scope':'all finite nonnegative absorber densities and h, with old arithmetic/domain guards',
        'scientific_history_admission':False}


def prepare_incident(N,U,R,a,b,opacity,orders=(64,128),rtol=1e-7):
    cell=reconstruct(N,U,R,a,b)
    if cell.status!='INTERIOR':return old.prepare_incident(N,U,R,a,b,opacity,orders=orders,rtol=rtol)
    indicator=32*math.ulp(cell.b)/min(cell.mean_q-cell.a,cell.b-cell.mean_q)
    if indicator<=rtol or not isinstance(opacity,NativeOpacity):
        return old.prepare_incident(N,U,R,a,b,opacity,orders=orders,rtol=rtol)
    if opacity.binary_sha256!=EXPECTED_BINARY_SHA256:
        raise ValueError('NATIVE_CERTIFICATE_BINARY_IDENTITY')
    for name,expected in SOURCE_PINS.items():
        if hashlib.sha256((REPO/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('NATIVE_CERTIFICATE_SOURCE_IDENTITY:'+name)
    if not math.isfinite(rtol) or rtol<=0:raise ValueError('Positive finite rtol required')
    if len(orders)!=2 or any(type(n) is not int or n<2 for n in orders) or orders[0]>=orders[1]:
        raise ValueError('Two increasing integer quadrature orders required')
    _support(cell) # rejects threshold crossings/uncertified cap before native calls
    coarse=old._measure(cell,opacity,orders[0],[])
    fine=old._measure(cell,opacity,orders[1],[])
    cert=_certificate(cell,[coarse,fine],indicator,rtol)
    remaining=cert['remaining_response_rtol']
    cK0,cKE=old._kernels(coarse.q,coarse.P,coarse.sigma,cell.R)
    fK0,fKE=old._kernels(fine.q,fine.P,fine.sigma,cell.R)
    ch=old._direct_heat(coarse.q,coarse.P,coarse.sigma,cell.R)
    fh=old._direct_heat(fine.q,fine.P,fine.sigma,cell.R)
    ccons=old._heat_consistency(cK0,cKE,ch,remaining,'INCIDENT_COARSE_HEAT_ABI_DIRECT')
    fcons=old._heat_consistency(fK0,fKE,fh,remaining,'INCIDENT_FINE_HEAT_ABI_DIRECT')
    errors=old._compare(old._components(old._sum(coarse.P),cell.R*old._sum(coarse.q*coarse.P),cK0,cKE,ch),
        old._components(old._sum(fine.P),cell.R*old._sum(fine.q*fine.P),fK0,fKE,fh),remaining,'INCIDENT_ORDER_PAIR')
    return old.PreparedIncident(fine.q,fine.P,fine.sigma,cell.R,cell.N,cell.U,coarse,remaining,{
        'status':'INTERIOR_POSITIVE_NATIVE_VALUE_CERTIFIED','orders':list(orders),
        'float_q_coordinate_indicator':indicator,'threshold_splits_q':[],
        'coarse':coarse.diagnostics,'fine':fine.diagnostics,
        'order_pair_component_names':old.RESPONSE_COMPONENTS.copy(),
        'heat_direct_abi_component_errors':{'coarse':ccons.tolist(),'fine':fcons.tolist()},
        'order_pair_component_errors':errors.tolist(),'order_pair_max_error':float(np.max(errors)),
        'native_coordinate_certificate':cert,
        'claim':'LOCAL_NATIVE_VALUE_CERTIFICATE_ONLY_NOT_HISTORY_ADMISSION'})
