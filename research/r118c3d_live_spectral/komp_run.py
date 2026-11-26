import json,hashlib
from pathlib import Path
import numpy as np
from scipy.sparse.linalg import expm_multiply
from kompaneets import LinearKompaneets
D=Path(__file__).resolve().parent;P=D.parent/'r118c3c_spectral_exchange/table512_spectrum.csv'
r=np.genfromtxt(P,names=True,delimiter=',');xp=r['x'];df=r['delta'];fp=1/np.expm1(xp)
print('source max fractional distortion x>=1e-5',max(abs(df[xp>=1e-5]/fp[xp>=1e-5])))
# actual post-recombination Thomson Compton y clock from C3B, but fixed Te=Tgamma
# operator tested separately using reference thermal clock and amplified exposure.
H=Path('/home/cosmosapjw/Downloads/bass_r118c3b_table/history.csv');v=np.genfromtxt(H,names=True,delimiter=',')
a=v['a'];tc=2.7255/a
theta=1.380649e-23*tc/(9.1093837139e-31*299792458.**2)
y0=float(np.trapezoid(theta*299792458*6.6524587051e-29*v['ne']/(2.1842852410855023e-18*v['h']),np.log(a))) # ne history m^-3
rows=[]
for n in (128,256,512):
 o=LinearKompaneets(np.geomspace(1e-5,50.,n+1));psi=np.interp(np.log(o.x),np.log(xp),df/(fp*(1+fp)))
 N=o.cap*psi
 assert max(abs(o.m*psi/o.fp))<.01
 ref=o.energy_norm(N);scale=max(np.sum(abs(N)),1e-300)
 for y in (y0,1e-3,.01):
    q=o.advance(N,y);t=expm_multiply(o.matrix*y,N)
    number=float(abs(q.sum()-N.sum())/scale);energy=float((q-N)@o.x)
    err=float(np.sum(abs(q-t))/scale);ratio=o.energy_norm(q)/ref
    assert number<1e-11 and ratio<=1+1e-12 and err<1e-8
    assert min(o.fp+o.m*q/o.cap)>=0
    row=dict(n=n,y=y,number_defect=number,oracle_relative=err,entropy_ratio=ratio,energy_change_dimensionless=energy,relative_energy_change=float(energy/max(abs(N@o.x),1e-300)),max_fraction=float(max(abs(o.m*q/o.cap/o.fp))),lambda_min=float(o.eig[0]),lambda_max=float(o.eig[-1]))
    rows.append(row);print(row,flush=True)
    if y==.01:np.savez_compressed(D/f'komp_{n}.npz',x=o.x,initial=N,final=q,capacity=o.cap)
out=dict(status='SCOPED_LINEARIZED_KOMPANEETS',scope='fixed Te=Tgamma, actual signed FF input, reflecting finite x domain; conditional exposure y0 and manufactured larger y; not coupled live Compton',history_sha=hashlib.sha256(H.read_bytes()).hexdigest(),source_sha=hashlib.sha256(P.read_bytes()).hexdigest(),rows=rows,y0=y0)
(D/'KOMPANEETS.json').write_text(json.dumps(out,indent=2)+'\n')
