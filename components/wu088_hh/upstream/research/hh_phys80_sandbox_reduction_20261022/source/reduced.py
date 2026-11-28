"""Exact closed-energy coordinates for the pinned PHYS79 isolated subnetworks.

No QSS, clipping, source extrapolation, implicit signed-state extension, or
cosmological admission. Raw coordinates are (Q,v,h,l); solver coordinates
are (Q/(H+D),v/D,h,l), or v/D only for CX-only C02.
"""
from __future__ import annotations
import math
import numpy as np
from phys79_bridge import atomic, collisions

MODEL_ID = "PHYS80_EXACT_CONSERVATIVE_REDUCTION_STRICT_V1"
CV = 1.5 * collisions.KB_EV_K
IX = atomic.SPECIES_INDEX


def ci_value_derivative(row, temperature):
    """Same admitted value as parent, analytic temperature derivative."""
    value = collisions.ci_rate(row, temperature)
    de, p, _, x, k, _, _ = collisions.CI_FITS[row]
    u = de / (collisions.KB_EV_K * temperature)
    root = math.sqrt(u)
    log_derivative = (u-k+u/(x+u)-p*root/(2*(1+p*root))) / temperature
    return value, value * log_derivative


def cx_value_derivatives(temperature):
    kf, kr = collisions.d_cx_rates(temperature, "detailed_balance")
    t = temperature
    r1 = 2.06e-10*t**.396*math.exp(-33/t)
    r2 = 2.03e-9*t**(-.332)
    dkr = r1*(.396/t+33/t**2)-.332*r2/t
    dkf = math.exp(-43/t)*(dkr+kr*43/t**2)
    return kf, kr, dkf, dkr


