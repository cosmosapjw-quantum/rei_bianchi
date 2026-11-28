"""Conditional resolved events, status-aware log coefficients, scaling and EOS.

This module supplies local algebra, not a nuclear-rate or thermal-closure
provider. Event ledgers and applicability are always explicit caller inputs.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

EPS=np.finfo(float).eps
K_B=1.380649e-23
ENERGY=('Q0','W','dI','dEth','dEfast','dEexc','dEgamma_ret','Egamma_esc','Enu')
class Unresolved(ValueError):pass
class RateOverflow(OverflowError):pass

@dataclass(frozen=True)
class Coefficient:
    status:str
    log_value:float|None=None
    def __post_init__(self):
        if self.status not in ('POSITIVE','SUPPORT_ZERO','ABSENT','UNRESOLVED'):raise ValueError('UNKNOWN_COEFFICIENT_STATUS')
        if self.status=='POSITIVE' and (self.log_value is None or not math.isfinite(self.log_value)):raise ValueError('INVALID_LOG_COEFFICIENT')
        if self.status!='POSITIVE' and self.log_value is not None:raise ValueError('NONPOSITIVE_STATUS_HAS_LOG_VALUE')
    @classmethod
    def positive(cls,value):
        if not math.isfinite(value) or value<=0:raise ValueError('POSITIVE_COEFFICIENT_REQUIRED')
        return cls('POSITIVE',math.log(value))

class LogRateTable:
    def __init__(self,T,values,interval_zero=None):
        self.x=np.log(np.asarray(T,dtype=float));self.T=np.asarray(T,dtype=float);self.values=tuple(values)
        if self.T.ndim!=1 or len(self.T)!=len(values) or len(values)<2 or np.any(~np.isfinite(self.T)) or np.any(self.T<=0) or np.any(np.diff(self.x)<=0):raise ValueError('INVALID_TEMPERATURE_TABLE')
        self.interval_zero=np.zeros(len(values)-1,dtype=bool) if interval_zero is None else np.asarray(interval_zero,dtype=bool)
        if self.interval_zero.shape!=(len(values)-1,):raise ValueError('INVALID_ZERO_INTERVAL_FLAGS')
    def at(self,T,mode='KNOT_ONLY',curvature_bound=None,relative_tolerance=None):
        if not math.isfinite(T) or T<=0:raise ValueError('INVALID_TEMPERATURE')
        exact=np.flatnonzero(self.T==T)
        if len(exact):return self.values[int(exact[0])],{'mode':'KNOT','error_bound':0.}
        if T<self.T[0] or T>self.T[-1]:raise Unresolved('EXTRAPOLATION_NOT_ADMITTED')
        if mode!='LOG_LINEAR':raise Unresolved('OFF_GRID_KNOT_ONLY')
        x=math.log(T);i=int(np.searchsorted(self.x,x)-1);left,right=self.values[i:i+2]
        if left.status==right.status=='SUPPORT_ZERO' and self.interval_zero[i]:return Coefficient('SUPPORT_ZERO'),{'mode':'DECLARED_ZERO_INTERVAL','error_bound':0.}
        if left.status!='POSITIVE' or right.status!='POSITIVE':raise Unresolved('STATUS_CROSSING_OR_ABSENT_INTERVAL')
        if curvature_bound is None or relative_tolerance is None:raise Unresolved('MISSING_INTERPOLATION_ERROR_BOUND')
        if not math.isfinite(curvature_bound) or curvature_bound<0 or not math.isfinite(relative_tolerance) or relative_tolerance<0:raise ValueError('INVALID_INTERPOLATION_BOUND')
        dx=float(self.x[i+1]-self.x[i]);log_bound=curvature_bound*dx*dx/8
        bound=math.expm1(log_bound)
        if bound>relative_tolerance:raise Unresolved('INTERPOLATION_BOUND_EXCEEDS_TOLERANCE')
        weight=(x-self.x[i])/dx;value=(1-weight)*left.log_value+weight*right.log_value
        return Coefficient('POSITIVE',value),{'mode':'LOG_LINEAR','log_error_bound':log_bound,'relative_error_bound':bound,'curvature_bound':curvature_bound}

class ResolvedEvent:
    def __init__(self,event_id,reactants,products,coefficient,unit,provenance,applicability,energy,A,q,
                 ionization_reference=None,parent_id=None,probability=None):
        if not event_id or not provenance or not applicability:raise Unresolved('MISSING_EVENT_IDENTITY_OR_APPLICABILITY')
        self.id=event_id;self.left=dict(reactants);self.right=dict(products);self.coefficient=coefficient
        if parent_id is not None or probability is not None:raise Unresolved('PARENT_BRANCH_GROUPS_UNSUPPORTED_SUPPLY_RESOLVED_CHANNELS')
        self.A=np.asarray(A);self.q=np.asarray(q);self.order=sum(self.left.values())
        if self.A.shape!=(21,) or not np.all(np.isfinite(self.A)) or np.any(self.A<0) or np.any(self.A!=np.floor(self.A)):raise ValueError('INTEGER_MASS_NUMBERS_REQUIRED')
        if self.q.shape!=(21,) or not np.all(np.isfinite(self.q)) or np.any(self.q<0) or np.any(self.q!=np.floor(self.q)):raise ValueError('INTEGER_IONIC_CHARGES_REQUIRED')
        for side in (self.left,self.right):
            if not side or any(not isinstance(i,int) or i<0 or i>=21 or not isinstance(n,int) or n<1 for i,n in side.items()):raise ValueError('INVALID_INTEGER_STOICHIOMETRY')
        if self.order not in (1,2):raise ValueError('ONLY_UNARY_BINARY_EVENTS_SUPPORTED')
        if unit!=('s^-1' if self.order==1 else 'm^3/s'):raise ValueError('COEFFICIENT_UNIT_MISMATCH')
        self.nu=np.array([self.right.get(i,0)-self.left.get(i,0) for i in range(21)],dtype=int)
        if sum(int(a)*int(v) for a,v in zip(self.A,self.nu))!=0:raise ValueError('BARYON_IMBALANCE')
        if energy is None or set(energy)!=set(ENERGY):raise Unresolved('MISSING_ENERGY_LEDGER')
        if any(not math.isfinite(v) for v in energy.values()):raise ValueError('NONFINITE_ENERGY_LEDGER')
        terms=[energy['Q0'],energy['W'],*[-energy[k] for k in ENERGY[2:]]]
        scale=max(math.fsum(abs(v) for v in terms),1e-300)
        self.energy_residual=abs(math.fsum(terms))/scale
        if self.energy_residual>128*EPS:raise ValueError('ENERGY_LEDGER_IMBALANCE')
        if ionization_reference is not None:
            expected=float(np.asarray(ionization_reference)@self.nu)
            if abs(expected-energy['dI'])/max(abs(expected)+abs(energy['dI']),1e-300)>128*EPS:raise ValueError('IONIZATION_REFERENCE_MISMATCH')
        self.energy=dict(energy);self.provenance=provenance;self.applicability=applicability;self.unit=unit
        self.parent_id=parent_id;self.probability=probability
        if probability is not None and (not math.isfinite(probability) or probability<0):raise ValueError('INVALID_BRANCH_PROBABILITY')
    def _monomial(self,Y,nb,powers,log_extra=0.):
        if self.coefficient.status in ('ABSENT','UNRESOLVED'):raise Unresolved(self.coefficient.status+'_EVENT_INPUT:'+self.id)
        if self.coefficient.status=='SUPPORT_ZERO':return 0.,-math.inf,'SUPPORT_ZERO'
        if self.order==2 and nb==0:return 0.,-math.inf,'ZERO_DENSITY'
        if any(Y[i]==0 and n>0 for i,n in powers.items()):return 0.,-math.inf,'ZERO_REACTANT'
        log_rate=self.coefficient.log_value+log_extra+(math.log(nb) if self.order==2 else 0.)
        log_rate+=math.fsum(n*math.log(Y[i]) for i,n in powers.items() if n)
        log_rate-=math.log(math.prod(math.factorial(n) for n in self.left.values()))
        if log_rate>math.log(np.finfo(float).max):raise RateOverflow('EVENT_RATE_OVERFLOW:'+self.id)
        value=math.exp(log_rate)
        return value,log_rate,'REPRESENTATIONAL_UNDERFLOW' if value==0 else 'POSITIVE'
    def evaluate(self,Y,nb):
        y=np.asarray(Y,dtype=float)
        if y.shape!=(21,) or not np.all(np.isfinite(y)) or np.any(y<0) or not math.isfinite(nb) or nb<0:raise ValueError('INVALID_EVENT_STATE')
        rate,log_rate,status=self._monomial(y,nb,self.left)
        gradient=np.zeros(21)
        for i,n in self.left.items():
            powers=dict(self.left);powers[i]-=1
            gradient[i]=self._monomial(y,nb,powers,math.log(n))[0]
        return {'id':self.id,'rate':rate,'log_rate':log_rate,'status':status,'gradient':gradient,
                'nu':self.nu,'source':self.nu*rate,'jacobian':np.outer(self.nu,gradient),
                'electron_source':float(self.q@self.nu)*rate,'nucleus_source':int(sum(self.nu))*rate,
                'thermal_particle_source':float((1+self.q)@self.nu)*rate,
                'reservoir_sources':{key:self.energy[key]*rate for key in ENERGY[2:]},
                'provenance':self.provenance,'applicability':self.applicability}


def evaluate_events(events,Y,nb):
    # Only fully resolved channel coefficients are supported. Parent probabilities
    # are rejected by ResolvedEvent; there is no implicit or ignored weighting.
    rows=[event.evaluate(Y,nb) for event in events]
    return {'source':sum((row['source'] for row in rows),np.zeros(21)),
            'jacobian':sum((row['jacobian'] for row in rows),np.zeros((21,21))),
            'events':rows,'electron_source':math.fsum(row['electron_source'] for row in rows),
            'nucleus_source':math.fsum(row['nucleus_source'] for row in rows),
            'thermal_particle_source':math.fsum(row['thermal_particle_source'] for row in rows),
            'reservoir_sources':{key:math.fsum(row['reservoir_sources'][key] for row in rows) for key in ENERGY[2:]}}


def outer_transform(F,J,scales,H):
    s=np.asarray(scales,dtype=float)
    if s.shape!=(21,) or not np.all(np.isfinite(s)) or np.any(s<=0) or not math.isfinite(H) or H<=0:raise ValueError('INVALID_OUTER_SCALE_OR_H')
    return np.asarray(F)/s/H,np.asarray(J)*s[None,:]/s[:,None]/H


def thermal_rhs(Y,F,q,T,H,Q_per_baryon,fast_e=0.,fast_edot=0.):
    if Q_per_baryon is None:raise Unresolved('MISSING_TOTAL_TRANSLATIONAL_ENERGY_SOURCE')
    y=np.asarray(Y);q=np.asarray(q);source=np.asarray(F)
    if any(not math.isfinite(v) for v in (T,H,Q_per_baryon,fast_e,fast_edot)) or T<0 or H<0 or fast_e<0 or fast_e>float(q@y):raise ValueError('INVALID_THERMAL_STATE')
    C=float((1+q)@y-fast_e);Cdot=float((1+q)@source-fast_edot)
    if C<=0:raise ValueError('NONPOSITIVE_HEAT_CAPACITY')
    Tdot=-2*H*T+(2*Q_per_baryon/(3*K_B)-T*Cdot)/C
    return {'C_th':C,'dot_C_th':Cdot,'dot_T_K_s':Tdot}
