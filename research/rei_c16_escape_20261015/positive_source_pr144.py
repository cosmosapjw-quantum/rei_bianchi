#!/usr/bin/env python3
"""Exact PR144 positive Moment and constructive three-atom source projection.

Original immutable PR144 qmu.py committed f85394d5; only runtime
imports are adapted to compatible C13 photon type. Source function body
below is byte copied unchanged from that PR's class through next function.
"""
from dataclasses import dataclass
from pathlib import Path
import math
import numpy as np
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"research/rei_c13_live_source_20261015"))
import short_interval as c13

@dataclass(frozen=True)
class Moment:
    """Energy U, longitudinal c*p, Pi=Pparallel-Pperp (all eV per H)."""
    U:float
    cPz:float
    Pi:float

    @classmethod
    def from_sky(cls,photons):
        photons.check()
        w=photons.NperH*photons.E
        return cls(float(w.sum()),float(w@photons.mu),
                   float(w@(.5*(3*photons.mu**2-1))))

    def positive_cone(self,tol=5e-14):
        if not all(math.isfinite(x) for x in (self.U,self.cPz,self.Pi)):
            return False
        if self.U<0:return False
        if self.U==0:return self.cPz==0 and self.Pi==0
        return (-self.U/2-tol*self.U<=self.Pi<=self.U*(1+tol)
                and 3*self.cPz**2<=self.U*(self.U+2*self.Pi)+tol*self.U**2)


def positive_three_atom(moment:Moment,energy_eV=30.):
    """Sharp constructive Hausdorff [mu=-1,1] moment realization.

    m=<mu>=cPz/U; v=<mu²>=(U+2Pi)/(3U);  m²<=v<=1.
    lambda=(v-m²)/(1-m²). Mass at +/-1 is lambda*(1+/-m)/2,
    remainder 1-lambda sits at mu=m. E chosen for counterexample ONLY.
    This is NOT a licensed Case-A physical photon emission spectrum.
    """
    if (not moment.positive_cone(tol=1e-13) or
        not math.isfinite(energy_eV) or energy_eV<=0):
        raise ValueError("NONREALIZABLE_QMU_OR_PHOTON_ENERGY")
    if moment.U==0:return c13.PhotonCloud.empty()
    U=moment.U;m=moment.cPz/U;v=(U+2*moment.Pi)/(3*U)
    if abs(m)>=1-1e-14:
        if abs(v-1)>2e-13:raise ValueError("NO_ONE_POLE_LIMIT")
        return c13.PhotonCloud(np.array([energy_eV]),
              np.array([1. if m>=0 else -1.]),np.array([U/energy_eV]))
    lam=(v-m*m)/(1-m*m)
    if not -1e-13<=lam<=1+1e-13:
        raise ValueError("NEGATIVE_CONSTRUCTED_QUADRATURE")
    lam=min(1.,max(0.,lam))
    E=np.full(3,energy_eV)
    mus=np.array([-1.,1.,m])
    weights=U*np.array([lam*(1-m)/2,lam*(1+m)/2,1-lam])/energy_eV
    sky=c13.PhotonCloud(E,mus,weights)
    check=Moment.from_sky(sky)
    if max(abs(check.U-U),abs(check.cPz-moment.cPz),
           abs(check.Pi-moment.Pi))>1e-11*U:
        raise ArithmeticError("POSITIVE_RECONSTRUCTION_NOT_MOMENT_EXACT")
    return sky


# End of byte-identical original PR144 moment constructor; only import header adapted.
