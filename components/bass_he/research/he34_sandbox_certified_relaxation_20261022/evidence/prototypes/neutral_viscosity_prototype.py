"""Independent equation implementation for neutral H/He shear viscosity.

Source: Wargnier et al (2020), Appendix C.29,C.30,C.35--C.38;
Bruno et al (2010), Eq11 coefficients in the pinned Mutation++ database.
No Mutation++ executable code is copied. Dynamic response nu=p/eta is only
a viscosity-matched model, not an exact transient collision operator.

Inputs are temperature [K], caller-specified atomic masses [kg], and any
nonnegative number weights proportional to n_H and n_He. They need not sum
to one. The common-temperature, dilute, nearly Maxwellian hydrodynamic
transport assumptions are external validity conditions.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import platform
import sys

KB = 1.380649e-23
DATA_PATH = Path(__file__).with_name("NEUTRAL_H_HE_TRANSPORT_SUBSET.json")
DATA = json.loads(DATA_PATH.read_text())
COEFF = {(tuple(row["pair"]), row["kind"]): row["coefficients"] for row in DATA["fits"]}

def _positive(v, name):
    if not math.isfinite(v) or v <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return v

def _expit(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)

def collision_integral(T, pair, kind):
    _positive(T, "T")
    if T < 50 or T > 50000:
        raise ValueError("Bruno2010 fitted domain is 50 <= T <= 50000 K")
    a = COEFF[(tuple(pair), kind)]
    z = math.log(T)
    raw_A2 = (a[0]+a[1]*z)*_expit(2*(z-a[2])/a[3]) + a[4]*_expit(2*(z-a[5])/a[6])
    return _positive(math.pi*1e-20*raw_A2, "Qbar")

@dataclass(frozen=True)
class NeutralTransport:
    T_K: float
    mass_H_kg: float
    mass_He_kg: float
    QHH22_m2: float
    QHHe11_m2: float
    QHHe22_m2: float
    QHeHe22_m2: float
    eta_H_Pa_s: float
    eta_He_Pa_s: float
    nD_HHe_per_m_s: float
    r: float
    Astar: float
    u: float

    def viscosity(self, n_H_weight, n_He_weight):
        if any(not math.isfinite(v) or v < 0 for v in [n_H_weight, n_He_weight]):
            raise ValueError("Number weights must be finite and nonnegative")
        scale = max(n_H_weight, n_He_weight)
        if scale == 0:
            raise ValueError("A zero-density pair has no defined mixture composition")
        # Exact homogeneity permits scaling; it introduces no artificial floor.
        x = n_H_weight/scale
        y = n_He_weight/scale
        a = 1/self.eta_H_Pa_s
        b = 1/self.eta_He_Pa_s
        cH = self.u*(1.2*self.Astar*self.r+2)
        cHe = self.u*(1.2*self.Astar/self.r+2)
        numerator = self.u*(1.2*self.Astar*(x/math.sqrt(self.r)-y*math.sqrt(self.r))**2+2*(x+y)**2)+x*y*(a+b)
        determinant_reduced = x*x*cHe*a+y*y*cH*b+x*y*(a*b+2.4*self.Astar*self.u*self.u*(self.r+1/self.r+2))
        return _positive(numerator/determinant_reduced, "eta_mix")

    def direct_matrix_reference(self, x, y):
        if x <= 0 or y <= 0:
            raise ValueError("Interior reference only; endpoints use pure species")
        import numpy as np
        fac = x*y*self.u
        G = np.array([[x*x/self.eta_H_Pa_s+fac*(1.2*self.Astar*self.r+2),
                       fac*(1.2*self.Astar-2)],
                      [fac*(1.2*self.Astar-2),
                       y*y/self.eta_He_Pa_s+fac*(1.2*self.Astar/self.r+2)]])
        v = np.array([x,y])
        return float(v@np.linalg.solve(G,v))

def prepare_neutral_transport(T_K, mass_H_kg, mass_He_kg):
    _positive(mass_H_kg, "mass_H")
    _positive(mass_He_kg, "mass_He")
    qhh = collision_integral(T_K, ("H","H"), "Q22")
    qhh11 = collision_integral(T_K, ("H","He"), "Q11")
    qhh22 = collision_integral(T_K, ("H","He"), "Q22")
    qhe = collision_integral(T_K, ("He","He"), "Q22")
    eh = 5/16*math.sqrt(math.pi*KB*T_K*mass_H_kg)/qhh
    ehe = 5/16*math.sqrt(math.pi*KB*T_K*mass_He_kg)/qhe
    nd = 3/16*math.sqrt(2*math.pi*KB*T_K*(1/mass_H_kg+1/mass_He_kg))/qhh11
    return NeutralTransport(T_K,mass_H_kg,mass_He_kg,qhh,qhh11,qhh22,qhe,eh,ehe,nd,
                            mass_He_kg/mass_H_kg,qhh22/qhh11,1/(nd*(mass_H_kg+mass_He_kg)))

def run():
    import numpy as np
    # Numerical test parameters: nuclear mass-number model H=1u, He=4u.
    # This does not select masses for a future BASS_HE physical run.
    mass_unit_test = 1.66053906660e-27
    max_relative = 0.0
    count = 0
    for T in [50.,100.,1000.,20000.,50000.]:
        p = prepare_neutral_transport(T,mass_unit_test,4*mass_unit_test)
        for x in [1e-12,1e-8,.01,.5,12/13,.99,1-1e-8,1-1e-12]:
            a = p.viscosity(x,1-x)
            b = p.direct_matrix_reference(x,1-x)
            max_relative = max(max_relative,abs(a-b)/b)
            assert abs(a-b)/b < 2e-14
            count += 1
        assert abs(p.viscosity(1,0)/p.eta_H_Pa_s-1)<5e-16
        assert abs(p.viscosity(0,1)/p.eta_He_Pa_s-1)<5e-16
        assert abs(p.viscosity(1e-300,1)/p.eta_He_Pa_s-1)<5e-16
        assert abs(p.viscosity(1,1e-300)/p.eta_H_Pa_s-1)<5e-16
        # Homogeneous weights need no normalization; keep both trace species.
        assert abs(p.viscosity(1e200,2e200)/p.viscosity(1,2)-1)<5e-16
    invalid = 0
    p = prepare_neutral_transport(20000,mass_unit_test,4*mass_unit_test)
    for a,b in [(0,0),(-1,1),(float("nan"),1),(float("inf"),1)]:
        try:
            p.viscosity(a,b)
        except ValueError:
            invalid += 1
        else:
            raise AssertionError((a,b))
    for T in [49,50001]:
        try:
            prepare_neutral_transport(T,mass_unit_test,4*mass_unit_test)
        except ValueError:
            invalid += 1
        else:
            raise AssertionError(T)
    return {
        "scope":"neutral H/He first-order Chapman-Enskog viscosity equation prototype; no transient ODE",
        "environment":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__},
        "matrix_reference_cases":count,"max_relative_matrix_difference":max_relative,
        "pure_trace_homogeneous_checks":25,"invalid_rejections":invalid,
        "test_mass_model":{"mass_unit_parameter_kg":mass_unit_test,"H_multiplier":1,"He_multiplier":4},
        "T20000_coefficients":p.__dict__,
        "T20000_eta_at_H_He_12_to_1_Pa_s":p.viscosity(12,1),
        "data_sha256":hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }

if __name__ == "__main__":
    result = run()
    print(json.dumps(result,indent=2))

