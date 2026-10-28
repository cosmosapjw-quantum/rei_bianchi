"""Contract-bound initial data and exact formula helpers; standard library only.

No integration, rate generation, old-bath substitution, or abundance floors.
"""
from pathlib import Path
import json
import math

UNIT=Path(__file__).resolve().parents[1]
C=299792458.
G=6.67430e-11
KB=1.380649e-23
EV_J=1.602176634e-19
KAPPA=8*math.pi*G/C**2
A17=(1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7)
Q17=(0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3)
I=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))
ZERO=((0.,0.,0.),(0.,0.,0.),(0.,0.,0.))


def matrix(flat):
    """Serialized order xx,yy,zz,xy,xz,yz; offdiagonals occur twice in A:B."""
    if len(flat)!=6 or not all(math.isfinite(x) for x in flat):raise ValueError('six finite tensor components required')
    xx,yy,zz,xy,xz,yz=map(float,flat)
    return ((xx,xy,xz),(xy,yy,yz),(xz,yz,zz))


def packed(a):return [a[0][0],a[1][1],a[2][2],a[0][1],a[0][2],a[1][2]]
def trace(a):return sum(a[j][j] for j in range(3))
def dot(a,b):return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def scale(a,factor):return tuple(tuple(factor*x for x in row) for row in a)
def add(a,b):return tuple(tuple(a[i][j]+b[i][j] for j in range(3)) for i in range(3))
def determinant(a):
    return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])


def stf(a):
    if len(a)!=3 or any(len(row)!=3 for row in a) or not all(math.isfinite(x) for row in a for x in row):
        raise ValueError('finite3x3 tensor required')
    norm=math.sqrt(dot(a,a));tol=1e-14+1e-12*norm
    if abs(trace(a))>tol or any(abs(a[i][j]-a[j][i])>tol for i in range(3) for j in range(3)):
        raise ValueError('tensor must be symmetric tracefree')
    return a


def eigenvalues_symmetric(a):
    """Closed real3x3 symmetric eigenvalues; no external eigensolver."""
    if any(not math.isclose(a[i][j],a[j][i],rel_tol=1e-12,abs_tol=1e-14) for i in range(3) for j in range(3)):
        raise ValueError('symmetric matrix required')
    q=trace(a)/3
    shifted=add(a,scale(I,-q));p=math.sqrt(dot(shifted,shifted)/6)
    if p==0:return (q,q,q)
    r=determinant(scale(shifted,1/p))/2
    # Mathematical r is in[-1,1]; bound roundoff only in this cubic identity.
    phi=math.acos(max(-1.,min(1.,r)))/3
    e1=q+2*p*math.cos(phi);e3=q+2*p*math.cos(phi+2*math.pi/3)
    return tuple(sorted((e1,3*q-e1-e3,e3)))


def quadrupole_distribution(a):
    stf(a);eigen=eigenvalues_symmetric(a)
    if eigen[0]<-1.-1e-12:raise ValueError('negative quadrupolar angular distribution')
    return {'eigenvalues':list(eigen),'minimum_angular_factor':1+eigen[0],
            'monopole_normalization':1.,'net_dipole':0.}


def lrs_quadrupole(q,axis=(0.,0.,1.)):
    if not -1<=q<=2:raise ValueError('LRS quadrupole q outside[-1,2]')
    length=math.sqrt(sum(v*v for v in axis))
    if length==0 or not math.isfinite(length):raise ValueError('nonzero finite axis required')
    n=[v/length for v in axis]
    return tuple(tuple(q/2*(3*n[i]*n[j]-(i==j)) for j in range(3)) for i in range(3))


def component_moments(rho,w,a):
    if not math.isfinite(rho) or rho<0 or not 0<=w<=1/3:raise ValueError('rho>=0 and0<=w<=1/3 required')
    angular=quadrupole_distribution(a)
    p=rho*w;pi=scale(a,2*p/5);pressure=add(scale(I,p),pi)
    return {'rho':rho,'p':p,'pi':pi,'pressure':pressure,'angular':angular,
            'minimum_pressure_eigenvalue':min(eigenvalues_symmetric(pressure))}


def initial_geometry(rho,S,Lambda=0.,kappa=KAPPA):
    stf(S)
    if not all(math.isfinite(x) for x in (rho,Lambda,kappa)) or rho<0 or kappa<=0:
        raise ValueError('invalid density/coupling')
    omega=dot(S,S)/6
    numerator=kappa*rho+Lambda*C*C
    if omega>=1 or numerator<=0:raise ValueError('constraint requires Omega_sigma<1 and positive expansion numerator')
    H=math.sqrt(numerator/(3*(1-omega)));sigma=scale(S,H)
    residual=3*H*H-kappa*rho-Lambda*C*C-dot(sigma,sigma)/2
    norm=max(3*H*H,abs(kappa*rho),abs(Lambda*C*C),dot(sigma,sigma)/2)
    return {'H_s-1':H,'sigma_s-1':sigma,'Omega_sigma':omega,'constraint_residual_s-2':residual,
            'relative_constraint_residual':residual/norm}


