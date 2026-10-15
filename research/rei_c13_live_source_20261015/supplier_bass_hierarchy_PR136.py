"""BASS-moment-normalized Einstein-Boltzmann quadrupole intake for REI.

Reuses already defined BASS collisionless hierarchy:
  bianchi/matter/hierarchy.py Lewis-Challinor J^(i)_{A_l},
  htt/bass/hierarchy/pstf_radiation.py I2_to_pi_gamma=1,
  BASS Dossier II: kinetic characteristics with physical-second convention.

Independent positive initial axisymmetric l=2 occupations:
  W_r(mu*)=1+A_r P2(mu*),  W_m(mu*)=1+A_m P2(mu*).
W is normalized to <W>=1 and nonnegative for -1<=A<=2. The seed
quadrupoles are independent of initial shear, so Sigma=0 with A!=0
can dynamically generate shear via Einstein's source.

Radiation and nonrel matter stress use exact invariant-momentum f0
characteristics, not an unadmitted l=2 time-truncation. BASS hierarchy
is independently evaluated as a source-identified moment/RHS oracle.

Not claimed: massive relativistic radial hierarchy evolved along time;
full Thomson polarization collision or native REI ionization history.
"""
from __future__ import annotations
import math
import numpy as np
from sigma_pi_coupled import SigmaPiDynamics,RadiationKillingGL


def p2(mu2):
    return .5*(3*np.asarray(mu2,dtype=float)-1.)


def check_initial_quadrupole(amplitude):
    amplitude=float(amplitude)
    if not math.isfinite(amplitude) or not(-1.<=amplitude<=2.):
        raise ValueError("BASS P2 positive f requires -1<=A<=2")
    return amplitude


def bass_hierarchy_scalar_shear_coefficient(j1,j2):
    """BASS Lewis-Challinor Eq12 l=2,i=0 at isotropic initial f.

    Initial J2=J4=0 but the source is (2/15)(J^(2)-5J^(1))*sigma.
    Ultrarelativistic: J1=J2=rho -> -8*rho/15.
    Nonrel: J1=3p, J2/J1->0 -> -2p.
    """
    if not (math.isfinite(j1) and math.isfinite(j2) and j1>=0 and j2>=0):
        raise ValueError("BASS scalar kinetic moments must be physical")
    return (2./15.)*(j2-5*j1)


