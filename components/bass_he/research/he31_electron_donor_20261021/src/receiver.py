"""Full40 canonical FV receiver, one diagnostic optical-depth state and resumable cases.

The original photon/neutrino hierarchy and physical initial axes are retained.
Optional prepared moments only rearrange the original finite quadrature.
"""
from __future__ import annotations

import os
for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                         "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_thread_variable] = "1"

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import traceback

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from bindings import UNIT, VENDOR, load_model, load_runner, implementation_identity, verify_baseline
from electron_donor import ElectronDonor, canonical_bytes, GAMMA_PER_NE

C_SI = 299792458.
G_SI = 6.67430e-11
KAPPA_T = 8*math.pi*G_SI/(C_SI*C_SI)
SQRT6 = math.sqrt(6.)
CASE_SCHEMA = "he31.full40_electron_receiver.v1"
DEFAULT_NUMERICS = dict(ellmax=8, radial_cells=24, angular_cells=12,
                        gauss_order=3, rtol=3e-11, atol=3e-13, samples=121)


def plain(value):
    """Convert NumPy scalar types before hashing and durable JSON encoding."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key:plain(item) for key,item in value.items()}
    if isinstance(value, (list,tuple)):
        return [plain(item) for item in value]
    return value


@lru_cache(maxsize=8)
def donor_at(path_string, expected_manifest_sha):
    path = Path(path_string)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_manifest_sha:
        raise ValueError("campaign donor manifest changed")
    return ElectronDonor.load(path)


def selected_donor(config):
    if config["opacity"] == "off":
        return None
    path = Path(config["donor_manifest"])
    if not path.is_absolute():
        path = UNIT/path
    donor = donor_at(str(path.resolve()), config["donor_manifest_sha256"])
    if donor.metadata["provenance"]["kind"] == "manufactured_control" and config.get("purpose") != "contract_control":
        raise ValueError("manufactured donor requires explicit contract_control purpose")
    donor.require_support(1/21., 1/(1+config["z_end"]))
    return donor


def validate_config(config):
    for key in ("Sigma_F", "P_m", "P_r", "z_end"):
        if not isinstance(config.get(key), (int,float)) or not math.isfinite(config[key]):
            raise ValueError("finite physical initial axes required: " + key)
    if not (0 <= config["Sigma_F"] <= .1 and abs(config["P_m"]) <= .0003
            and abs(config["P_r"]) <= .001 and 2 <= config["z_end"] < 20):
        raise ValueError("case lies outside the stated HE31 pilot axes or z interval")
    if config.get("opacity") not in ("on", "off") or config.get("backend") not in ("reference", "prepared"):
        raise ValueError("explicit opacity and moment backend required")
    numerics = config.get("numerics", DEFAULT_NUMERICS)
    if numerics != DEFAULT_NUMERICS:
        raise ValueError("this ready campaign uses the frozen nominal numerical contract")
    return numerics


def source(z_end):
    _, _, SourceLock = load_model()
    original = json.loads((VENDOR/"REI_BACKGROUND_FAMILY_LOCK.json").read_text())
    c = original["cosmology"]
    return SourceLock(c["H0_per_s"], c["Omega_m"], c["Omega_r"], c["Omega_lambda"],
                      original["clock"]["a_ref"], 1/(1+z_end))


@lru_cache(maxsize=1)
def matter_unit_pi():
    _, Momentum, _ = load_model()
    return Momentum(30., amplitude=1., radial_cells=24, angular_cells=12,
                    gauss_order=3).moments(0., 0.).pi_s


def make_model(config):
    numerics = validate_config(config)
    Canonical, _, _ = load_model()
    src = source(config["z_end"])
    sigma, pm, pr = config["Sigma_F"], config["P_m"], config["P_r"]
    q = sigma/math.sqrt(6-sigma*sigma)
    h_initial = src.href*math.sqrt(1+q*q)
    fr = src.h0**2*src.omega_r/(src.aref**4*src.href**2)
    arad = 5*pr*(1+q*q)/(SQRT6*fr)
    cm = KAPPA_T*SQRT6*src.rhocrit_j_m3*(src.omega_m*.1/src.aref**3)*matter_unit_pi()/h_initial**2
    am = pm/cm
    if not -1 <= am <= 2 or abs(arad) > .5:
        raise ValueError("requested axes violate original positive distribution domain")
    donor = selected_donor(config)
    model = Canonical(src, 2.7255, ellmax=numerics["ellmax"],
        Sigma_ref=sigma/math.sqrt(2.), orientation=int(sigma > 0),
        kappa_gamma=arad, kappa_nu=arad, ne_source=donor,
        mass_fraction=.1, massive_A=am, mass_over_Tref=30.,
        radial_cells=numerics["radial_cells"], angular_cells=numerics["angular_cells"],
        subcell_gauss_order=numerics["gauss_order"])
    if config["backend"] == "prepared":
        from prepared_moments import PreparedCanonicalMoments
        model.momentum = PreparedCanonicalMoments(model.momentum)
    return model, donor, dict(matter_A=am, radiation_A=arad,
                              H_initial_per_s=h_initial, mass_fraction=.1, mass_over_Tref=30.)


def augmented_rhs(model, donor):
    """40 unchanged physics variables plus τ; one canonical RHS per call."""
    size = len(model.initial_state())
    def rhs(x, state):
        derivative = model.rhs(x, state[:size])
        rate = 0. if donor is None else donor.rate(model.source.aref*math.exp(x))
        # derivative[0]=H_ref/H from that very RHS, avoiding another field/moment call.
        return np.r_[derivative, rate*derivative[0]/model.source.href]
    return rhs


def normalized_row(x, state, field, src):
    factor = KAPPA_T*SQRT6/(field["H"]*field["H"])
    pm = factor*field["Pi_matter_J_m3"]
    pg = factor*field["Pi_gamma_J_m3"]
    pn = factor*field["Pi_nu_J_m3"]
    pr = pg+pn
    return dict(eta=float(x), a=field["a"], z=1/field["a"]-1,
        elapsed_s=float(state[0]/src.href), H_per_s=field["H"],
        signed_Sigma=SQRT6*field["s"]/field["H"], Sigma_F=SQRT6*abs(field["s"])/field["H"],
        P_m=pm, P_gamma=pg, P_nu=pn, P_r=pr, Pi_m=abs(pm), Pi_r=abs(pr),
        Pi_total=abs(pm+pr), tau_T=float(state[-1]), ne_cm3=field["n_e_cm3"])


def scientific_identity(config):
    validate_config(config)
    donor = selected_donor(config)
    physical = {k:config[k] for k in ("Sigma_F", "P_m", "P_r", "z_end", "opacity", "backend")}
    return dict(schema=CASE_SCHEMA, physics=physical, numerics=DEFAULT_NUMERICS,
                donor_identity=None if donor is None else donor.identity,
                implementation_sha256=implementation_identity(),
                closure="canonical FV plus unpolarized gamma/nu full40; one-way ne; diagnostic tau41",
                coordinates="signed Frobenius; massive nonbaryonic; energy-density SI stress")


def case_identity(config):
    return hashlib.sha256(canonical_bytes(scientific_identity(config))).hexdigest()


def run_case(config):
    started = time.perf_counter()
    identity = case_identity(config)
    result = dict(schema=CASE_SCHEMA, case_id=config["case_id"], identity_sha256=identity,
        inputs=config, source_identity=scientific_identity(config), status="failed",
        environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                         platform=platform.platform(), pid=os.getpid(), numerical_threads=1))
    result["execution_resource_sha256"] = {path:sha for path,sha in verify_baseline()["files"].items()
                                          if "resources/" in path or path.endswith("shared_runner.py")}
    try:
        model, donor, mapping = make_model(config)
        y0 = np.r_[model.initial_state(), 0.]
        grid = np.linspace(0., model.source.xmax, DEFAULT_NUMERICS["samples"])
        sol = solve_ivp(augmented_rhs(model, donor), (0., model.source.xmax), y0,
                        method="DOP853", t_eval=grid, rtol=DEFAULT_NUMERICS["rtol"],
                        atol=DEFAULT_NUMERICS["atol"])
        if not sol.success or len(sol.t) != len(grid):
            raise RuntimeError("full40+tau integration failed: " + sol.message)
        fields = [model.fields(float(x), sol.y[:-1,i]) for i,x in enumerate(sol.t)]
        history = [normalized_row(x, sol.y[:,i], d, model.source)
                   for i,(x,d) in enumerate(zip(sol.t, fields))]
        initial = history[0]
        axis_error = max(abs(initial["Sigma_F"]-config["Sigma_F"]),
                         abs(initial["P_m"]-config["P_m"]), abs(initial["P_r"]-config["P_r"]))
        number_error = max(abs(d[key][0]-1) for d in fields for key in ("N_gamma", "N_nu"))
        gates = dict(initial_axes_abs_1e12=axis_error <= 1e-12,
                     photon_neutrino_number_5e11=number_error <= 5e-11,
                     nonnegative_canonical_cells=all(d["massive_min_cell_population"] >= 0 for d in fields),
                     optical_depth_nondecreasing=bool(np.all(np.diff(sol.y[-1]) >= -1e-13)),
                     finite_history=bool(np.isfinite(sol.y).all()),
                     final_scale_matches=abs(history[-1]["a"]-model.source.aend) <= 1e-14)
        result.update(status="completed" if all(gates.values()) else "failed", gates=gates,
            initial_mapping=mapping, initial_axis_error=axis_error, number_monopole_error=number_error,
            sol_t=sol.t.tolist(), sol_y=sol.y.tolist(), history=history,
            nfev=int(sol.nfev), solver_message=sol.message,
            donor=None if donor is None else donor.report(),
            physical_state_dimension=len(y0)-1, diagnostic_state_dimension=1,
            note="tau uses target H; donor chemistry is prescribed; original scalar unpolarized closure")
    except Exception as error:
        result.update(error=str(error), traceback=traceback.format_exc())
    result["wall_seconds"] = time.perf_counter()-started
    result = plain(result)
    result["payload_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def completed_result(config, path):
    try:
        result = json.loads(Path(path).read_text())
        digest = result.pop("payload_sha256")
        if hashlib.sha256(canonical_bytes(result)).hexdigest() != digest:
            return False
        if (result["schema"] != CASE_SCHEMA or result["status"] != "completed"
                or result["identity_sha256"] != case_identity(config)
                or not result["gates"] or not all(result["gates"].values())):
            return False
        states = np.asarray(result["sol_y"], dtype=float)
        count = DEFAULT_NUMERICS["samples"]
        return bool(states.shape == (41,count) and np.isfinite(states).all()
                    and len(result["sol_t"]) == count and len(result["history"]) == count
                    and abs(result["history"][-1]["a"]-1/(1+config["z_end"])) <= 1e-14
                    and np.all(np.diff(result["sol_t"]) > 0))
    except (OSError,ValueError,KeyError,TypeError,OverflowError):
        return False


def write_case(config, results_dir):
    path = Path(results_dir)/(config["case_id"]+".json")
    if completed_result(config, path):
        return json.loads(path.read_text())
    if path.exists():
        raise FileExistsError("prior partial/failed case preserved: " + str(path))
    result = run_case(config)
    load_runner().atomic_json(path, result, replace=False)
    if result["status"] != "completed":
        raise RuntimeError("case failed; immutable evidence written to " + str(path))
    return result


def case_grid():
    path = os.environ.get("HE31_CAMPAIGN")
    if not path:
        raise ValueError("HE31_CAMPAIGN must name the prepared campaign JSON")
    campaign = json.loads(Path(path).read_text())
    if campaign.get("schema") != "he31.campaign.v1":
        raise ValueError("unsupported HE31 campaign")
    cases = campaign["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("campaign must contain at least one case")
    for config in cases:
        scientific_identity(config)  # input support/SHA before starting any workers
    return cases