def gravity_derivatives(H,sigma,components,Lambda=0.,kappa=KAPPA):
    """Algebraic RHS and dC identity evaluation, never a time advance."""
    stf(sigma)
    rho=sum(row['rho'] for row in components);p=sum(row['p'] for row in components)
    pi=ZERO
    for row in components:stf(row['pi']);pi=add(pi,row['pi'])
    sigma2=dot(sigma,sigma)/2
    Hdot=-H*H-2*sigma2/3-kappa*(rho+3*p)/6+Lambda*C*C/3
    sigmadot=add(scale(sigma,-3*H),scale(pi,kappa))
    rhodot=sum(-3*H*(row['rho']+row['p'])-dot(sigma,row['pi'])+row.get('Q',0.) for row in components)
    constraint=3*H*H-kappa*rho-Lambda*C*C-sigma2
    constraint_dot=6*H*Hdot-kappa*rhodot-dot(sigma,sigmadot)
    return {'Hdot':Hdot,'sigmadot':sigmadot,'rhodot':rhodot,'C':constraint,'Cdot':constraint_dot,
            'Cdot_plus_2HC_plus_kappa_sumQ':constraint_dot+2*H*constraint+kappa*sum(row.get('Q',0.) for row in components)}


def F(n,x):
    if not math.isfinite(n) or not math.isfinite(x) or x<=0:raise ValueError('finite exponent and positive scale ratio required')
    return math.log(x) if n==0 else math.expm1(n*math.log(x))/n


def normalized_response(S0,stress_coefficient,p,m,x):
    """Return sigma/H where stress_coefficient=kappa*pi0/H0², tensor-valued."""
    stf(S0);stf(stress_coefficient)
    return scale(add(S0,scale(stress_coefficient,F(3+p-m,x))),x**(p-3))


def constant_prehistory(source,power,loss,duration_s=None,*,relaxed=False):
    """Explicit causal constant-source B/U, separate from every IC profile.

    source:particles/Href/s; power:eV/Href/s; loss:s^-1. No chosen U/B or
    implicit prehistory is supplied. Infinite-age relaxation requires loss>0.
    """
    if not all(math.isfinite(x) and x>=0 for x in (source,power,loss)):
        raise ValueError('finite nonnegative source,power,loss required')
    if source==0 and power!=0:raise ValueError('power without particle source is inconsistent')
    if relaxed:
        if duration_s is not None or loss==0:raise ValueError('explicit relaxed choice needs loss>0 and no finite duration')
        factor=1/loss;choice='EXPLICIT_RELAXED_CONSTANT_HISTORY'
    else:
        if duration_s is None or not math.isfinite(duration_s) or duration_s<0:
            raise ValueError('explicit finite nonnegative prehistory duration required')
        factor=duration_s if loss==0 else -math.expm1(-loss*duration_s)/loss
        choice='EXPLICIT_FINITE_CONSTANT_HISTORY'
    return {'B_per_Href':source*factor,'U_eV_per_Href':power*factor,'choice':choice,
            'assumed_history':'constant source/power/loss; earlier stocks zero','profile_applied':False}


def initial_profile(profile_id='legacy_reproduction_300K'):
    catalog=json.loads((UNIT/'theory/INITIAL_PROFILES.json').read_text())
    matches=[p for p in catalog['profiles'] if p['id']==profile_id]
    if len(matches)!=1:raise ValueError('explicit known initial profile required')
    profile=matches[0];y=list(profile['y_per_Href']);hidden=list(catalog['hidden_Li6']['initial_per_Href'])
    B=list(profile['B_per_Href']);U=list(profile['U_fast_eV_per_Href'])
    if len(y)!=17 or len(hidden)!=4 or len(B)!=2 or len(U)!=2 or any(not math.isfinite(x) or x<0 for x in y+hidden+B+U):
        raise ValueError('nonnegative finite species/fast stocks required')
    if any(b==0 and energy!=0 for b,energy in zip(B,U)):raise ValueError('nonzero kinetic stock with zero fast particle stock')
    electron=sum(q*v for q,v in zip(Q17,y))+B[1]+sum(q*v for q,v in enumerate(hidden))
    baryon=sum(a*v for a,v in zip(A17,y))+B[0]+3*B[1]+6*sum(hidden)
    nuclei=sum(y)+sum(hidden)
    thermal=1.5*KB*profile['temperature_K']*(nuclei+electron)/EV_J
    return {'profile_id':profile_id,'classification':profile['classification'],'state17_per_Href':y,
            'hidden_Li6_per_Href':hidden,'fast_B_per_Href':B,'fast_U_eV_per_Href':U,
            'boundary_ledgers':list(profile['boundary_ledgers']),'electron_per_Href':electron,
            'baryons_per_Href':baryon,'thermal_energy_eV_per_Href':thermal,'temperature_K':profile['temperature_K'],
            'compatible_bath':profile['compatible_bath'],'automatic_bath_substitution':False,
            'abundance_floors_added':False,'new_execution':'INITIAL_DATA_ONLY_NOT_EVOLVED'}
