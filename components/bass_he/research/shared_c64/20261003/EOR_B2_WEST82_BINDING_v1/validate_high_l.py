"""Independent analytic manufactured checks. Not atomic cross sections."""
import json,math
from pathlib import Path
import mpmath as mp
import numpy as np
from bass_he_west82 import solve_partial_wave
mp.mp.dps=110

def exact(e,l,V,g,R):
    e=mp.mpf(str(e));V=mp.mpf(str(V));g=mp.mpf(str(g));R=mp.mpf(str(R))
    q=mp.sqrt(e-V+mp.j*g/2);k=mp.sqrt(e);nu=mp.mpf(l)+mp.mpf('.5')
    def jb(z):return mp.sqrt(mp.pi*z/2)*mp.besselj(nu,z)
    def nb(z):return mp.sqrt(mp.pi*z/2)*mp.bessely(nu,z)
    u=jb(q*R);up=q*mp.diff(jb,q*R)
    j=jb(k*R);n=nb(k*R);dj=k*mp.diff(jb,k*R);dn=k*mp.diff(nb,k*R)
    a=(u*dn-up*n)/k;b=(j*up-dj*u)/k
    s=(a-mp.j*b)/(a+mp.j*b)
    return s,1-abs(s)**2

rows=[]
for l in [20,32,33,38,48,64]:
    for e in [.2,1.,4.]:
        R=(l+3)/math.sqrt(e);V=-.15*e;g=.005*e
        out=solve_partial_wave(e,l,[0.,R],[V],[[g]])
        s,p=exact(e,l,V,g,R)
        err_s=float(abs(mp.mpc(*out['S'])-s));err_p=float(abs(mp.mpf(out['loss_probability'])-p)/p)
        row={'ell':l,'energy':e,'R':R,'V':V,'g':g,'loss':out['loss_probability'],'exact_110digit_loss':str(p),'S_abs':err_s,'P_rel':err_p}
        rows.append(row)
        assert err_s<1e-9 and err_p<1e-9,row
weak=[]
for l in [33,48,64]:
    R=l+3.;g=1e-22
    out=solve_partial_wave(1.,l,[0.,R],[0.],[[g]])
    s,p=exact(1.,l,0.,g,R)
    er=float(abs(mp.mpf(out['loss_probability'])-p)/p)
    row={'ell':l,'g':g,'loss':out['loss_probability'],'subtraction':out['loss_by_subtraction'],'P_rel':er,'exact_110digit_loss':str(p)}
    weak.append(row);assert er<1e-9,row
split=[]
for l in [32,48]:
    R=l+3.;a=1e-5;edges=np.r_[0.,np.geomspace(a,R,81)]
    x=solve_partial_wave(1.,l,edges,[0.]*(len(edges)-1),[[1e-4]]*(len(edges)-1))
    s,p=exact(1.,l,0.,1e-4,R)
    err=float(abs(mp.mpf(x['loss_probability'])-p)/p)
    row={'ell':l,'first_edge':a,'shells':len(edges)-1,'P_rel':err,'S_abs':float(abs(mp.mpc(*x['S'])-s)),'nfev':x['nfev']}
    split.append(row);assert err<1e-8 and row['S_abs']<1e-8,row
summary={'schema':'bass-he.west82.high-l-validation.v1','cases':rows,'rare_cases':weak,'small_origin_cases':split,'max_S_abs':max(x['S_abs'] for x in rows),'max_P_rel':max(x['P_rel'] for x in rows),'max_rare_P_rel':max(x['P_rel'] for x in weak),'physical_atomic_runs':0,'reference_precision_digits':110,'all_cases':'DECLARED_MANUFACTURED_SQUARE_WELLS_NOT_WEST_PHYSICAL_INPUTS'}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    with a.out.open('x') as f:json.dump(summary,f,indent=2)
    print(json.dumps({k:v for k,v in summary.items() if k.startswith('max_')},indent=2));print(split)
