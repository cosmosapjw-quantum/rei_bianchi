#!/usr/bin/env python3
"""R45 positive 3x3 deuterium tracer on a Faure21 self-consistent H/e/thermal FLRW history.
Uses only published Faure Table 1 D1..D6, or explicitly source-swapped Grackle
k52/k53. Linear tracer assumption neglects O(D/H) backreaction on the H bath.
Magnus order-2 piecewise midpoint propagator exp(K*delta_lambda/H), automatically
conserves total D and positivity for any positive coefficients.
"""
from __future__ import annotations
import math, json
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from faure21_flrw import Cosmology, IDX, LABELS, rates, initial, run, SEC_MYR, save_csv


def matrix(lam, refsol, c, model='faure'):
    z=(1+c.z_initial)*math.exp(-lam)-1
    x=refsol.sol(lam)
    temp=float(x[12]);Tr=c.T0_K*(1+z)
    k=rates(temp,Tr)
    if model=='grackle_k52_k53':
        l=math.log10(temp)
        k[LABELS.index('D5')]=1e-9*(.417+.846*l-.137*l*l) if temp<=1e4 else 1.609e-9
        k[LABELS.index('D6')]=1.1e-9*math.exp(-488/temp)
    elif model!='faure':raise ValueError('network')
    n=c.nH(z);v=x[:12]
    a=k[LABELS.index('D2')]+k[LABELS.index('D4')]*n*v[IDX['Hp']]
    b=k[LABELS.index('D1')]*n*v[IDX['e']]+k[LABELS.index('D3')]*n*v[IDX['H']]
    f=k[LABELS.index('D5')]*n*v[IDX['H2']]
    d=k[LABELS.index('D6')]*n*v[IDX['Hp']]
    return np.array([[-a,b,0.],[a,-b-f,d],[0.,f,-d]]),{'a':a,'b':b,'formation_Dp_to_HD':f,'destruction_HD_to_Dp':d}


def integrate_tracer(c,refsol,model,nsteps=2400,outputs=241):
    z0,zf=c.z_initial,c.z_final
    L=math.log((1+z0)/(1+zf)); lams=np.linspace(0,L,nsteps+1)
    y=initial(c)[[IDX['D'],IDX['Dp'],IDX['HD']]].copy()
    out=[]
    requested=np.linspace(0,L,outputs)
    allstates=np.empty((nsteps+1,3));allstates[0]=y
    for i in range(nsteps):
        lo,hi=lams[i:i+2];mid=(lo+hi)/2
        km,_=matrix(mid,refsol,c,model)
        zm=(1+c.z_initial)*math.exp(-mid)-1
        prop=expm(km/c.Hubble(zm)*(hi-lo))
        y=prop@y
        allstates[i+1]=y
    for lam in requested:
        if lam==L:ii=nsteps
        else:ii=int(np.floor(lam/L*nsteps))
        # operator-consistent within-bin exact exp, not linear interpolation
        loc=lam-lams[ii]
        if loc>0:
            mid=(lams[ii]+lam)/2;z=(1+c.z_initial)*math.exp(-mid)-1
            op,_=matrix(mid,refsol,c,model)
            yy=expm(op/c.Hubble(z)*loc)@allstates[ii]
        else:yy=allstates[ii]
        z=(1+c.z_initial)*math.exp(-lam)-1
        src=refsol.sol(lam);K,pr=matrix(lam,refsol,c,model)
        out.append({'model':model,'z':float(z),'elapsed_Myr':float(src[13]),
                    'nH_nuclei_cm3':float(c.nH(z)),'Tgas_K':float(src[12]),
                    'x_D':float(yy[0]),'x_Dp':float(yy[1]),'x_HD':float(yy[2]),
                    'D_fractional_conservation':float(sum(yy)),
                    'HD_formation_Dp_loss_s_inv':float(pr['formation_Dp_to_HD']),
                    'HD_destruction_HD_loss_s_inv':float(pr['destruction_HD_to_Dp']),
                    'HD_formation_per_H_s':float(pr['formation_Dp_to_HD']*yy[1]),
                    'HD_destruction_per_H_s':float(pr['destruction_HD_to_Dp']*yy[2])})
    return out


def main():
    root=Path(__file__).resolve().parents[1];d=root/'results';d.mkdir(exist_ok=True)
    c=Cosmology();z,x,res,sol=run(c,N=241)
    allrows=[]
    for model in ('faure','grackle_k52_k53'):
        allrows+=integrate_tracer(c,sol,model,nsteps=2400)
    save_csv(d/'R45_D_TRACER_PUBLIC_SOURCE_CONTRAST.csv',allrows)
    print(json.dumps({s:next(reversed([r for r in allrows if r['model']==s])) for s in ('faure','grackle_k52_k53')},indent=2))

if __name__=='__main__':main()
