"""Manufactured affine coefficient interval study; independent scaled Radau truth."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from age_envelope import enclosure


def coefficient_bounds(a,b,star):
    j=(1e-4*(1+.3*a),1e-4*(1+.3*b))
    r=[(105*(1+.2*a),105*(1+.2*b)),(85*(1+.12*a),85*(1+.12*b))]
    if b<=star:r.append((0.,0.))
    elif a>=star:r.append((130*(1+.09*(a-star)),130*(1+.09*(b-star))))
    else:r.append((0.,130*(1+.09*(b-star))))
    return j,r


def reference(star):
    y=np.zeros(4);calls=0
    # Continuous state with separate smooth domains at the opacity switch.
    for a,b,on in [(0.,star,False),(star,1.,True)]:
        def rhs(x,y):
            k=np.array([105*(1+.2*x),85*(1+.12*x),130*(1+.09*(x-star)) if on else 0.])
            events=k*y[0]
            return np.r_[1+.3*x-events.sum(),events]
        sol=solve_ivp(rhs,(a,b),y,method='Radau',rtol=2e-12,atol=1e-14)
        if not sol.success:raise RuntimeError(sol.message)
        y=sol.y[:,-1];calls+=sol.nfev
    return y*1e-4,calls


def evaluate(n,star,split):
    grid=sorted(set(np.linspace(0.,1.,n+1).tolist()+([star] if split else [])))
    ni=(0.,0.);absorbed=np.zeros((3,2));heat=np.zeros(2)
    for a,b in zip(grid,grid[1:]):
        j,r=coefficient_bounds(a,b,star)
        ans=enclosure(ni,j,r,b-a,(80,80))
        ni=ans.n;absorbed+=ans.absorbed;heat+=ans.heat
    return {'n':list(ni),'absorbed':absorbed.tolist(),'heat':heat.tolist(),'slabs':len(grid)-1}


def study():
    rows=[]
    for star in (.73,.985):
        truth,calls=reference(star)
        for n in (8,16,32,64,128,256,512,1024,2048):
            for split in (False,True):
                r=evaluate(n,star,split)
                assert r['n'][0]-2e-15<=truth[0]<=r['n'][1]+2e-15
                for bound,val in zip(r['absorbed'],truth[1:]):
                    assert bound[0]-2e-15<=val<=bound[1]+2e-15
                rows.append(dict(star=star,panels=n,event_split=split,**r,
                  true_state=truth.tolist(),reference_calls=calls,
                  survivor_relative_width=(r['n'][1]-r['n'][0])/truth[0],
                  heii_event_absolute_width=r['absorbed'][2][1]-r['absorbed'][2][0]))
    return {'scope':'manufactured prescribed affine coefficients, E=80 eV, opacity switch not photon threshold',
            'arithmetic':'real comparison theorem; binary64 evaluation, not outward certified',
            'rows':rows,'all_truth_enclosure_checks':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);r=study()
    (a.out/'AFFINE_INTERVAL_STUDY.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    for row in r['rows']:
        if row['panels']==8:print(row['star'],row['event_split'],row['survivor_relative_width'],row['heii_event_absolute_width'])
