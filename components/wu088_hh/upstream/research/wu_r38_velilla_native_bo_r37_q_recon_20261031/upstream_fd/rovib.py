"""Native original diatomic H2 fit plus isotopic bare-nucleus Schrödinger dynamics.

Units are atomic: a0 and Hartree, m_e=1; c,hbar,kB retained in exported SI.
The fitted electronic h2(r) is obtained directly from EPAPS Fortran h3plus.f.
Diatomic v,J energies are from a Dirichlet finite-difference radial Hamiltonian
for a pair of bare nuclei with the specified reduced mass; this is not a complete
three-body SQM scattering calculation nor a fitted experimental isotope Q.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import minimize_scalar
from .native_pes import NativePES

MP = 1836.15267343   # electron-mass units, bare proton. CODATA-derived input
MD = 3670.48296788   # bare deuteron
EH_J = 4.3597447222071e-18
KB_J = 1.380649e-23
C_MPS = 299792458.
H_J_S = 6.62607015e-34
HC_CM = H_J_S*C_MPS*100.
K_PER_EH = EH_J/KB_J
CM_PER_EH = EH_J/HC_CM
MU_H2 = MP/2
MU_HD = MP*MD/(MP+MD)

@dataclass(frozen=True)
class RadialGrid:
    r_min: float = 0.50
    r_max: float = 16.00
    step: float = 0.0050
    def internal(self) -> np.ndarray:
        return np.arange(self.r_min+self.step, self.r_max, self.step, dtype=float)


def energy_levels(pes: NativePES, mu: float, Js: range, vibrational_count: int=2, grid: RadialGrid=RadialGrid()):
    r=grid.internal(); dr=grid.step
    potential=np.array([pes.h2(float(x)) for x in r],dtype=float)
    kinetic=1/(2*mu*dr*dr)
    off=-kinetic*np.ones(len(r)-1)
    out={}
    for J in Js:
        diag=2*kinetic+potential + J*(J+1)/(2*mu*r*r)
        eig=eigh_tridiagonal(diag,off,select="i",select_range=(0,vibrational_count-1),eigvals_only=True,check_finite=True)
        for v,value in enumerate(eig):out[(v,J)]=float(value)
    return out


def source_minima(pes:NativePES):
    m=minimize_scalar(lambda x:pes.dimh3p(x,x,x)[0],bounds=(1.50,1.80),method='bounded',options={'xatol':1e-12})
    h=minimize_scalar(pes.h2,bounds=(1.25,1.55),method='bounded',options={'xatol':1e-13})
    return {'equilateral_r_a0':float(m.x),'equilateral_Eh':float(m.fun),'h2_equilibrium_r_a0':float(h.x),'h2_equilibrium_Eh':float(h.fun),'electronic_dissociation_D_e_cm1':float((h.fun-m.fun)*CM_PER_EH)}


def channels(hd,h2):
    rows=[]
    for (v,j),Ei in sorted(hd.items()):
        if v>1 or (v==1 and j>6) or (v==0 and j>11): continue
        for jp in range(10):
            Ef=h2[(0,jp)]
            # Initial = H+ + HD(v,j); final = D+ + H2(v'=0,j')
            # Source BO PES common to isotope channels. Positive delta means endothermic.
            delta=Ef-Ei
            rows.append({'initial_v':v,'initial_J':j,'product_v':0,'product_J':jp,
                'E_HD_Eh':Ei,'E_H2_Eh':Ef,'delta_E_Eh':delta,'threshold_K':max(delta,0)*K_PER_EH,
                'Q_release_J':-delta*EH_J,'delta_E_cm1':delta*CM_PER_EH,'channel_exothermic':delta<0})
    return rows
