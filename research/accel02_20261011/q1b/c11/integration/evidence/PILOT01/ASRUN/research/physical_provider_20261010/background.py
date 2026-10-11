"""Exact dust+Lambda LRS Bianchi-I background for the scoped HM12 candidate.

This is a selected GR model, not an observed Bianchi history.  Gas thermal and
radiation stress backreaction are excluded.  The mean redshift is a volume
label.  Public interface: BianchiBackground(r=0.001).at(proper_elapsed_seconds),
returning a_rel, b, H, s, z, nH, nHe (density in proper cm^-3).

With a_perp=a exp(-b), a_parallel=a exp(2b), s=bdot, sigma^2=3s^2.
Hfid is the historical HM12 flat-model scale, not H(a=1) at nonzero shear.
Hydrogen/helium masses use the explicitly declared mass-number approximation
m_H=m_proton and m_He=4 m_proton; no atomic mass precision is claimed.
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
from pathlib import Path

from scipy.integrate import quad
from scipy.optimize import brentq

MPC_CM = 3.0856775814913673e24
G_CGS = 6.67430e-8
M_PROTON_G = 1.67262192369e-24


class BianchiBackground:
    def __init__(
        self,
        r: float = 0.001,
        *,
        z_i: float = 5.807,
        Hfid_km_s_Mpc: float = 70.0,
        omega_m: float = 0.3,
        omega_lambda: float = 0.7,
        omega_b: float = 0.045,
        helium_mass_fraction: float = 0.24,
        b_i: float = 0.0,
        t_max: float = 1.0e11,
    ):
        vals = (
            r, z_i, Hfid_km_s_Mpc, omega_m, omega_lambda, omega_b,
            helium_mass_fraction, b_i, t_max,
        )
        if not all(math.isfinite(x) for x in vals):
            raise ValueError("BACKGROUND_NONFINITE_INPUT")
        if not (
            abs(r) < 1 and z_i > -1 and Hfid_km_s_Mpc > 0
            and omega_m > 0 and omega_lambda > 0 and 0 < omega_b <= omega_m
            and 0 < helium_mass_fraction < 1 and t_max > 0
        ):
            raise ValueError("BACKGROUND_PARAMETER_DOMAIN")
        self.r = r
        self.z_i = z_i
        self.a_i = 1.0 / (1.0 + z_i)
        self.v_i = self.a_i**3
        self.b_i = b_i
        self.t_max = t_max
        self.hfid = Hfid_km_s_Mpc * 1.0e5 / MPC_CM
        self.B = self.hfid**2 * omega_m
        self.D = self.hfid**2 * omega_lambda
        f_i = self.B / self.v_i + self.D
        self.H_i = math.sqrt(f_i / (1.0 - r*r))
        self.s_i = r * self.H_i
        self.s0 = self.s_i * self.v_i
        self.C = self.s0**2
        self.omega = 3.0 * math.sqrt(self.D)
        self.root_poly_i = math.sqrt(
            self.D*self.v_i**2 + self.B*self.v_i + self.C
        )
        rho_b0 = omega_b * 3.0*self.hfid**2 / (8.0*math.pi*G_CGS)
        self.nH_i = (1.0-helium_mass_fraction)*rho_b0/M_PROTON_G/self.v_i
        self.nHe_i = helium_mass_fraction*rho_b0/(4.0*M_PROTON_G)/self.v_i

    def _volume(self, t: float) -> float:
        """Exact a(t)^3; stable at t=0 and short intervals."""
        return self.v_i*(1.0+self._relative_volume_increment(t))

    def _relative_volume_increment(self, t: float) -> float:
        """Compute (a(t)/a_i)^3-1 without subtracting unit volumes."""
        x = self.omega*t
        cosh_minus_one = 2.0*math.sinh(0.5*x)**2
        return (
            cosh_minus_one
            + self.root_poly_i/(self.v_i*math.sqrt(self.D))*math.sinh(x)
            + self.B/(2.0*self.D*self.v_i)*cosh_minus_one
        )

    def _validate_time(self, t: float) -> None:
        if not math.isfinite(t) or not 0.0 <= t <= self.t_max:
            raise ValueError("BACKGROUND_TIME_OUTSIDE_IMMUTABLE_DOMAIN")

    @lru_cache(maxsize=32768)
    def _at_tuple(self, t: float) -> tuple[float, ...]:
        self._validate_time(t)
        v = self._volume(t)
        a_rel = (v/self.v_i)**(1.0/3.0)
        a_abs = self.a_i*a_rel
        s = self.s0/v
        H = math.sqrt(self.D+self.B/v+self.C/(v*v))
        if self.s0 == 0.0 or t == 0.0:
            delta_b = 0.0
        else:
            # Integrate a smooth, dimensionless scaled-time function, avoiding
            # subtraction of nearly equal closed-form logarithms at small t.
            delta_b = t*quad(
                lambda u: self.s0/self._volume(t*u),
                0.0, 1.0, epsabs=1.0e-35, epsrel=2.0e-13,
            )[0]
        b = self.b_i+delta_b
        nH = self.nH_i*self.v_i/v
        nHe = self.nHe_i*self.v_i/v
        # Relative spatial axes are measured from the initial coordinate gauge,
        # so b_i cancels.  This is what conserved comoving momentum needs.
        ap = a_rel*math.exp(-delta_b)
        az = a_rel*math.exp(2.0*delta_b)
        z = self.z_i if t == 0.0 else (1.0+self.z_i)/a_rel-1.0
        return a_rel, b, H, s, z, nH, nHe, a_abs, ap, az

    def at(self, t: float) -> dict:
        a_rel,b,H,s,z,nH,nHe,a_abs,ap,az = self._at_tuple(float(t))
        # A fresh dict prevents callers mutating cached provider evidence.
        return {
            "a_rel":a_rel,"b":b,"H":H,"s":s,"z":z,"nH":nH,"nHe":nHe,
            "a_abs":a_abs,"scale_rel":[ap,ap,az],"hubble":[H-s,H-s,H+2*s],
        }

    def time_of_redshift(self, z: float) -> float:
        if not math.isfinite(z) or z <= -1.0:
            raise ValueError("BACKGROUND_REDSHIFT_DOMAIN")
        if z == self.z_i:
            return 0.0
        z_end=self.at(self.t_max)["z"]
        if z == z_end:
            return self.t_max
        if not z_end <= z <= self.z_i:
            raise ValueError("BACKGROUND_REDSHIFT_OUTSIDE_IMMUTABLE_DOMAIN")
        target = math.expm1(3.0*math.log1p((self.z_i-z)/(1.0+z)))
        return brentq(
            lambda t: self._relative_volume_increment(t)-target,
            0.0,self.t_max,xtol=1.0e-4,rtol=4.0*math.ulp(1.0),
        )

    def collisionless_ray(self, t: float, energy_i_ev: float, mu_i: float) -> dict:
        if not (math.isfinite(energy_i_ev) and energy_i_ev>0
                and math.isfinite(mu_i) and -1.0<=mu_i<=1.0):
            raise ValueError("BACKGROUND_RAY_DOMAIN")
        point = self.at(t)
        ap,_,az = point["scale_rel"]
        q_perp = energy_i_ev*math.sqrt(max(0.0,1.0-mu_i*mu_i))
        q_parallel = energy_i_ev*mu_i
        energy = math.hypot(q_perp/ap,q_parallel/az)
        return {"energy_ev":energy,"mu":q_parallel/(az*energy),
                "q_perp":q_perp,"q_parallel":q_parallel}


def validate_background() -> dict:
    """Run scalar identities and an independent direct ODE comparison."""
    from scipy.integrate import solve_ivp
    import numpy as np

    bg = BianchiBackground()
    times = np.linspace(0.0,bg.t_max,17)
    maxima = {"volume_relative":0.0,"shear_relative":0.0,
              "friedmann_relative":0.0,"baryon_relative":0.0,
              "null_covector_relative":0.0,"flrw_relative":0.0}
    previous_a = 0.0
    monotonic = True
    for t in times:
        p=bg.at(float(t)); a=p["a_abs"]; ap,_,az=p["scale_rel"]
        maxima["volume_relative"]=max(maxima["volume_relative"],abs(ap*ap*az/p["a_rel"]**3-1))
        maxima["shear_relative"]=max(maxima["shear_relative"],abs(p["s"]*a**3/bg.s0-1))
        rhs=bg.D+bg.B/a**3+bg.C/a**6
        maxima["friedmann_relative"]=max(maxima["friedmann_relative"],abs(p["H"]**2/rhs-1))
        maxima["baryon_relative"]=max(maxima["baryon_relative"],abs(p["nH"]*p["a_rel"]**3/bg.nH_i-1),abs(p["nHe"]*p["a_rel"]**3/bg.nHe_i-1))
        monotonic=monotonic and a>previous_a; previous_a=a
        for mu in (-1.0,-0.37,0.0,0.37,1.0):
            ray=bg.collisionless_ray(float(t),70.0,mu)
            qz=az*ray["energy_ev"]*ray["mu"]
            qp=ap*ray["energy_ev"]*math.sqrt(max(0.0,1.0-ray["mu"]**2))
            maxima["null_covector_relative"]=max(maxima["null_covector_relative"],abs(qz-ray["q_parallel"])/70.0,abs(qp-ray["q_perp"])/70.0)
    # Independent dimensionless ODE for a/a_i and b, using the Einstein RHS.
    def rhs(u,y):
        a_rel,b=y; a=bg.a_i*a_rel
        H=math.sqrt(bg.D+bg.B/a**3+bg.C/a**6)
        return [bg.t_max*a_rel*H,bg.t_max*bg.s0/a**3]
    ode=solve_ivp(rhs,(0.0,1.0),[1.0,bg.b_i],method="DOP853",rtol=3e-13,atol=[1e-15,1e-20],t_eval=times/bg.t_max)
    if not ode.success:
        raise RuntimeError("BACKGROUND_REFERENCE_ODE_FAILED")
    maxima["independent_ode_a_relative"]=max(abs(bg.at(float(t))["a_rel"]/float(a)-1) for t,a in zip(times,ode.y[0]))
    bscale=abs(bg.at(bg.t_max)["b"]-bg.b_i)
    maxima["independent_ode_b_scaled"]=max(abs(bg.at(float(t))["b"]-float(b))/bscale for t,b in zip(times,ode.y[1]))
    flrw=BianchiBackground(r=0.0)
    tau_i=2/(3*math.sqrt(flrw.D))*math.asinh(math.sqrt(flrw.D/flrw.B)*flrw.a_i**1.5)
    for t in times:
        a=(flrw.B/flrw.D)**(1/3)*math.sinh(1.5*math.sqrt(flrw.D)*(tau_i+t))**(2/3)
        maxima["flrw_relative"]=max(maxima["flrw_relative"],abs(flrw.at(float(t))["a_abs"]/a-1))
    # Time inverse has an unavoidable short-interval conditioning floor from
    # storing redshift near z=5.8 in binary64; report absolute seconds explicitly.
    time_errors=[abs(bg.time_of_redshift(bg.at(float(t))["z"])-t) for t in times[1:-1]]
    inverse_rounding_bound_s=4.0*math.ulp(bg.z_i)/((1.0+bg.z_i)*bg.at(bg.t_max)["H"])
    inverse_within_rounding_bound=bool(max(time_errors)<=inverse_rounding_bound_s)
    out={
        "status":"PASS" if monotonic and max(maxima.values())<1e-11 and inverse_within_rounding_bound else "FAIL",
        "test_type":"selected_model_geometry_validation",
        "identities":maxima,"monotone_scale":monotonic,
        "redshift_inverse_max_absolute_s":max(time_errors),
        "redshift_inverse_max_relative_to_interval":max(time_errors)/bg.t_max,
        "redshift_inverse_input_rounding_bound_s":inverse_rounding_bound_s,
        "redshift_inverse_within_input_rounding_bound":inverse_within_rounding_bound,
        "initial":bg.at(0.0),"final":bg.at(bg.t_max),
        "constants":{"MPC_CM":MPC_CM,"G_CGS":G_CGS,"M_PROTON_G":M_PROTON_G},
        "mass_approximation":"mH=m_proton, mHe=4*m_proton",
        "scientific_ceiling":"conditional Einstein dust+Lambda background; not observed Bianchi geometry; radiation backreaction omitted",
    }
    return out


if __name__ == "__main__":
    result=validate_background()
    evidence=Path(__file__).with_name("evidence")
    evidence.mkdir(exist_ok=True)
    (evidence/"background_validation.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)