class BASSQuadrupoleTransport(SigmaPiDynamics):
    """Previous Einstein solver with independent positive radiation/matter I2.

    The entire angular hierarchy is implicit in exact f0 characteristics.
    Matter is the cold nonrel Maxwellian radial approximation.
    """

    def __init__(self,model,*,sigma_ref,orientation,
                 source_rad_amplitude=0.,source_matter_amplitude=0.,
                 angular_n=64,geometry="einstein_stress"):
        self.ar=check_initial_quadrupole(source_rad_amplitude)
        self.am=check_initial_quadrupole(source_matter_amplitude)
        self._ang=RadiationKillingGL(angular_n)
        self._q2=p2(self._ang.mu2)
        self._wr=1+self.ar*self._q2
        if np.min(self._wr)<-1e-13 or abs(np.dot(self._ang.w,self._wr)-1)>1e-13:
            raise ValueError("BASS radiation source angle normalization failed")
        self._matter_ppar0=1+2*self.am/5.
        self._matter_pperp0=1-self.am/5.
        if self._matter_ppar0<0 or self._matter_pperp0<0:
            raise ValueError("BASS matter angular population not positive")
        super().__init__(model,sigma_ref=sigma_ref,orientation=orientation,
                         closure="collisionless_matter",
                         geometry=geometry,n_mu=angular_n)

    def radiation_normalized(self,b:float):
        """Return energy and pressure ratios to isotropic reference epsilon.

        E0 scale a^-4 from exact positive weighted Killing angular moment.
        At b=0 exactly initial Pi/epsilon=A_r/5.
        """
        if not math.isfinite(b) or abs(b)>30:
            raise ValueError("radiation log-axis outside validated domain")
        if b==0.:
            return 1.,self.ar/5.,(1./3.+2*self.ar/15.),(
                   1./3.-self.ar/15.)
        ep=math.exp(2*b);ez=math.exp(-4*b)
        mu2=self._ang.mu2
        R=np.sqrt(ep*(1-mu2)+ez*mu2)
        wm=self._ang.w*self._wr
        Er=math.fsum((wm*R).tolist())
        par=math.fsum((wm*ez*mu2/R).tolist())
        perp=.5*math.fsum((wm*ep*(1-mu2)/R).tolist())
        if abs(Er-par-2*perp)>2e-13*max(Er,1):
            raise ArithmeticError("BASS massless PSTF quadrupole trace")
        return Er,par-perp,par,perp

    def moments(self,eta,b):
        ep=self.model.radiation_energy_ref*math.exp(-4*eta)
        m,Pi,par,perp=self.radiation_normalized(b)
        return ep*m,ep*Pi,ep*(m-1.),(ep*par,ep*perp)

    def matter(self,eta,b):
        """Exact anisotropic nonrel thermal second moment for frozen f0."""
        p=self.model.gas_pressure_ref*math.exp(-5*eta)
        par=p*self._matter_ppar0*math.exp(-4*b)
        perp=p*self._matter_pperp0*math.exp(2*b)
        return .5*(2*perp+par),par-perp,(2*perp+par)/3.

    def hierarchy_linearized_pi(self,eta,b):
        """BASS l=2 linear moment hierarchy as independent diagnostic.

        Radiation: d(Pi_r/eps_r_iso)/d(ln a)=-(8/5)db/d(ln a).
        Nonrel matter: d(Pi_m/p_m_iso)/d(ln a)=-6db/d(ln a).
        Hence Pi_r/eps_iso=A_r/5-(8/5)b and
              Pi_m/p_iso=3A_m/5-6b.

        Source gamma/pi terms O(b*A,b^2), generated l=4, collision
        and polarization terms are deliberately *omitted*. This is
        NEVER fed back into the exact Einstein solver.
        """
        if not (math.isfinite(eta) and math.isfinite(b)):
            raise ValueError("finite hierarchy diagnostic state")
        rad=self.model.radiation_energy_ref*math.exp(-4*eta)
        mat=self.model.gas_pressure_ref*math.exp(-5*eta)
        return (rad*(self.ar/5.-8*b/5.),
                mat*(3*self.am/5.-6*b))

    def source_identity(self):
        return {
            "BASS_radiation_I2_to_pi":"1.0, htt/bass/hierarchy/pstf_radiation.py",
            "BASS_massive_J2_pi":"pi_ab=J^(0)_ab, bianchi/matter/hierarchy.py",
            "BASS_l2_source":"(2/15)*(J^(2)-5*J^(1))*sigma_ab",
            "amplitude_rad":self.ar,"amplitude_matter":self.am,
            "angular_nodes":len(self._ang.w)*2,
            "closure":"source P2 collisionless f0 + nonrel thermal massive limit",
        }

    def angular_batch(self,bvals):
        """Memory-bounded positive-half GL64 NumPy batch."""
        bvals=np.asarray(bvals,dtype=float)
        if bvals.ndim!=1 or not np.all(np.isfinite(bvals)) or np.any(np.abs(bvals)>30):
            raise ValueError("finite vector input in validated b domain")
        output=np.empty((len(bvals),2),dtype=float)
        mu2=self._ang.mu2
        w=self._ang.w*self._wr
        for start in range(0,len(bvals),1024):
            b=bvals[start:start+1024,None]
            ep=np.exp(2*b);ez=np.exp(-4*b)
            rr=np.sqrt(ep*(1-mu2)+ez*mu2)
            output[start:start+1024,0]=rr@w
            output[start:start+1024,1]=(
                (ez*mu2/rr-.5*ep*(1-mu2)/rr)@w
            )
        return output
