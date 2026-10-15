"""Exact positive pairwise angular-jump semigroup + partner four-momentum ledger.

This C5 source-owning implementation connects PR145's nonnegative canonical
momentum cells to an *explicitly conditional* angular jump generator

  d N(q_i,mu_j)/d tau =
       W_j sum_k N(q_i,mu_k) - N(q_i,mu_j),

where tau is a supplied, dimensionless *integrated optical depth*, and W_j
are the positive normalized Gauss-cell angular measure weights.

At fixed eta,b the exact stochastic semigroup is
  N_new=exp(-tau) N_old + (1-exp(-tau)) W_j N_shell.
Hence (i) each canonical radial shell's number is conserved, (ii)
N_new>=0, (iii) entropy D(N/N_shell||W) does not increase, (iv) the
event has a well-defined partner gas energy and momentum impulse
Q_m^a+Q_g^a=0. The jump law has canonical angular detailed balance but
is NOT a physical H/He scattering cross section, not a Boltzmann rate
or true matter/baryon thermal equilibrium at b != 0. Never assume
the collision optical depth without its microscopic owner.

In non-tilted LRS P2-even sectors the z momentum flux cancels. An
asymmetric distribution requires a separate baryon bulk Euler owner;
this module fails closed rather than promote a spurious no-recoil model.

Physical massless photon/He recombination collisions and source reservoir
are *NOT* being re-solved; this is a single frozen-metric transaction.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss

from canonical_fv import CanonicalMomentumFV

C_SI=299792458.


@dataclass(frozen=True)
class CollisionMoments:
    energy_norm:float
    pbar_norm:float
    delta_pressure_norm:float
    moment_z_norm:float
    number_canonical:float


@dataclass(frozen=True)
class CollisionEvent:
    optical_depth:float
    component_energy_before_J_m3:float
    component_energy_after_J_m3:float
    gas_energy_before_J_m3:float
    gas_energy_after_J_m3:float
    massive_delta_energy_J_m3:float
    gas_delta_energy_J_m3:float
    massive_delta_zmomentum_J_m3_over_c:float
    gas_delta_zmomentum_J_m3_over_c:float
    count_before:float
    count_after:float
    max_radial_shell_count_abs_error:float
    relative_entropy_before:float
    relative_entropy_after:float
    Pi_m_before_J_m3:float
    Pi_m_after_J_m3:float
    status:str


class PositiveCanonicalAngularCollision:
    """Source-imposed finite-state Markov generator, no fitted rate owner.

    Source FV populations are immutable; each returned population is an
    independent read-only array. This avoids unintentionally mutating a
    previously committed accepted collision or changing initial PR145
    reference data.
    """
    def __init__(self, source:CanonicalMomentumFV,
                 massive_reference_energy_J_m3:float):
        if not isinstance(source,CanonicalMomentumFV):
            raise TypeError("requires actual positive PR145 FV source")
        if (not math.isfinite(massive_reference_energy_J_m3)
            or massive_reference_energy_J_m3<=0):
            raise ValueError("positive SI massive reference energy is required")
        self.source=source
        self.ref_energy=float(massive_reference_energy_J_m3)
        order=source.gauss_order
        z,w=leggauss(order)
        edges=np.linspace(-1.,1.,source.angular_cells+1)
        half=np.diff(edges)/2
        mu=(edges[:-1]+half)[:,None]+half[:,None]*z[None,:]
        wmu=(half[:,None]*w[None,:]/2).reshape(-1)
        if abs(float(np.sum(wmu))-1.)>1e-14:
            raise ArithmeticError("angular measure must normalize to one")
        nmu=mu.size
        if nmu!=source._numbers.shape[1]:
            raise ValueError("angular Gauss/owner source mismatch")
        self.mu=mu.reshape(-1)
        self.wmu=wmu
        self.q=source._q[:,0].copy()
        self.nq=source._numbers.shape[0]
        self.nmu=nmu
        for k in ("mu","wmu","q"):
            getattr(self,k).flags.writeable=False
        self.initial=source._numbers.copy()
        self.initial.flags.writeable=False
        self._initial_shell=self.initial.sum(axis=1)
        if not (np.isfinite(self.initial).all() and
                np.all(self.initial>=0)):
            raise ArithmeticError("negative source population")

    def populations(self):
        return self.initial.copy()

    def isotropic_target(self,populations):
        pop=np.asarray(populations,dtype=float)
        if pop.shape!=self.initial.shape or np.any(~np.isfinite(pop)) or np.any(pop<0):
            raise ValueError("invalid positive canonical phase-space source")
        return pop.sum(axis=1)[:,None]*self.wmu[None,:]

    def _validate_parity(self,pop):
        # Canonical momentum evenness must hold; without it a gas bulk
        # Euler velocity and recoil spatial momentum require new physics.
        err=np.max(abs(pop-pop[:,::-1]))
        scale=max(float(np.max(pop)),1e-200)
        if err>2e-13*scale:
            raise ValueError("odd momentum sector requires gas Euler owner")

    def moments(self,eta:float,b:float,populations)->CollisionMoments:
        if (not math.isfinite(eta) or eta<0
            or not math.isfinite(b) or abs(b)>1):
            raise ValueError("physical eta,b source outside domain")
        pop=np.asarray(populations,dtype=float)
        if pop.shape!=self.initial.shape or not np.isfinite(pop).all() or np.any(pop<0):
            raise ValueError("nonphysical phase populations")
        r=math.exp(-eta)
        pp2=(r*self.q[:,None])**2*math.exp(2*b)*(1-self.mu[None,:]**2)
        pz=(r*self.q[:,None])*math.exp(-2*b)*self.mu[None,:]
        pz2=pz*pz
        E=np.sqrt(self.source.mass**2+pp2+pz2)
        scale=r**3/self.source.reference_energy_norm
        en=scale*float(np.sum(pop*E))
        perp=scale*float(np.sum(pop*pp2/(2*E)))
        para=scale*float(np.sum(pop*pz2/E))
        pz_density=scale*float(np.sum(pop*pz))
        return CollisionMoments(en,(2*perp+para)/3,para-perp,
                                pz_density,float(np.sum(pop)))

    def relative_entropy(self,populations):
        pop=np.asarray(populations,dtype=float)
        target=self.isotropic_target(pop)
        mask=pop>0
        # D is unnormalized in n_shell, but decreases under every Markov
        # semigroup step because each shell's mass is conserved.
        result=float(np.sum(pop[mask]*np.log(pop[mask]/target[mask])))
        return max(result,0.) if result>-1e-15 else result

    def source_rhs(self,populations):
        """dN/dtau, with no physical collision frequency assumed."""
        arr=np.asarray(populations,dtype=float)
        self._validate_parity(arr)
        return self.isotropic_target(arr)-arr

    def event(self,eta:float,b:float,optical_depth:float,
              population,gas_energy_J_m3:float,
              gas_momentum_z_J_m3_over_c:float=0.):
        """Committed exact Markov step at FIXED metric and η.

        Q^0_m = Delta(energy density) in the normal tetrad and
        Q^z_m = c*Delta(momentum density), so gas Q^a_g=-Q^a_m.
        We expose a finite event impulse, not a per-second rate.
        """
        if not (math.isfinite(optical_depth) and 0<=optical_depth<=1000):
            raise ValueError("source-owned nonnegative finite optical depth")
        if not (math.isfinite(gas_energy_J_m3) and gas_energy_J_m3>=0
                and math.isfinite(gas_momentum_z_J_m3_over_c)):
            raise ValueError("finite nonnegative partner thermal energy")
        arr=np.asarray(population,dtype=float)
        target=self.isotropic_target(arr)
        self._validate_parity(arr)
        before=self.moments(eta,b,arr)
        H0=self.relative_entropy(arr)
        alpha=-math.expm1(-optical_depth)
        out=np.maximum(arr+alpha*(target-arr),0.)
        after=self.moments(eta,b,out)
        H1=self.relative_entropy(out)

        # Stable event impulses: use the transition flux, not subtraction
        # of two much larger cosmic rest-energy densities.
        delta_pop=out-arr
        r=math.exp(-eta)
        pp2=(r*self.q[:,None])**2*math.exp(2*b)*(1-self.mu[None,:]**2)
        pz=(r*self.q[:,None])*math.exp(-2*b)*self.mu[None,:]
        E=np.sqrt(self.source.mass**2+pp2+pz*pz)
        factor=self.ref_energy*r**3/self.source.reference_energy_norm
        delta_energy=factor*float(np.sum(delta_pop*E))
        delta_zmomentum=factor/C_SI*float(np.sum(delta_pop*pz))
        if b==0.:
            # Angular redistribution at fixed magnitude has exactly
            # no mass-shell energy exchange, not merely 1e-12 agreement.
            delta_energy=0.
        gas_after=gas_energy_J_m3-delta_energy
        if gas_after < 0:
            # No silent clipping: even a tiny unassigned deficit breaks
            # exact finite-event energy accounting.
            raise ValueError(
                "partner gas thermal energy insufficient for source-owned collision; "
                "do not silently borrow rest-mass or unowned stellar energy")
        shell=np.max(abs(out.sum(axis=1)-arr.sum(axis=1)))
        scale=max(float(np.sum(arr)),1e-200)
        if shell>3e-14*scale:
            raise ArithmeticError("canonical radial-shell particle count leakage")
        if H1>H0+3e-12*scale:
            raise ArithmeticError("canonical relative entropy increased")
        # For parity-symmetric source Qz should vanish up to f64 roundoff;
        # any true directed momentum needs a separate dynamical gas Euler.
        if abs(delta_zmomentum)>3e-12*factor*max(float(np.sum(arr*self.q[:,None])),1e-200)/C_SI:
            raise ArithmeticError("unexpected nonzero directed momentum")
        result=CollisionEvent(
            optical_depth=optical_depth,
            component_energy_before_J_m3=self.ref_energy*before.energy_norm,
            component_energy_after_J_m3=self.ref_energy*after.energy_norm,
            gas_energy_before_J_m3=gas_energy_J_m3,
            gas_energy_after_J_m3=gas_after,
            massive_delta_energy_J_m3=delta_energy,
            gas_delta_energy_J_m3=-delta_energy,
            massive_delta_zmomentum_J_m3_over_c=delta_zmomentum,
            gas_delta_zmomentum_J_m3_over_c=-delta_zmomentum,
            count_before=before.number_canonical,
            count_after=after.number_canonical,
            max_radial_shell_count_abs_error=float(shell),
            relative_entropy_before=H0,
            relative_entropy_after=H1,
            Pi_m_before_J_m3=self.ref_energy*before.delta_pressure_norm/3,
            Pi_m_after_J_m3=self.ref_energy*after.delta_pressure_norm/3,
            status="SCOPED_CONDITIONAL_PAIR_4MOMENTUM_CONSISTENCY"
        )
        out.flags.writeable=False
        return out,result