class ExactReduction:
    def __init__(self, physics):
        self.physics = physics
        if (physics["H_per_s"] != 0 or physics["PI"] is not False or physics["RR"] is not False
                or physics["external_heat_bath"] is not False
                or physics["proper_volume_and_density"] != "fixed"
                or physics["gas_anisotropic_stress"] != 0
                or physics["d_cx"] is not True
                or physics["d_cx_closure"] != "detailed_balance"):
            raise ValueError("UNSUPPORTED_PHYSICAL_SUBNETWORK")
        self.ci_rows = tuple(physics["ci_rows"])
        if self.ci_rows not in ((), (0, 1, 3)):
            raise ValueError("ONLY_NEUTRAL_CI_OR_CX_ONLY_ADMITTED")
        self.only_cx = not self.ci_rows
        self.y0 = np.array(physics["initial_Y_per_H"], dtype=float)
        self.u0 = float(physics["initial_u_eV_per_H"])
        self.eps = np.array(physics["ionic_potential_eV"], dtype=float)
        if not np.array_equal(self.eps, collisions.ionic_potential_eV()):
            raise ValueError("GLOBAL_IONIC_POTENTIAL_MISMATCH")
        if (self.y0.shape != (atomic.N_SPECIES,) or not np.isfinite(self.y0).all()
                or np.any(self.y0 < 0) or not math.isfinite(self.u0) or self.u0 <= 0):
            raise ValueError("INVALID_INITIAL_STATE")
        forbidden = [i for i, s in enumerate(atomic.SPECIES)
                     if s.charge > 1 or s.isotope in ("T", "n")]
        if np.any(self.y0[forbidden] != 0):
            raise ValueError("NONZERO_HIGHER_CHARGE_OR_T_NEUTRON_UNSUPPORTED")
        totals = atomic.ISOTOPE_SUM@self.y0
        declared = physics["isotope_inventory_per_H"]
        if any(not math.isclose(float(a), float(declared[name]), rel_tol=5e-15, abs_tol=0)
               for a, name in zip(totals, atomic.ISOTOPES)):
            raise ValueError("INITIAL_INVENTORY_METADATA_MISMATCH")
        self.H = math.fsum(self.y0[[IX["H1_I"], IX["H1_II"]]])
        self.D = math.fsum(self.y0[[IX["D_I"], IX["D_II"]]])
        self.he_i = [IX["He3_I"], IX["He4_I"]]
        self.he_ii = [IX["He3_II"], IX["He4_II"]]
        self.li_i = [IX["Li6_I"], IX["Li7_I"]]
        self.li_ii = [IX["Li6_II"], IX["Li7_II"]]
        self.B = math.fsum(self.y0[self.he_i+self.he_ii])
        self.L = math.fsum(self.y0[self.li_i+self.li_ii])
        if min(self.H, self.D, self.B, self.L) <= 0:
            raise ValueError("POSITIVE_H_D_HE_LI_INVENTORIES_REQUIRED")
        self.S = self.H+self.D
        self.nuclei = math.fsum((self.H, self.D, self.B, self.L))
        self.q0 = np.array([
            math.fsum(self.y0[[IX["H1_II"], IX["D_II"]]]),
            self.y0[IX["D_II"]],
            math.fsum(self.y0[self.he_ii])/self.B,
            math.fsum(self.y0[self.li_ii])/self.L])
        if not (self.q0[2] < 1 and self.q0[3] < 1):
            raise ValueError("INITIAL_NEUTRAL_HE_LI_REQUIRED")
        self.he_lift = self.y0[self.he_i]/(1-self.q0[2])
        self.li_lift = self.y0[self.li_i]/(1-self.q0[3])
        self.scale4 = np.array([self.S, self.D, 1., 1.])
        self.active = np.array([1]) if self.only_cx else np.arange(4)
        self.IH = float(self.eps[IX["H1_II"]])
        self.delta = float(self.eps[IX["D_II"]]-self.eps[IX["H1_II"]])
        self.IHe = float(self.eps[IX["He4_II"]])
        self.ILi = float(self.eps[IX["Li7_II"]])
        self.bgrad = np.array([self.IH, self.delta, self.IHe*self.B, self.ILi*self.L])
        self.xgrad = np.array([1., 0., self.B, self.L])
        self.nH = float(physics["nH_cm3"])
        self.clock = float(physics["theta_per_proper_second"])
        if not (math.isfinite(self.nH) and self.nH > 0
                and math.isfinite(self.clock) and self.clock > 0):
            raise ValueError("INVALID_DENSITY_OR_CLOCK")
        if not math.isclose(self.clock, self.nH*physics["k_ref_cm3_s"], rel_tol=5e-15):
            raise ValueError("REFERENCE_CLOCK_MISMATCH")
        self.z0 = (self.q0/self.scale4)[self.active]
        self.network = collisions.CollisionNetwork(
            ci_rows=self.ci_rows, d_cx=True, d_cx_closure="detailed_balance")
        y, u, t, _, _ = self.state(self.z0)
        if not np.allclose(y, self.y0, rtol=5e-15, atol=0):
            raise ValueError("INITIAL_LIFT_MISMATCH")
        if not math.isclose(t, physics["T_initial_K"], rel_tol=5e-15):
            raise ValueError("INITIAL_THERMAL_CONTRACT_MISMATCH")
        self.network.rate_coefficients(t)

    def raw(self, z):
        z = np.asarray(z, dtype=float)
        if z.shape != (len(self.active),) or not np.isfinite(z).all():
            raise ValueError("INVALID_REDUCED_STATE")
        q = self.q0.copy()
        q[self.active] = z*self.scale4[self.active]
        return q

    def state(self, z):
        q = self.raw(z)
        Q, v, h, l = q
        if (min(Q-v, self.H-Q+v, v, self.D-v) < 0
                or not (0 <= h <= 1 and 0 <= l <= 1)):
            raise ValueError("STRICT_RAW_COORDINATE_GUARD")
        y = np.zeros(atomic.N_SPECIES)
        dv = v-self.q0[1]
        dhion = (Q-self.q0[0])-dv
        y[IX["H1_I"]] = self.y0[IX["H1_I"]]-dhion
        y[IX["H1_II"]] = self.y0[IX["H1_II"]]+dhion
        y[IX["D_I"]] = self.y0[IX["D_I"]]-dv
        y[IX["D_II"]] = self.y0[IX["D_II"]]+dv
        he_change = self.he_lift*(h-self.q0[2])
        li_change = self.li_lift*(l-self.q0[3])
        y[self.he_i] = self.y0[self.he_i]-he_change
        y[self.he_ii] = self.y0[self.he_ii]+he_change
        y[self.li_i] = self.y0[self.li_i]-li_change
        y[self.li_ii] = self.y0[self.li_ii]+li_change
        u = math.fsum([self.u0] + [-float(b)*float(d) for b, d in zip(self.bgrad, q-self.q0)])
        xe = math.fsum([Q, self.B*h, self.L*l])
        N = self.nuclei+xe
        if np.any(y < 0) or not np.isfinite(y).all() or not (u > 0 and N > 0):
            raise ValueError("STRICT_PHYSICAL_STATE_GUARD")
        temperature = u/(CV*N)
        if not math.isfinite(temperature) or temperature <= 0:
            raise ValueError("INVALID_REDUCED_TEMPERATURE")
        return y, u, temperature, xe, N

    def encode(self, y, u):
        y = np.asarray(y, dtype=float)
        if y.shape != self.y0.shape or not np.isfinite(y).all() or np.any(y < 0):
            raise ValueError("INVALID_FULL_STATE")
        q = np.array([y[IX["H1_II"]]+y[IX["D_II"]], y[IX["D_II"]],
                      math.fsum(y[self.he_ii])/self.B,
                      math.fsum(y[self.li_ii])/self.L])
        z = (q/self.scale4)[self.active]
        yl, ul, *_ = self.state(z)
        if not np.allclose(y, yl, rtol=2e-12, atol=0) or not math.isclose(u, ul, rel_tol=2e-12):
            raise ValueError("FULL_STATE_OUTSIDE_FIXED_INVARIANT_MANIFOLD")
        return z

    def _values(self, z):
        q = self.raw(z)
        _, _, t, xe, N = self.state(z)
        if self.only_cx:
            kh = khe = kli = dkh = dkhe = dkli = 0.
        else:
            kh, dkh = ci_value_derivative(0, t)
            khe, dkhe = ci_value_derivative(1, t)
            kli, dkli = ci_value_derivative(3, t)
        kf, kr, dkf, dkr = cx_value_derivatives(t)
        return q, t, xe, N, (kh, khe, kli, kf, kr), (dkh, dkhe, dkli, dkf, dkr)

    def rhs(self, theta, z):
        q, _, xe, _, rates, _ = self._values(z)
        Q, v, h, l = q
        kh, khe, kli, kf, kr = rates
        f = self.nH*np.array([
            kh*xe*(self.S-Q),
            math.fsum([kh*xe*(self.D-v), kf*(self.D-v)*(Q-v), -kr*v*(self.H-Q+v)]),
            khe*xe*(1-h),
            kli*xe*(1-l)])
        return (f/(self.clock*self.scale4))[self.active]

    def jacobian(self, theta, z):
        q, t, xe, N, rates, derivs = self._values(z)
        Q, v, h, l = q
        kh, khe, kli, kf, kr = rates
        dkh, dkhe, dkli, dkf, dkr = derivs
        ex = self.xgrad
        M = np.array([
            kh*((self.S-Q)*ex-xe*np.array([1., 0., 0., 0.])),
            kh*((self.D-v)*ex-xe*np.array([0., 1., 0., 0.])),
            khe*((1-h)*ex-xe*np.array([0., 0., 1., 0.])),
            kli*((1-l)*ex-xe*np.array([0., 0., 0., 1.]))])
        M[1, 0] += kf*(self.D-v)+kr*v
        M[1, 1] += kf*(2*v-self.D-Q)-kr*(self.H-Q+2*v)
        w = np.array([
            dkh*xe*(self.S-Q),
            math.fsum([dkh*xe*(self.D-v), dkf*(self.D-v)*(Q-v), -dkr*v*(self.H-Q+v)]),
            dkhe*xe*(1-h), dkli*xe*(1-l)])
        gradT = -(self.bgrad+CV*t*ex)/(CV*N)
        raw = self.nH*(M+np.outer(w, gradT))
        scaled = raw*self.scale4[None, :]/self.scale4[:, None]/self.clock
        return scaled[np.ix_(self.active, self.active)]

    def lifted_rhs(self, theta, z):
        """Full 22-state proper-time tangent, for independent operator checks."""
        rawdot = np.zeros(4)
        rawdot[self.active] = self.rhs(theta, z)*self.scale4[self.active]*self.clock
        dq, dv, dh, dl = rawdot
        yp = np.zeros(atomic.N_SPECIES)
        yp[IX["H1_I"]] = -dq+dv
        yp[IX["H1_II"]] = dq-dv
        yp[IX["D_I"]] = -dv
        yp[IX["D_II"]] = dv
        yp[self.he_i] = -self.he_lift*dh
        yp[self.he_ii] = self.he_lift*dh
        yp[self.li_i] = -self.li_lift*dl
        yp[self.li_ii] = self.li_lift*dl
        udot = -math.fsum(float(a)*float(b) for a, b in zip(self.bgrad, rawdot))
        return np.r_[yp, udot]
