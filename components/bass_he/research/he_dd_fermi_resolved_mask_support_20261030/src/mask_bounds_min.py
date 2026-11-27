"""Measured Fermi mask × EXFOR reported-SIG, positive-spectrum support bound.
This is NOT a physical event rate or heat. Requires pinned PR117 source files.
"""
import hashlib, json, math
from fractions import Fraction as F
from pathlib import Path

FERMI_SHA='a78ced8234a7eb104a5f5b406a6bc609591ec2c323a26008625b239b5dccc0e5'
EXFOR_SHA='2e14076cffe194bfa87ebb61748cf13ed095bd93139d1018ffc13cfdf23de559'
E=(F(201),F(225),F(253),F(285),F(320),F(359))
Q=F('23.84647820')
OMEGA_H=4*math.pi*(1-math.sin(math.pi/9))


def read(root:Path):
    raw=(root/'data/fermi_igrb_2015_AB_C_78row_mirror.csv').read_bytes()
    ex=(root/'data/exfor_M0475_SIG6.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=FERMI_SHA or hashlib.sha256(ex).hexdigest()!=EXFOR_SHA:
        raise ValueError('ORIGINAL_SOURCE_IDENTITY_MISMATCH')
    rows=[x.split() for x in raw.decode('ascii').splitlines() if x.startswith(('A ','B ','C '))]
    if len(rows)!=78 or [sum(x[0]==m for x in rows) for m in 'ABC']!=[26]*3:
        raise ValueError('ORIGINAL_FERMI_RECORD_GRAIN')
    data={}
    for m in 'ABC':
        b=[z for z in rows if z[0]==m and z[1] in ('200.0','282.8')]
        if len(b)!=2 or [(F(z[1]),F(z[2])) for z in b]!=[(F(200),F('282.8')),(F('282.8'),F(400))]:
            raise ValueError('ORIGINAL_BIN_EDGES')
        data[m]=b
    exj=json.loads(ex)
    if exj['raw_source_git_blob']!='c49433293921dbb012d7f1b0387745732a598efa':
        raise ValueError('WRONG_EXFOR_ORIGINAL')
    if tuple(F(z[0]) for z in exj['rows'])!=E:raise ValueError('EXFOR_ENERGY_KNOTS')
    sig=[F(z[1]) for z in exj['rows']]
    if any(s<0 for s in sig):raise ValueError('NEGATIVE_SIG')
    return data,sig


def flat_mean(lo,hi,sig):
    integ=F(0)
    for j in range(5):
        a=max(lo,E[j]);b=min(hi,E[j+1]);
        if a>=b:continue
        slope=(sig[j+1]-sig[j])/(E[j+1]-E[j]);inter=sig[j]-slope*E[j]
        integ+=slope*(b*b-a*a)/2+inter*(b-a)
    return integ/(hi-lo)


def compute(root:Path):
    data,sig=read(root)
    out=[]
    for m in 'ABC':
        for category,col,omega in [('IGRB',3,4*math.pi),('EGB',8,4*math.pi)]+([('resolved_highlat',13,OMEGA_H)] if m=='A' else []):
            bins=data[m]
            if category=='resolved_highlat' and any(data[other][i][col]!=bins[i][col] for other in 'BC' for i in (0,1)):
                raise ValueError('RESOLVED_MIRROR_NOT_REPEATED')
            flux=[F(z[col]) for z in bins]
            flat=sum((flux[i]*flat_mean(F(z[1]),F(z[2]),sig) for i,z in enumerate(bins)),F(0))
            upper=flux[0]*max(sig[0],sig[1],sig[2],sig[3])+flux[1]*max(sig[3:])
            if not 0<flat<=upper:raise ValueError('INVALID_BOUND')
            out.append({'model':m if category!='resolved_highlat' else 'common','component':category,
                        'Omega_sr':omega,'flat_s_inv_per_He':float(flat)*omega*1e-33,
                        'spectrum_shape_free_upper_s_inv_per_He':float(upper)*omega*1e-33,
                        'spectrum_shape_free_lower_s_inv_per_He':0.})
    return {'schema':'MASK_REPORTED_SIG_POSITIVE_SPECTRAL_ENVELOPE_V1','rows':out,
            'R_event':None,'heat_rate':None,'kappa':None,'L4':False,'production':'HOLD'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    a=p.parse_args();print(json.dumps(compute(a.root),indent=2))
