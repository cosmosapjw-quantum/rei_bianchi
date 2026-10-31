#!/usr/bin/env python3
"""Independent minimal BASS193 direct Coulomb clock replay. NO cosmological IVP.
Usage: python reproduce_coulomb.py REI_F4_CAUSAL_MEMORY_20261031_FULL.zip outdir
Requires numpy, scipy; the original ZIP must match its locked SHA256.
"""
from pathlib import Path
from scipy.integrate import quad
import argparse, hashlib, io, json, math, zipfile
import numpy as np

EXPECTED='d46b61d49b025c6a81b003304223cb9c9aec5863432c80c53e883cf11055ad88'
PREFIX='REI_F4_CAUSAL_MEMORY_20261031/'
ME=9.1093837139e-28; EV=1.602176634e-12
E2=7.2973525693e-3*1.054571817e-27*2.99792458e10
ELOW=13.7; EHIGH=61.0; YEAR=31557600.0

def t_ee(EeV, ne):
    if not(EeV>=ELOW and ne>0): raise ValueError('FS2010 Eq12 domain')
    lnL=math.log(4*EeV/(7.40e-11*ne))
    if lnL<=1:raise ValueError('Coulomb log outside monotonic domain')
    E=EeV*EV
    return E*ME*math.sqrt(2*E/ME)/(4*math.pi*E2**2*ne*lnL)

def settle_time(ne):
    return quad(lambda E:t_ee(E,ne)/E,ELOW,EHIGH,epsrel=5e-11)[0]

def run(archive,outdir):
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError('immutable PR306 input SHA mismatch')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None: raise ValueError('ZIP CRC')
        with np.load(io.BytesIO(z.read(PREFIX+'source_bass/trajectory.npz')),allow_pickle=False) as data:
            Y=data['Y']; q=data['q']; labels=list(data['diagnostic_names']); d=data['diagnostics']
            zred=data['z']; x=data['x']; b=d[:,labels.index('b')]
            nb=d[:,labels.index('nb_m3')]; ne=d[:,labels.index('ne_m3')]
            H=d[:,labels.index('H')]; ts=d[:,labels.index('elapsed_s')]
    if len(zred)!=193 or Y.shape!=(193,21) or np.max(abs(nb*(Y@q)/ne-1))>=3e-14:
        raise AssertionError('original BASS21 charge and shape')
    plasma=[]
    for i in range(193):
        te=t_ee(EHIGH,float(ne[i]*1e-6)); t131=settle_time(float(ne[i]*1e-6))
        plasma.append((i,float(zred[i]),float(ne[i]*1e-6),float(H[i]),te/YEAR,t131/YEAR,float(H[i]*te)))
    slopes=np.diff(b)/np.diff(x)
    intervals=[]
    for j in range(192):
        dt=float(ts[j+1]-ts[j]); low=float(min(ne[j],ne[j+1])*1e-6)
        te=t_ee(EHIGH,low);tau=settle_time(low)
        intervals.append((j,float(zred[j+1]),dt/YEAR,te/dt,tau/dt,1-float(slopes[j]),1+2*float(slopes[j])))
    P=np.asarray(plasma,float); Q=np.asarray(intervals,float)
    if not np.all(np.diff(ts)>0) or not np.all(Q[:,5:]>0):
        raise AssertionError('proper time / two positive directional expansion factors')
    outdir.mkdir(parents=True,exist_ok=True)
    np.savetxt(outdir/'plasma193.csv',P,delimiter=',',header='epoch,z,ne_cm3,H_s,tee61_year,tau61to13p7_year,Htee61',comments='',fmt='%.17g')
    np.savetxt(outdir/'clock192.csv',Q,delimiter=',',header='arrival,z_low,dt_year,tee61_over_dt,tau_over_dt,perp_expansion,parallel_expansion',comments='',fmt='%.17g')
    result={'epochs':193,'arrival':192,'max_tee61_over_dt':float(max(Q[:,3])),
       'max_tau61_to_13p7_over_dt':float(max(Q[:,4])),'max_H_tee61':float(max(P[:,6])),
       'min_perp_expansion':float(min(Q[:,5])),'min_parallel_expansion':float(min(Q[:,6])),
       'label':'E>13.7eV PRIMARY COULOMB ONLY, source-conditional, NO IVP'}
    (outdir/'replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input_zip',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();print(json.dumps(run(args.input_zip,args.output),indent=2))
