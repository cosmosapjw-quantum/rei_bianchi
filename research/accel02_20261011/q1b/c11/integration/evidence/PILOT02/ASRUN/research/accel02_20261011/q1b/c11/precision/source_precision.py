"""C11 versioned same-formula FLRW source arithmetic.

The immutable HM12 table arrays/background coefficients remain the inputs.
Only floating point algebra changes. Native/checkpoint R0/R1 retain the exact
immutable provider rays; stable analytic differences are independently exposed.
D=integral(q-cell_left)source is DIAGNOSTIC, not an authoritative state component.
Native reconstruction guards are untouched; no floors/seeds/clipping occur.
"""
from __future__ import annotations
import importlib.util
import math
from pathlib import Path
import sys
import numpy as np

_C10=Path(__file__).resolve().parents[2]/'c10'/'source_entry.py'
_spec=importlib.util.spec_from_file_location('c11_frozen_c10_source_entry',_C10)
_old=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_old)
SourceEntryError=_old.SourceEntryError
provider_event_times=_old.provider_event_times
PAIR_RTOL=_old.PAIR_RTOL
_relative=_old._relative
_sum_arrays=_old._sum_arrays
_scaled_residual=_old._scaled_residual


def log_ray(bg,t):
    if bg.r != 0.:
        raise ValueError('SOURCE_PRECISION_FLRW_ONLY')
    bg._validate_time(float(t))
    # Exact same hyperbolic background volume solution as immutable provider.
    return -math.log1p(bg._relative_volume_increment(float(t)))/3.


def ray_difference(bg,t0,t1):
    """R(t0)-R(t1), including late absolute epochs with short time separations."""
    if not (math.isfinite(t0) and math.isfinite(t1) and t1>=t0):
        raise ValueError('SOURCE_PRECISION_RAY_DIFFERENCE_TIME')
    l1=log_ray(bg,t1)
    A=1.+bg.B/(2.*bg.D*bg.v_i)
    B=bg.root_poly_i/(bg.v_i*math.sqrt(bg.D))
    half=bg.omega*((t1-t0)*.5)
    midpoint=bg.omega*(t0+(t1-t0)*.5)
    dv=2.*math.sinh(half)*(A*math.sinh(midpoint)+B*math.cosh(midpoint))
    dlog=math.log1p(dv/(1.+bg._relative_volume_increment(float(t0))))/3.
    return math.exp(l1)*math.expm1(dlog)


def _log_ratio(a,b):
    return math.log1p((a-b)/b)


def _weights_and_offsets(x):
    """Integrals [(1-u),u] exp(xu), and exp(xu)-1, over u in[0,1]."""
    # Cell widths are positive and narrow; preserve omitted-term requirement.
    if not 0 <= x < .5:
        raise ValueError('SOURCE_PRECISION_SEGMENT_WIDTH_DOMAIN')
    v0=v1=0.;term=x
    for k in range(1,25):
        v0+=term/((k+1)*(k+2));v1+=term/(k+2)
        term*=x/(k+1)
    return .5+v0,.5+v1,v0,v1


class StableCellSource:
    def __init__(self,source):
        if source.provider.r != 0.:
            raise ValueError('SOURCE_PRECISION_FLRW_ONLY')
        self.original=source;self.provider=source.provider
        self.edges=source.edges;self.mu=source.mu;self.weights=source.weights
        table=self.provider.tables['emissivity']
        self.native=table.energies_eV
        self.native_logs=np.array([[_log_ratio(e,a) for e in self.native]
                                   for a in self.edges[:-1]])
        self.cell_width=np.array([_log_ratio(b,a) for a,b in zip(self.edges[:-1],self.edges[1:])])

    def source(self,t,band=None):
        self.provider.geometry(float(t)) # strict unchanged physical time domain
        bg=self.provider.background;table=self.provider.tables['emissivity']
        lr=log_ray(bg,float(t));r=math.exp(lr)
        z=bg.z_i+(1.+bg.z_i)*math.expm1(lr)
        profile=table._z_profile(z)
        # Same proper prefactor; exact FLRW cancellation avoids two powers.
        module=sys.modules[type(table).__module__]
        factor=(1.+bg.z_i)**3/(module.MPC_CM**3*module.H_ERG_S)
        bounds=self.original._band(band)
        shape=(len(self.mu),len(self.edges)-1)
        N=np.zeros(shape);Q=np.zeros(shape);D=np.zeros(shape)
        for j,a in enumerate(self.edges[:-1]):
            lower=max(0.,_log_ratio(bounds[0],a)-lr)
            upper=min(self.cell_width[j],_log_ratio(bounds[1],a)-lr)
            if upper<=lower:continue
            knots=self.native_logs[j]-lr
            begin=max(0,int(np.searchsorted(knots,lower,side='right'))-1)
            end=min(len(knots)-1,int(np.searchsorted(knots,upper,side='left')))
            ns=[];qs=[];ds=[]
            for i in range(begin,end):
                xl=max(lower,knots[i]);xr=min(upper,knots[i+1]);dx=xr-xl
                if dx<=0:continue
                width=_log_ratio(self.native[i+1],self.native[i])
                # Compute interpolation fractions relative to the retained knot.
                f0=profile[i]+(profile[i+1]-profile[i])*((xl-knots[i])/width)
                f1=profile[i]+(profile[i+1]-profile[i])*((xr-knots[i])/width)
                if f0<0 or f1<0:raise ValueError('SOURCE_PRECISION_NEGATIVE_PROFILE_NO_CLIPPING')
                w0,w1,v0,v1=_weights_and_offsets(dx)
                n=dx*(f0+f1)*.5
                q=dx*a*math.exp(xl)*(f0*w0+f1*w1)
                d=dx*a*(math.expm1(xl)*(f0+f1)*.5+math.exp(xl)*(f0*v0+f1*v1))
                ns.append(n);qs.append(q);ds.append(d)
            for k,weight in enumerate(self.weights):
                pref=weight*factor
                N[k,j]=pref*math.fsum(ns);Q[k,j]=pref*math.fsum(qs);D[k,j]=pref*math.fsum(ds)
        R=np.full(len(self.mu),r)
        if any(not np.isfinite(x).all() or np.any(x<0) for x in (N,Q,D)):
            raise ValueError('SOURCE_PRECISION_NONFINITE_NEGATIVE')
        return {'N':N,'Q_eV':Q,'U_eV':R[:,None]*Q,'R':R,'D_eV':D}


