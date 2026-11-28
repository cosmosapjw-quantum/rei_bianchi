
from __future__ import annotations
import math
from numbers import Real
import numpy as np
from scipy.linalg import norm

def _real(x,name):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,Real) or not math.isfinite(float(x)):
        raise ValueError(name+" must be finite real")
    return float(x)

def _n2(x):
    a=np.asarray(x)
    return float(abs(a)) if a.ndim==0 else float(norm(a,2))

def cubic_hermite(v0,v1,d0,d1,h,u):
    h=_real(h,"h"); u=_real(u,"u")
    if h<=0 or not 0<=u<=1: raise ValueError("h>0 and u in [0,1] required")
    h00=2*u**3-3*u**2+1; h10=u**3-2*u**2+u
    h01=-2*u**3+3*u**2; h11=u**3-u**2
    dh00=6*u*u-6*u; dh10=3*u*u-4*u+1
    dh01=-6*u*u+6*u; dh11=3*u*u-2*u
    value=h00*np.asarray(v0)+h*h10*np.asarray(d0)+h01*np.asarray(v1)+h*h11*np.asarray(d1)
    deriv=(dh00*np.asarray(v0)+h*dh10*np.asarray(d0)+dh01*np.asarray(v1)+h*dh11*np.asarray(d1))/h
    return value,deriv

def piecewise_candidate(times, values, derivatives, ks, t):
    if not (len(times)==len(values)==len(derivatives)==len(ks)) or len(times)<2:
        raise ValueError("aligned node data required")
    ts=np.asarray(times,dtype=float)
    if not np.isfinite(ts).all() or np.any(np.diff(ts)<=0): raise ValueError("strictly increasing finite times required")
    t=_real(t,"t")
    if t<ts[0] or t>ts[-1]: raise ValueError("t outside domain")
    j=len(ts)-2 if t==ts[-1] else int(np.searchsorted(ts,t,side="right")-1)
    h=ts[j+1]-ts[j]; u=(t-ts[j])/h
    O,dotO=cubic_hermite(values[j],values[j+1],derivatives[j],derivatives[j+1],h,u)
    K=(1-u)*np.asarray(ks[j])+u*np.asarray(ks[j+1])
    Dcol=dotO/2+K
    Drow=(dotO/2-K).conj().T
    return O,dotO,Dcol,Drow,K,j

def separation(a,b):
    vals=[_n2(np.asarray(a[i])-np.asarray(b[i])) for i in range(5)]
    return {"O":vals[0],"dotO":vals[1],"Dcol":vals[2],"Drow":vals[3],"K":vals[4],
            "Dmax":max(vals[2],vals[3]),"T_like_primary":math.hypot(vals[4],max(vals[2],vals[3]))}

def select_midpoint(candidates, old_predict, new_predict):
    rows=[]
    for z in candidates:
        old=old_predict(z); new=new_predict(z)
        s=separation(old,new); s["z"]=float(z); rows.append(s)
    best=max(rows,key=lambda r:(r["T_like_primary"],-r["z"]))
    return {"rows":rows,"selected_z":best["z"],"criterion":"max sqrt(DeltaK^2+DeltaDmax^2); tie -> lower z"}
