"""Independent continuous-RHS comparison for the source-backed V4 route."""
from __future__ import annotations
import json
from pathlib import Path
from sys import path

HERE = Path(__file__).resolve().parent
path.insert(0, str(HERE / "donor"))
path.insert(0, str(HERE.parent / "lrs_threshold_oracle_20261015"))
import numpy as np
from scipy.integrate import solve_ivp
from dynamic_chemistry import CHANNELS, PRODUCT, TARGET, Gas
from lrs_threshold_oracle import GAUSS8, Ray
from recomb_thermal import (C_CM_PER_S, MB_CM2, K_B_EV_PER_K,
                            NATIVE_BINDING_EV, EV_J, evolve_thermal,
                            particle_count)
from rate_table import CaseARates
from verner_angular import load_primary_fits

GAS = Gas(.37, .03, .085, .012, .003)
N_STAR = 1e-6  # proper cm^-3 at X=0, source-backed subset
H0 = 1e-16  # proper s^-1, prescribed local background
END = .05
T0 = 15_000.0
STEPS = (.005, .0025, .00125, .000625)


def rays(shear: float, photon_scale: float = .005):
    return tuple(Ray(e, float(mu), .5 * float(w) * count * photon_scale, shear)
                 for e, count in ((110., .12), (72., .08), (43., .06))
                 for mu, w in GAUSS8)


def independent_rhs(ray_set, initial: Gas, provider, end=END):
    """Fresh rate equations; no V4 splitting, pair_exact or ledger closure."""
    fits = load_primary_fits()
    n = len(ray_set)
    y0 = np.array([*[r.photons0 for r in ray_set], *initial.as_tuple(),
                   1.5*K_B_EV_PER_K*T0*particle_count(initial.as_tuple())], float)
    bind = np.array(NATIVE_BINDING_EV)
    idx_target = np.array(TARGET)
    idx_product = np.array(PRODUCT)
    photo_normal = C_CM_PER_S*N_STAR*MB_CM2/H0

    def rhs(x, y):
        photons = y[:n]
        g = y[n:n+5]
        u = y[-1]
        energies = np.array([r.geometry(x)[0] for r in ray_set])
        sigma = np.array([[fits[name].sigma_mb(float(e)) for name in CHANNELS]
                          for e in energies])
        dilution = np.exp(-3*x)
        p = photo_normal*dilution*sigma*photons[:, None]*g[idx_target][None, :]
        pchan = p.sum(axis=0)
        ne = g[1]+g[3]+2*g[4]
        t = u/(1.5*K_B_EV_PER_K*(g.sum()+ne))
        c = provider(float(t))
        alpha = np.array((c[0], c[1]+c[3], c[2]))
        cooling = np.array((c[4], c[5]+c[7], c[6]))
        rr = (N_STAR/H0)*dilution*ne*g[idx_product]*alpha
        du_cool = float(np.dot(rr, cooling/alpha)/(EV_J*1e7))
        out = np.zeros_like(y)
        out[:n] = -p.sum(axis=1)
        for j in range(3):
            out[n+TARGET[j]] += -pchan[j]+rr[j]
            out[n+PRODUCT[j]] += pchan[j]-rr[j]
        out[-1] = -2*u + float(np.sum(p*(energies[:, None]-bind[None, :]))) - du_cool
        return out

    solution = solve_ivp(rhs, (0, end), y0, method="Radau", rtol=2e-11,
                         atol=2e-14, max_step=.002)
    if not solution.success:
        raise RuntimeError(solution.message)
    y = solution.y[:, -1]
    ne = y[n+1]+y[n+3]+2*y[n+4]
    t = y[-1]/(1.5*K_B_EV_PER_K*(sum(y[n:n+5])+ne))
    return y, float(t), float(ne), int(solution.nfev)


def run():
    provider = CaseARates()
    cases = {
        "H_only": (rays(0., 0.), Gas(.37, .03, 0., 0., 0.)),
        "He_only": (rays(0., 0.), Gas(0., 0., .085, .012, .003)),
        "mixed_FLRW": (rays(0.), GAS),
        "mixed_LRS_minus": (rays(-.04), GAS),
        "mixed_LRS_plus": (rays(.04), GAS),
    }
    records = {}
    for name, (rr, gas) in cases.items():
        ref, rt, rn, nfev = independent_rhs(rr, gas, provider)
        rows = []
        for step in STEPS:
            result = evolve_thermal(rr, gas, END, temperature_initial_K=T0,
                                    max_step=step, atomic_rates=provider,
                                    n_star_cm3=N_STAR, h0_s=H0)
            vector = np.array([*result.photons_final, *result.final.as_tuple(),
                               result.final_thermal_ev])
            rows.append({
                "step": step, "steps": result.steps,
                "T_K": result.final_temperature_K,
                "ne": result.final.electrons,
                "T_abs_error_K": abs(result.final_temperature_K-rt),
                "ne_abs_error": abs(result.final.electrons-rn),
                "max_state_abs_error": float(np.max(np.abs(vector-ref))),
                "energy_residual_ev": result.energy_residual_ev,
                "photon_residual": result.photon_reaction_residual,
                "electron_residual": result.electron_reaction_residual,
                "hydrogen_residual": result.hydrogen_residual,
                "helium_residual": result.helium_residual,
                "min_population": min(*result.final.as_tuple(), *result.photons_final),
                "recomb_events": result.recomb_events,
                "photo_events": result.photo_events,
            })
        records[name] = {"radau_T_K": rt, "radau_ne": rn,
                         "radau_nfev": nfev, "refinement": rows}
    return {"scope": "Grackle 3.4.1 Case-A owner table 10000..24000 K; prescribed H/H0=1",
            "source_parent": "PR156 0c2e7b2ada4fea131a5779066894589d0dda8059",
            "n_star_cm3": N_STAR, "h0_s": H0, "X_end": END, "T0_K": T0,
            "cases": records}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
