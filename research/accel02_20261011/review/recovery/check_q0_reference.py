#!/usr/bin/env python3
"""Independent Q0 ordinate/units check from literal table rows. No model solver."""
import json,hashlib,math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
REPO=BASE.parents[1]
SOURCE=REPO/'research/physical_provider_20261010/sources'
H=6.62607015e-27;C=2.99792458e10;EV=1.602176634e-12
MPC=648000./math.pi*149597870700.*100.*1e6
HC=H*C/EV*1e8
BANDS={'full':(10.,50000.),'HI_ionizing':(13.60,50000.),'HeI_ionizing':(24.59,50000.),'HeII_ionizing':(54.42,50000.)}
DISJOINT={'below_HI':(10.,13.60),'HI_to_HeI':(13.60,24.59),'HeI_to_HeII':(24.59,54.42),'above_HeII':(54.42,50000.)}
def raw(name):
    lines=[x.split() for x in (SOURCE/name).read_text().splitlines() if x.strip() and not x.lstrip().startswith('#')]
    zs=np.array(lines[0],float);d=np.array(lines[1:],float)[::-1]
    return zs,HC/d[:,0],d[:,1:]
def profile(table,z):
    zz,E,vals=table;i=np.searchsorted(zz,z)
    if zz[i]==z:return E,vals[:,i]
    w=(z-zz[i-1])/(zz[i]-zz[i-1]);return E,(1-w)*vals[:,i-1]+w*vals[:,i]
def integrate(table,z,lo,hi,p,kind):
    E,f=profile(table,z);terms=[];gx,gw=np.polynomial.legendre.leggauss(16)
    for i in range(len(E)-1):
        a=max(lo,E[i]);b=min(hi,E[i+1])
        if b<=a:continue
        x0,x1=np.log(E[i]),np.log(E[i+1]);aa,bb=np.log(a),np.log(b)
        slope=(f[i+1]-f[i])/(x1-x0)
        if p==0:
            term=(bb-aa)*(f[i]+slope*(aa-x0)+f[i]+slope*(bb-x0))/2
        else:
            x=(aa+bb)/2+(bb-aa)/2*gx
            term=(bb-aa)/2*np.dot(gw,(f[i]+slope*(x-x0))*np.exp(x))
        terms.append(float(term))
    factor=4*math.pi/(C*H) if kind=='uvb' else (1+z)**3/(MPC**3*H)
    return math.fsum(terms)*factor*(EV if p else 1.)
def main():
    Q=json.loads((BASE/'recovery/Q0_SOURCE_ATTRIBUTION.json').read_text());uvb=raw('UVB.out');em=raw('emissivity.out')
    ic_checks={};ic_error=0
    for band,(lo,hi) in BANDS.items():
        for p,label in [(0,'number'),(1,'energy')]:
            val=integrate(uvb,15.9,lo,hi,p,'uvb');record=Q['runs']['EVENT_COUPLED002']['initial_UVB_moment_comparison'][f'{band}_{label}']['exact_declared_interpolation']
            error=abs(val-record)/abs(record);ic_error=max(ic_error,error)
            ic_checks[f'{band}_{label}']={'independent':val,'q0':record,'relative_difference':error}
    selected=[0,119,122,128];source_checks={};source_error=0
    for ix in selected:
        row=Q['exact_source_history'][ix];z=row['z'];r={}
        for band,(lo,hi) in BANDS.items():
            for p,label in [(0,'number'),(1,'energy')]:
                val=integrate(em,z,lo,hi,p,'emissivity');record=row[f'{band}_{label}_proper'];error=abs(val-record)/abs(record);source_error=max(source_error,error)
                r[f'{band}_{label}']={'independent':val,'q0':record,'relative_difference':error}
        source_checks[str(ix)]={'z':z,'fields':r}
    partition={}
    exact_total=integrate(uvb,15.9,10,50000,0,'uvb')
    for run in Q['runs']:
        with np.load(BASE/'n2/evidence'/run/'history.npz') as z:
            q=z['q'];N=(z['scaled_states'][0]*z['scales'])[4:4+len(q)]/q
        partition[run]={}
        for band,(lo,hi) in DISJOINT.items():
            mask=(q>=lo)&(q<hi) if hi<50000 else (q>=lo)&(q<=hi)
            sample=float(N[mask].sum());exact=integrate(uvb,15.9,lo,hi,0,'uvb')
            partition[run][band]={'sampled_N':sample,'exact_N':exact,'signed_error_divided_by_exact_full_N':(sample-exact)/exact_total}
    output={'schema':'rei_accel02_q0_independent_reference_v1','method':'Literal rows parsed independently; z-ordinate interpolation; p0 exact log-interval trapezoid, p1 16-point Gauss per native nonzero-width log-energy interval; duplicate rows skipped only as zero-width measure; standard cgs conversions explicit.','implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'ODE_calls':0,'native_calls':0,'source_attribution_sha256':hashlib.sha256((BASE/'recovery/Q0_SOURCE_ATTRIBUTION.json').read_bytes()).hexdigest(),'max_IC_relative_difference':ic_error,'max_selected_source_relative_difference':source_error,'IC':ic_checks,'source_selected_epochs':source_checks,'initial_number_disjoint_attribution':partition}
    (HERE/'Q0_REFERENCE_ARITHMETIC.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'IC_error':ic_error,'source_error':source_error,'partition':partition},indent=2))
if __name__=='__main__':main()
