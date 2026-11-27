#!/usr/bin/env python3
"""Independent direct phi(min)*H(max) oracle for the small original-source case."""
import hashlib,json,sys,time
from pathlib import Path
import mpmath as mp
import numpy as np
UNIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(UNIT/'implementation'))
from original_source import decode_output,write_new

def main():
    root=UNIT/'verification/source_smoke'
    started=time.perf_counter();mp.mp.dps=70
    k=mp.mpf(7)/10;eta=-mp.mpf(10)/7
    value=decode_output(root/'U_SWEEP.bin')
    data=np.load(root/'GRID.npz',allow_pickle=False)
    r,w,force=data['r'],data['weights'],data['force']
    errors=[]
    for ell in range(value.shape[0]):
        fb=mp.coulombf(ell,eta,k*27);gb=mp.coulombg(ell,eta,k*27)
        hh=[];phi=[]
        for radius in r:
            ff=mp.coulombf(ell,eta,k*mp.mpf(float(radius)))
            gg=mp.coulombg(ell,eta,k*mp.mpf(float(radius)))
            hh.append((gg+1j*ff)/(gb+1j*fb))
            phi.append((gb*ff-fb*gg)/k)
        ref=[]
        for i in range(len(r)):
            ref.append(mp.fsum(phi[min(i,j)]*hh[max(i,j)]*mp.mpf(float(w[j]*force[ell,j]))
                               for j in range(len(r))))
        error=max(abs(mp.mpc(complex(x))-y) for x,y in zip(value[ell],ref))/max(map(abs,ref))
        errors.append(float(error))
    angular=[]
    for ell in (0,3):
        rr=mp.mpf('27.25')
        target=rr*mp.exp(-rr)*mp.sqrt(2*ell+1)*mp.quad(lambda mu:
            2*(1+1/mp.sqrt(rr**2+mp.mpf('.49')-mp.mpf('1.4')*rr*mu))*
            mp.exp(-2*mp.sqrt(rr**2+mp.mpf('.49')-mp.mpf('1.4')*rr*mu))*mp.legendre(ell,mu),[-1,1])
        got=force[ell,list(r).index(float(rr))]
        angular.append(float(abs(mp.mpf(float(got))-target)/abs(target)))
    assert max(errors)<3e-13
    assert max(angular)<3e-12
    report=dict(schema='PHYS73_INDEPENDENT_COULOMB_ORACLE_V1',status='PASS_SCOPED',
                method='70dps direct phi(min)*normalized_H(max), independent of ratio recurrence',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                channels=value.shape[0],nodes=len(r),dps=70,
                relative_errors=errors,angular_low_mode_relative_errors=angular,
                Coulomb_scalar_calls=2*value.shape[0]*(len(r)+1),
                direct_angular_quadratures=2,old_panel_integrations=0,
                continuum_quadrature_error_certified=False,
                wall_seconds=time.perf_counter()-started,HH_R10='OFF')
    write_new(UNIT/'verification/INDEPENDENT_COULOMB_ORACLE.json',report)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
