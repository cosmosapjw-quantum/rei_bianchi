#!/usr/bin/env python3
"""Why exact recurrence identities do not license an unstable wide-strip fast path."""
from pathlib import Path
import argparse,ctypes as ct,json,sys
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_native import build

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    lib=ct.CDLL(build()['libraries']['reference']['path'])
    f=lib.fg_boys;f.argtypes=[ct.c_size_t,ct.c_void_p,ct.c_size_t,ct.c_void_p,ct.c_size_t];f.restype=ct.c_int
    mp.mp.dps=80;rows=[]
    for imag in [8,16,24,32]:
        x=np.array([complex(0,imag)],dtype=np.clongdouble);vals=np.empty(10,np.clongdouble)
        if f(1,x.ctypes.data,2,vals.ctypes.data,20):raise RuntimeError('reference Boys evaluation failed')
        y=vals[9];E=np.exp(-x[0])
        for j in range(8,-1,-1):y=(np.longdouble(2)*x[0]*y+E)/np.longdouble(2*j+1)
        oracle=mp.hyp1f1(mp.mpf('0.5'),mp.mpf('1.5'),-mp.mpc(0,imag))
        def err(z):return float(abs(mp.mpc(str(z.real),str(z.imag))-oracle))
        gain=abs((2*mp.mpc(0,imag))**9/mp.fac2(17))
        rows.append(dict(x_real=0,x_imag=imag,reference_F0_absolute_error=err(vals[0]),
            seed9_downward_F0_absolute_error=err(y),seed_error_amplification=float(gain)))
    result=dict(schema='WU088_BOYS_UNSTABLE_OPTIMIZATION_COUNTEREXAMPLE_V1',rows=rows,mpmath_version=mp.__version__,
                decision='REJECT_SINGLE_ORDER9_SEED_IN_WIDE_COMPLEX_STRIP',production_mutation=False,
                note='Controlled scalar-domain counterexample; not a physical H error estimate.')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as fp:json.dump(result,fp,indent=2);fp.write('\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
