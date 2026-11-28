"""Dimensionless signed LRS Frobenius coordinates; sum signed stress first."""
import math
C=299792458.0
G=6.67430e-11
KAPPA_T=8*math.pi*G/C**2

def normalized(H,s,pi_s_components):
    if H<=0: raise ValueError('H must be positive')
    u=math.sqrt(6)*s/H
    v=KAPPA_T*math.sqrt(6)*sum(pi_s_components)/H**2
    return dict(u=u,v=v,Sigma_F=abs(u),Pi_F=abs(v),Sigma_half=abs(u)/math.sqrt(2),Pi_half=abs(v)/math.sqrt(2))

def initial_mapping(Sigma_F,Pi_F,stress_sign,source):
    if not (0<=Sigma_F<math.sqrt(6) and Pi_F>=0 and stress_sign in (-1,0,1) and (Pi_F==0)==(stress_sign==0)): raise ValueError('invalid requested coordinates')
    q=Sigma_F/math.sqrt(6-Sigma_F**2)
    fr=source.h0**2*source.omega_r/(source.aref**4*source.href**2)
    A=stress_sign*5*Pi_F*(1+q*q)/(math.sqrt(6)*fr)
    if abs(A)>.5: raise ValueError('radiation amplitude exceeds frozen domain')
    return dict(Sigma_ref=Sigma_F/math.sqrt(2),orientation=int(Sigma_F>0),kappa_gamma=A,kappa_nu=A)

def c15_normalized(row,control=False):
    parts=[row[k]/3 for k in ('Pi_gamma','Pi_nu','Pi_massive','Pi_UV')]
    result=normalized(row['H'],row['s_inv_s'],parts)
    result.update(gravitational_source_v=KAPPA_T*math.sqrt(6)*(row['Pi_total_source']/3)/row['H']**2,control=control)
    return result
