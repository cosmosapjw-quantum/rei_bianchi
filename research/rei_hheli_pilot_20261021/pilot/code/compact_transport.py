"""Exact reflection-even subspace of the source-pinned LRS FV hierarchy.

The finite angular cutoff and FV quadrature are explicit configuration values.
Only odd multipoles and the identically zero gas-energy placeholder are removed.
All four even energy/number towers are retained. Atomic electrons enter via the
proper density argument, never by modifying the massive nonbaryonic distribution.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

UNIT = Path(__file__).resolve().parents[1]
VENDOR = UNIT / "vendor"


@lru_cache(maxsize=1)
def verify_vendor():
    data = json.loads((UNIT/"evidence/BASELINE_MANIFEST.json").read_text())
    for path, expected in data["files"].items():
        if hashlib.sha256((UNIT/path).read_bytes()).hexdigest() != expected:
            raise RuntimeError("pinned baseline changed: " + path)
    return data


verify_vendor()
for _name in ("canonical_fv", "species_hierarchy", "lrs_boltzmann", "prepared_moments"):
    if _name in sys.modules and Path(sys.modules[_name].__file__).resolve() != VENDOR/(_name+".py"):
        raise RuntimeError("shadowed baseline module: " + _name)
sys.path.insert(0, str(VENDOR))
from canonical_fv import CanonicalMomentumFV
from prepared_moments import PreparedCanonicalMoments
from lrs_boltzmann import SourceLock, GAMMA_PER_NE
from scipy.constants import sigma as STEFAN_BOLTZMANN

C = 299792458.
G = 6.67430e-11
KAPPA_T = 8*math.pi*G/C**2
SQRT6 = math.sqrt(6.)


@lru_cache(maxsize=32)
def even_operator(ellmax: int, power: int):
    """Analytic Legendre adjoint, with rational coefficients before binary64.

    L*_p P_l = -3 l mu P_(l-1) + 3(l+3-p) mu² P_l + (p-3)P_l.
    This exposes exact parity, bandwidth two in the even index, and the
    N0'=0 / E0'=-2(s/H)E2 identities without quadrature roundoff.
    """
    if not isinstance(ellmax, int) or ellmax%2 or not 2 <= ellmax <= 32 or power not in (3,4):
        raise ValueError("even ellmax 2..32 and power 3 or 4 required")
    n = ellmax//2+1
    mat = np.zeros((n,n))
    for l in range(0,ellmax+1,2):
        plus = Q((l+1)*(l+2),(2*l+1)*(2*l+3))
        diag = Q((l+1)**2,(2*l+1)*(2*l+3))
        if l:
            diag += Q(l*l,(2*l+1)*(2*l-1))
        fac = 3*(l+3-power)
        mat[l//2,l//2] = float(fac*diag + power-3 - (Q(3*l*l,2*l-1) if l else 0))
        if l+2 <= ellmax:
            mat[l//2,l//2+1] = float(fac*plus)
        if l >= 2:
            minus = Q(l*(l-1),(2*l+1)*(2*l-1))
            mat[l//2,l//2-1] = float(fac*minus-Q(3*l*(l-1),2*l-1))
    return np.frombuffer(mat.tobytes(), dtype=np.float64).reshape(mat.shape)


@lru_cache(maxsize=1)
def cosmology():
    return json.loads((VENDOR/"REI_BACKGROUND_FAMILY_LOCK.json").read_text())["cosmology"]


def source(z_end=2.):
    c = cosmology()
    return SourceLock(c["H0_per_s"],c["Omega_m"],c["Omega_r"],c["Omega_lambda"],1/21.,1/(1+z_end))


@lru_cache(maxsize=32)
def unit_matter_pi(radial_cells=24,angular_cells=12,gauss_order=3,mass=30.):
    return CanonicalMomentumFV(mass,1.,radial_cells,angular_cells,gauss_order).moments(0.,0.).pi_s


class CompactTransport:
    def __init__(self, sigma, pm, pr, *, ellmax=8, radial_cells=24,
                 angular_cells=12, gauss_order=3, z_end=2., mass_fraction=.1,
                 mass_over_Tref=30., orientation=1):
        self.source = source(z_end)
        self.ellmax = ellmax
        self.n = ellmax//2+1
        self.size = 3+4*self.n
        self.energy = even_operator(ellmax,4)
        self.number = even_operator(ellmax,3)
        self.damp = np.ones(self.n); self.damp[0]=0.; self.damp[1]=.9
        self.fm = mass_fraction
        self.omega_b = cosmology()["Omega_b"]
        if not (0 <= sigma < math.sqrt(6.) and orientation in (-1,1)
                and 0 < self.fm < 1-self.omega_b/self.source.omega_m):
            raise ValueError("positive density, physical Sigma, nonbaryonic mass fraction required")
        self.sigma, self.pm, self.pr = float(sigma),float(pm),float(pr)
        self.q0 = orientation*sigma/math.sqrt(6-sigma*sigma)
        hinit = self.source.href*math.sqrt(1+self.q0*self.q0)
        mass_pref = self.source.omega_m*self.fm/self.source.aref**3
        cm = KAPPA_T*SQRT6*self.source.rhocrit_j_m3*mass_pref*unit_matter_pi(
            radial_cells,angular_cells,gauss_order,mass_over_Tref)/hinit**2
        fr = self.source.h0**2*self.source.omega_r/(self.source.aref**4*self.source.href**2)
        self.am = pm/cm
        self.ar = 5*pr*(1+self.q0*self.q0)/(SQRT6*fr)
        if not (-1 <= self.am <= 2 and -1 <= self.ar <= 2):
            raise ValueError(f"nonnegative initial W requires -1<=A<=2: Am={self.am}, Ar={self.ar}")
        original = CanonicalMomentumFV(mass_over_Tref,self.am,radial_cells,angular_cells,gauss_order)
        self.moments = PreparedCanonicalMoments(original)
        self.mass_pref = mass_pref
        self.dust_omega = self.source.omega_m*(1-self.fm)
        self.omega_gamma = 4*STEFAN_BOLTZMANN/C*2.7255**4/self.source.rhocrit_j_m3
        self.omega_nu = self.source.omega_r-self.omega_gamma
        if self.omega_nu <= 0:
            raise ValueError("source radiation partition invalid")

    def initial_state(self):
        y = np.zeros(self.size)
        y[2]=self.q0
        a=y[3:].reshape(4,self.n)
        a[:,0]=1.; a[:,1]=self.ar/5
        return y

    def unpack_full(self, y):
        """Reconstruct the original 4+4*(L+1) state, exact odd zeros and u=0."""
        out = np.zeros(4+4*(self.ellmax+1))
        out[:3]=np.asarray(y)[:3]
        out[4:].reshape(4,self.ellmax+1)[:,::2]=np.asarray(y)[3:self.size].reshape(4,self.n)
        return out

    def pack_full(self,y):
        a=np.asarray(y)
        if a.shape != (4+4*(self.ellmax+1),) or a[3] != 0 or np.any(a[4:].reshape(4,-1)[:,1::2] != 0):
            raise ValueError("full state is outside exact reflection-even/u=0 subspace")
        return np.r_[a[:3],a[4:].reshape(4,-1)[:,::2].ravel()]

    def geometry(self,x,y):
        a=self.source.aref*math.exp(x)
        b=float(y[1]); s=float(y[2])*self.source.href
        tower=np.asarray(y)[3:self.size].reshape(4,self.n)
        eg,ng,en,nn=tower
        m=self.moments.moments(float(x),b)
        inva4=a**-4
        rad=(self.omega_gamma*eg[0]+self.omega_nu*en[0])*inva4
        h2=self.source.h0**2*(self.dust_omega/a**3+self.mass_pref*m.rho+rad+self.source.omega_lambda)+s*s
        if h2 <= 0 or eg[0] <= 0 or en[0] <= 0 or not math.isfinite(h2):
            raise FloatingPointError("nonpositive Einstein/radiation state")
        h=math.sqrt(h2)
        pm=self.mass_pref*m.pi_s
        pg=self.omega_gamma*inva4*eg[1]/3
        pn=self.omega_nu*inva4*en[1]/3
        return a,h,s,pm,pg,pn,tower,m

    def rhs(self,x,y,ne_cm3=0., *, with_geometry=False):
        geom=self.geometry(x,y)
        a,h,s,pm,pg,pn,tower,m=geom
        v=s/h; g=GAMMA_PER_NE*ne_cm3/h
        derivative=np.empty(self.size)
        derivative[:3]=(self.source.href/h,v,-3*y[2]+3*self.source.h0**2/(self.source.href*h)*(pm+pg+pn))
        d=derivative[3:].reshape(4,self.n)
        d[0]=v*(self.energy@tower[0])-g*self.damp*tower[0]
        d[1]=v*(self.number@tower[1])-g*self.damp*tower[1]
        d[2]=v*(self.energy@tower[2])
        d[3]=v*(self.number@tower[3])
        return (derivative,geom) if with_geometry else derivative

    def observables(self,x,y,ne_cm3=0.,tau=0.):
        a,h,s,pm,pg,pn,tower,m=self.geometry(x,y)
        factor=KAPPA_T*SQRT6*self.source.rhocrit_j_m3/h**2
        pm*=factor; pg*=factor; pn*=factor; pr=pg+pn
        return dict(eta=float(x),a=a,z=1/a-1,elapsed_s=float(y[0])/self.source.href,
            H_per_s=h,signed_Sigma=SQRT6*s/h,Sigma_F=SQRT6*abs(s)/h,
            P_m=pm,P_gamma=pg,P_nu=pn,P_r=pr,Pi_m=abs(pm),Pi_r=abs(pr),
            Pi_total=abs(pm+pr),ne_cm3=ne_cm3,tau_T=tau,b=float(y[1]),
            N_gamma_0=float(tower[1,0]),N_nu_0=float(tower[3,0]),
            matter_number_comoving=m.ncell_number*math.exp(3*x),
            min_canonical_cell=m.min_cell_number)

    def brightness_min(self,y,angles=128):
        from numpy.polynomial.legendre import legval
        mu=np.linspace(-1,1,angles)
        towers=np.asarray(y)[3:self.size].reshape(4,self.n)
        minima=[]
        for values in towers:
            coeff=np.zeros(self.ellmax+1)
            coeff[::2]=(4*np.arange(self.n)+1)*values
            minima.append(float(np.min(legval(mu,coeff))))
        return min(minima)
