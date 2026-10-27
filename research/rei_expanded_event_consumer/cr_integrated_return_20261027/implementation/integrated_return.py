"""Integrated diagnostic map: native25 plus retained-photon two-port.

No rate, history, physical abundance update, or 27-state ODE is constructed.
Only unchanged CR validation helpers are called; no producer generator is run.
"""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('cr_export_validation', UNIT/'vendor/cr/export_adapter.py')
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)
EV_J = 1.602176634e-19
I = 54.42 * EV_J
DENSITY = tuple(i for i in range(27) if i != 24)


def real(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int,float)):
        raise ValueError(name+': explicit real required')
    x=float(value)
    if not math.isfinite(x) or (positive and x<=0) or (nonnegative and x<0):
        raise ValueError(name+': finite domain required')
    return x


def vector(x, name):
    if len(x)!=27: raise ValueError(name+': length27 diagnostic serialization required')
    return [real(v,name) for v in x]


def flatten(a,k,g):
    v=[0.0]*27
    v[11],v[12],v[21],v[22],v[25],v[26]=a,-a,-a,-k,a,g
    return v


def normalize(A,K,G,b, *, dA=0.0,dK=0.0,dG=0.0,db=0.0):
    """General input-interface JVP; signed finite directions are independent."""
    A,K,G=[real(v,n,nonnegative=True) for v,n in ((A,'A'),(K,'K'),(G,'G'))]
    b=real(b,'b',positive=True)
    dA,dK,dG,db=[real(v,n) for v,n in ((dA,'dA'),(dK,'dK'),(dG,'dG'),(db,'db'))]
    a,k,g=A/b,K/b,G/b
    da,dk,dg=dA/b-a*db/b,dK/b-k*db/b,dG/b-g*db/b
    delta,jvp=flatten(a,k,g),flatten(da,dk,dg)
    residual=math.fsum((-I*A,-K,G))
    derivative=math.fsum((-I*dA,-dK,dG))/b-residual*db/(b*b)
    if not all(math.isfinite(x) for x in delta+jvp+[derivative]):
        raise ValueError('finite normalized output required')
    return {'native25_delta':delta[:25], 'native25_jvp':jvp[:25],
        'retained_photon_port':{'count_per_baryon':a,'energy_J_per_baryon':g,
            'count_jvp':da,'energy_jvp':dg,'native_w_ext_owner':False},
        'flat27_diagnostic':delta,'flat27_jvp':jvp,
        'energy_constraint':residual/b,'energy_constraint_jvp':derivative,
        'state_update_applied':False, 'finite_coupled_abundance_update':False}


def consume(event, b=None, **directions):
    if isinstance(event,(list,tuple)): raise ValueError('alternative batch cannot be summed')
    cr.validate_event(event)
    A=event['integrated_count_m3']; energy=event['integrated_energy_J_m3']
    out={'canonical_event_id':event['canonical_event_id'], 'case':event['case'],'z':event['z'],
        'proper_volume_event':deepcopy(event),'native_projection':None,
        'normalization':'INTEGRATED_PER_PROPER_VOLUME','state_update_applied':False}
    if b is None:
        if directions: raise ValueError('explicit positive consumer b needed for directions')
        return out
    out['native_projection']=normalize(A,-energy['fast_kinetic'],energy['radiation'],b,**directions)
    out['normalization']='DECLARED_CONSUMER_DIAGNOSTIC_PER_BARYON'
    return out


def admit_once(event, seen, *, case, z):
    """One scenario validation guard, never an alternative accumulator."""
    cr.validate_event(event)
    if (event['case'],event['z'])!=(case,z): raise ValueError('alternatives cannot be combined')
    key=event['canonical_event_id']
    if key in seen: raise ValueError('duplicate event')
    seen.add(key)


def read_actual(path=None):
    data=json.loads((path or UNIT/'vendor/cr/INTEGRATED_EVENT_EXPORTS.json').read_text())
    if data.get('schema')!='CR_HEIII_INTEGRATED_EXPORTS_V1': raise ValueError('export schema')
    events=data['events']; ids=set()
    if len(events)!=24: raise ValueError('exact24 alternatives required')
    for e in events:
        cr.validate_event(e)
        if e['canonical_event_id'] in ids: raise ValueError('duplicate event')
        ids.add(e['canonical_event_id'])
    return events


def reference(delta,jvp,beta,dbeta):
    d,t=vector(delta,'delta'),vector(jvp,'jvp')
    beta=real(beta,'beta',positive=True); dbeta=real(dbeta,'dbeta')
    out=d.copy(); tangent=t.copy()
    for i in DENSITY: out[i],tangent[i]=beta*d[i],beta*t[i]+dbeta*d[i]
    return out,tangent


def integrated_clock_pair(event,b,H,*,dH=0.0,**directions):
    real(H,'H',positive=True); real(dH,'dH')
    p=consume(event,b,**directions)['native_projection']
    return {'proper':p,'eta':deepcopy(p),'d_dH':[0.0]*27,'is_rate':False}


def endpoint_reference(x,dx,rminus,rplus,drminus,drplus,delta_n,ddelta_n):
    """Algebra only at fixed physical volume; logT passes through."""
    x,dx,dn,ddn=[vector(v,n) for v,n in ((x,'x'),(dx,'dx'),(delta_n,'dn'),(ddelta_n,'ddn'))]
    rm,rp=real(rminus,'rminus',positive=True),real(rplus,'rplus',positive=True)
    drm,drp=real(drminus,'drminus'),real(drplus,'drplus')
    plus=x.copy(); tangent=dx.copy()
    for i in DENSITY:
        plus[i]=(rm*x[i]+dn[i])/rp
        tangent[i]=(rm*dx[i]+x[i]*drm+ddn[i])/rp-plus[i]*drp/rp
    return plus,tangent


def capacity(A,K,nHeIII,Nfast,Ufast):
    A,K,nH,nF,uF=[real(v,n,nonnegative=True) for v,n in
        ((A,'A'),(K,'K'),(nHeIII,'nHeIII'),(Nfast,'Nfast'),(Ufast,'Ufast'))]
    bounds=[nH/A if A else None,nF/A if A else None,uF/K if K else None]
    finite=[x for x in bounds if x is not None]
    return {'bounds':dict(zip(('HeIII','fast_count','fast_energy'),bounds)),
        'smax':min(finite) if finite else None,'unconstrained_bounds_are_null':True,
        'is_applied_step':False,'is_history_or_submeasure_qualification':False}