def integrate_source(cell_source,t0,t1,event_times=(),orders=(16,32),rtol=1e-10):
    if not (math.isfinite(t0) and math.isfinite(t1) and t1>t0
            and math.isfinite(rtol) and 0<rtol<=1e-10):
        raise ValueError('SOURCE_ENTRY_TIME_DOMAIN')
    if (len(orders)!=2 or any(isinstance(n,bool) or not isinstance(n,int) or n<2 for n in orders) or orders[1]<=orders[0]):
        raise ValueError('SOURCE_ENTRY_ORDER_PAIR')
    source=cell_source if isinstance(cell_source,StableCellSource) else StableCellSource(cell_source)
    events=list(map(float,event_times))
    if not all(map(math.isfinite,events)):raise ValueError('SOURCE_ENTRY_NONFINITE_EVENT')
    points=[float(t0),*sorted(set(e for e in events if t0<e<t1)),float(t1)]
    initial,final=_old._snapshot(source,t0),_old._snapshot(source,t1)
    # Return bit-identical immutable provider geometry at accepted boundaries.
    p=source.provider
    R0=p.ray(np.ones(len(source.mu)),source.mu,float(t0))[2]
    R1=p.ray(np.ones(len(source.mu)),source.mu,float(t1))[2]
    names=('dN','dQ','injected_energy_eV','radiation_source_work_eV','dD_eV')
    approximations=[];snapshots=2
    for order in orders:
        x,w=np.polynomial.legendre.leggauss(order);pieces={name:[] for name in names}
        for left,right in zip(points[:-1],points[1:]):
            half=.5*(right-left)
            for xi,wi in zip(x,w):
                t=left+half*(1+xi)
                value=source.source(t)
                n,q,u,r=[value[key] for key in ('N','Q_eV','U_eV','R')]
                snapshots+=1
                dr=ray_difference(p.background,t,t1)
                for name,array in zip(names,(n,q,u,dr*q,value['D_eV'])):
                    pieces[name].append(half*wi*array)
        approximations.append({key:_sum_arrays(v) for key,v in pieces.items()})
    coarse,fine=approximations
    errors={key:_relative(coarse[key],fine[key]) for key in names}
    diagnostics={'schema':'rei.q1b.c11.source_precision.v1','orders':list(orders),
        'rtol':rtol,'pair_rtol':PAIR_RTOL,'event_boundaries_s':points,
        'source_evaluations':snapshots,'per_cell_fine_scale_max_errors':errors,
        'zero_fine_requires_exact_zero':True,'photon_floor':False,
        'provider_endpoint_R_byte_identity':True,
        'stable_vs_provider_R_absolute_max':float(max(np.max(abs(initial[3]-R0)),np.max(abs(final[3]-R1)))),
        'diagnostic_dD_is_authoritative':False,
        'quadrature_claim':'Predetermined order-pair comparison, not rigorous error bound',
        'pass':all(v<=rtol for v in errors.values())}
    if not diagnostics['pass']:raise SourceEntryError('SOURCE_ENTRY_TIME_QUADRATURE_REJECTED',diagnostics)
    residual=_sum_arrays([R1[:,None]*fine['dQ'],fine['radiation_source_work_eV'],-fine['injected_energy_eV']])
    scale=np.maximum.reduce([abs(R1[:,None]*fine['dQ']),abs(fine['radiation_source_work_eV']),abs(fine['injected_energy_eV'])])
    diagnostics['source_pairing_max_relative']=_scaled_residual(residual,scale)
    if diagnostics['source_pairing_max_relative']>PAIR_RTOL:
        raise SourceEntryError('SOURCE_ENTRY_SOURCE_PAIRING_REJECTED',diagnostics)
    return {**fine,'R0':R0.copy(),'R1':R1.copy(),'t0':float(t0),'t1':float(t1),
        'stable_delta_R':np.full_like(R0,ray_difference(p.background,t0,t1)),
        'diagnostics':diagnostics}


def advance_source(N0,U0,result):
    # Existing contract/domain checks and immutable geometry output are reused.
    out=_old.advance_source(N0,U0,result)
    work=result['stable_delta_R'][:,None]*(np.asarray(U0)/result['R0'][:,None])+result['radiation_source_work_eV']
    residual=_sum_arrays([out['U_eV'],-np.asarray(U0),work,-result['injected_energy_eV']])
    scale=np.maximum.reduce([abs(out['U_eV']),abs(U0),abs(work),abs(result['injected_energy_eV'])])
    pairing=_scaled_residual(residual,scale)
    if pairing>PAIR_RTOL:raise SourceEntryError('SOURCE_ENTRY_FINAL_PAIRING_REJECTED',{'pairing':pairing})
    out['radiation_work_eV']=work;out['energy_pairing_residual_eV']=residual
    out['diagnostics']['pairing_max_relative']=pairing
    out['diagnostics']['ray_work_arithmetic']='same-formula stable analytic difference'
    return out
