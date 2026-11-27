"""Source-identified, live-ionization LRS Bianchi I preliminary trajectories.

Nine elemental charge fractions are an exact invariant of the selected
isotope-equal photo/RR model. All 21 isotope/charge abundances are saved. The
atomic gas is isotropic; the finite-mass anisotropic sector is nonbaryonic.
The chemical rates and photon opacity both use each trajectory's actual H.
"""
from __future__ import annotations

import os
for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"

from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import tempfile
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from compact_transport import CompactTransport, GAMMA_PER_NE, SQRT6, UNIT
from primordial_network import PrimordialNetwork
from shared_runner import atomic_json

SCHEMA = "he32.live_primordial_pilot.v1"
DEFAULTS = dict(ellmax=16, radial_cells=24, angular_cells=12, gauss_order=3,
                mass_fraction=.1, mass_over_Tref=30., orientation=1,
                z_start=20., z_end=2., samples=201, method="BDF",
                rtol=3e-11, atol=3e-13, max_step=.025)
SIGMAS = [0., .0001, .001, .01, .03, .1, .3, .6]
PMS = [-.0006, -.0003, -.0001, 0., .0001, .0003, .0012]
PRS = [-.0024, -.001, -.0003, 0., .0003, .001, .0048]
CHECK_NAMES = frozenset(("finite", "isotope_charge_simplex", "sampled_radiation_positivity",
    "comoving_number", "component_shear_budget", "opacity_monotone",
    "frozen_Li_high_states", "physical_chart", "freezeout_envelope"))


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, np.ndarray):
        return plain(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    return value


def canonical(value):
    return json.dumps(plain(value), sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(config):
    required = {"Sigma_F", "P_m", "P_r"}
    if not required <= config.keys():
        raise ValueError("Sigma_F, P_m and P_r are required")
    permitted = required | DEFAULTS.keys() | {"case_id", "role"}
    if config.keys() - permitted:
        raise ValueError("unrecognized configuration fields")
    c = dict(DEFAULTS, **config)
    integer_fields = ("ellmax", "radial_cells", "angular_cells", "gauss_order", "orientation", "samples")
    float_fields = ("Sigma_F", "P_m", "P_r", "mass_fraction", "mass_over_Tref",
                    "z_start", "z_end", "rtol", "atol", "max_step")
    for key in integer_fields:
        if isinstance(c[key], bool) or not isinstance(c[key], (int, float, np.number)) or int(c[key]) != c[key]:
            raise ValueError("integral numeric configuration required: " + key)
        c[key] = int(c[key])
    for key in float_fields:
        if isinstance(c[key], bool) or not isinstance(c[key], (int, float, np.number)) or not math.isfinite(c[key]):
            raise ValueError("finite numeric configuration required: " + key)
        c[key] = float(c[key])
    if (c["z_start"] != 20. or c["z_end"] != 2. or c["samples"] < 3
            or c["method"] not in ("BDF", "Radau")
            or not 1e-14 <= c["rtol"] <= 1e-6
            or not 1e-16 <= c["atol"] <= 1e-8
            or not 0 < c["max_step"] <= .1):
        raise ValueError("outside the declared redshift/integration contract")
    return c


@lru_cache(maxsize=1)
def executor_identity():
    paths = ["src/coupled_pilot.py", "src/compact_transport.py",
             "src/primordial_network.py", "src/atomic_photo_rr.py",
             "data/ATOMIC_PHOTO_RR.json", "data/ISOTOPE_SCENARIO.json"]
    paths += sorted(str(p.relative_to(UNIT)) for p in (UNIT / "vendor").glob("*.py"))
    paths += ["vendor/REI_BACKGROUND_FAMILY_LOCK.json"]
    return dict(schema=SCHEMA, files={p: file_sha(UNIT / p) for p in paths},
                python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                arithmetic="binary64; one native thread per case")


def case_identity(config):
    c = normalize(config)
    science = {k: v for k, v in c.items() if k not in ("case_id", "role")}
    return hashlib.sha256(canonical(dict(config=science, executor=executor_identity()))).hexdigest()


def case_grid():
    override = os.environ.get("HE32_CAMPAIGN")
    if override:
        value = json.loads(Path(override).read_text())
        return [normalize(c) for c in value["cases"]]
    return [normalize(dict(case_id=f"s{i:02d}_m{j:02d}_r{k:02d}", role="sweep",
                           Sigma_F=s, P_m=m, P_r=r))
            for i, s in enumerate(SIGMAS) for j, m in enumerate(PMS)
            for k, r in enumerate(PRS)]


class CoupledPilot:
    def __init__(self, config):
        self.config = c = normalize(config)
        self.transport = t = CompactTransport(c["Sigma_F"], c["P_m"], c["P_r"],
            **{k: c[k] for k in ("ellmax", "radial_cells", "angular_cells",
                "gauss_order", "z_end", "mass_fraction", "mass_over_Tref", "orientation")})
        self.chemistry = PrimordialNetwork()
        self.nt = t.size
        self.chem = slice(self.nt, self.nt + 9)
        self.tau = self.nt + 9
        self.budget = slice(self.nt + 10, self.nt + 13)
        self.size = self.nt + 13
        self.end = math.log(7.)

    def initial_state(self):
        return np.r_[self.transport.initial_state(), self.chemistry.initial_fractions,
                     np.zeros(4)]

    def rhs(self, x, y):
        a = self.transport.source.aref * math.exp(x)
        f = y[self.chem]
        ne = self.chemistry.electron_density_cm3(a, f)
        dt, geom = self.transport.rhs(x, y[:self.nt], ne, with_geometry=True)
        _, h, _, pm, pg, pn, _, _ = geom
        d = np.empty(self.size)
        d[:self.nt] = dt
        d[self.chem] = self.chemistry.rhs(x, f, h)
        d[self.tau] = GAMMA_PER_NE * ne / h
        pref = math.exp(3*x) * 3*self.transport.source.h0**2 / (self.transport.source.href*h)
        d[self.budget] = pref * np.array([pm, pg, pn])
        return d

    def jacobian(self, x, y):
        """Exact linear/chemical blocks plus four smooth geometry columns.

        Central differences are confined to b, q, E_gamma0, E_nu0. All other
        columns use the analytic generator and electron-density gradient.
        This does not finite-difference each isotope or each angular mode.
        """
        t = self.transport
        a, h, s, pm, _, _, tower, _ = t.geometry(x, y[:self.nt])
        f = y[self.chem]
        ne = self.chemistry.electron_density_cm3(a, f)
        ne_grad = self.chemistry.electron_gradient_cm3(a)
        v, g = s/h, GAMMA_PER_NE*ne/h
        n = t.n
        j = np.zeros((self.size, self.size))
        j[2, 2] = -3.
        for k, op in enumerate((t.energy, t.number, t.energy, t.number)):
            sl = slice(3 + k*n, 3 + (k+1)*n)
            block = v*op
            if k < 2:
                block = block - g*np.diag(t.damp)
                j[sl, self.chem] = np.outer(-GAMMA_PER_NE/h*t.damp*tower[k], ne_grad)
            j[sl, sl] = block
        for column, omega, budget_row in ((4, t.omega_gamma, self.nt+11),
                                          (4+2*n, t.omega_nu, self.nt+12)):
            coefficient = t.source.h0**2*omega/(t.source.href*h*a**4)
            j[2, column] += coefficient
            j[budget_row, column] = math.exp(3*x)*coefficient
        j[self.chem, self.chem] = self.chemistry.jacobian(x, f, h)
        j[self.tau, self.chem] = GAMMA_PER_NE/h*ne_grad
        # At fixed eta, d rho_massive/db = -6 pi_massive follows by
        # differentiating each canonical packet energy. Differentiate the
        # H-denominator analytically so a large photo RHS is never subtracted
        # to recover a small geometry sensitivity.
        dlogh = {1: -3*t.source.h0**2*pm/h**2,
                 2: y[2]*t.source.href**2/h**2,
                 3: t.source.h0**2*t.omega_gamma/(2*h**2*a**4),
                 3+2*n: t.source.h0**2*t.omega_nu/(2*h**2*a**4)}
        chemical_rhs = self.chemistry.rhs(x, f, h)
        delta = np.cbrt(np.finfo(float).eps)
        for column in (1, 2, 3, 3+2*n):
            step = delta*max(1., abs(float(y[column])))
            yp, ym = y.copy(), y.copy()
            yp[column] += step
            ym[column] -= step
            j[:, column] = (self.rhs(x, yp)-self.rhs(x, ym))/(2*step)
            j[self.chem, column] = -chemical_rhs*dlogh[column]
            j[self.tau, column] = -GAMMA_PER_NE*ne/h*dlogh[column]
        return j

    def integrate(self):
        c = self.config
        return solve_ivp(self.rhs, (0., self.end), self.initial_state(),
                         method=c["method"], jac=self.jacobian,
                         rtol=c["rtol"], atol=c["atol"], max_step=c["max_step"],
                         t_eval=np.linspace(0., self.end, c["samples"]))

    def summarize(self, solution):
        if not solution.success or solution.t[-1] != self.end:
            raise RuntimeError("integration did not reach z=2: " + solution.message)
        t = self.transport
        rows, electron_rows, abundance_rows, brightness = [], [], [], []
        for x, y in zip(solution.t, solution.y.T):
            a = t.source.aref*math.exp(float(x))
            f = y[self.chem]
            ne = self.chemistry.electron_density_cm3(a, f)
            row = t.observables(float(x), y[:self.nt], ne, float(y[self.tau]))
            row.update(H_Href=row["H_per_s"]/t.source.href, I_s_initial=t.q0,
                       I_m=float(y[self.nt+10]), I_gamma=float(y[self.nt+11]),
                       I_nu=float(y[self.nt+12]))
            lhs = math.exp(3*x)*row["signed_Sigma"]*row["H_Href"]/SQRT6
            row["I_shear"] = lhs
            row["budget_residual"] = lhs-t.q0-sum(y[self.budget])
            rows.append(row)
            electron_rows.append(self.chemistry.electron_by_nuclide_cm3(a, f))
            abundance_rows.append(self.chemistry.abundance_per_H(f))
            brightness.append(t.brightness_min(y[:self.nt], angles=257))
        names = list(rows[0])
        obs = np.array([[r[k] for k in names] for r in rows])
        f = solution.y[self.chem]
        norms = np.stack([f[0:2].sum(axis=0), f[2:5].sum(axis=0), f[5:9].sum(axis=0)])
        by_name = {k: obs[:, i] for i, k in enumerate(names)}
        nc = by_name["matter_number_comoving"]
        metrics = dict(fraction_min=float(f.min()), fraction_max=float(f.max()),
            fraction_sum_max_abs_error=float(np.max(abs(norms-1))),
            brightness_min_sampled=float(min(brightness)),
            matter_comoving_number_max_relative_error=float(np.max(abs(nc/nc[0]-1))),
            radiation_number0_max_abs_error=float(max(
                np.max(abs(by_name["N_gamma_0"]-1)), np.max(abs(by_name["N_nu_0"]-1)))),
            budget_max_abs_residual=float(np.max(abs(by_name["budget_residual"]))),
            tau_min_increment=float(np.min(np.diff(by_name["tau_T"]))),
            elapsed_s=float(by_name["elapsed_s"][-1]),
            proper_ne_max_cm3=float(by_name["ne_cm3"].max()),
            proper_baryon_max_cm3=float(self.chemistry.nH0_m3*self.chemistry.baryons_per_H*1e-6/t.source.aref**3),
            high_Li_fraction_max_abs=float(np.max(abs(f[7:9]))),
            b_max_abs=float(np.max(abs(by_name["b"]))))
        checks = dict(finite=bool(np.isfinite(solution.y).all() and np.isfinite(obs).all()),
            isotope_charge_simplex=metrics["fraction_min"] >= -2e-10 and
                metrics["fraction_max"] <= 1+2e-10 and metrics["fraction_sum_max_abs_error"] <= 2e-9,
            sampled_radiation_positivity=metrics["brightness_min_sampled"] >= -2e-8,
            comoving_number=metrics["matter_comoving_number_max_relative_error"] <= 2e-12 and
                metrics["radiation_number0_max_abs_error"] <= 2e-10,
            component_shear_budget=metrics["budget_max_abs_residual"] <= 3e-8,
            opacity_monotone=metrics["tau_min_increment"] >= -2e-12,
            frozen_Li_high_states=metrics["high_Li_fraction_max_abs"] <= 1e-13,
            physical_chart=metrics["b_max_abs"] < 1.,
            freezeout_envelope=metrics["elapsed_s"] <= 1.1e17 and metrics["proper_baryon_max_cm3"] < .01)
        arrays = dict(x=solution.t, state=solution.y, observables=obs,
            observable_names=np.asarray(names), ion_fractions=f,
            abundance_per_H=np.asarray(abundance_rows).T,
            species_names=np.asarray(self.chemistry.species_names),
            electron_by_nuclide_cm3=np.asarray(electron_rows).T,
            nuclide_names=np.asarray(self.chemistry.nuclide_names),
            brightness_min_sampled=np.asarray(brightness))
        return arrays, plain(metrics), plain(checks), plain(rows[-1])


def atomic_npz(path, arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            np.savez_compressed(stream, **arrays)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def completed_result(config, path):
    path = Path(path)
    if not path.is_file():
        return False
    receipt = json.loads(path.read_text())
    if (receipt.get("status") != "completed" or receipt.get("identity") != case_identity(config)
            or receipt.get("schema") != SCHEMA or set(receipt.get("checks", {})) != CHECK_NAMES
            or any(v is not True for v in receipt["checks"].values())):
        return False
    data = path.parent / receipt["npz"]
    return data.is_file() and file_sha(data) == receipt["npz_sha256"]


def write_case(config, outdir):
    config = normalize(config)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    identity = case_identity(config)
    case_id = config.get("case_id", identity[:16])
    receipt_path, npz_path = outdir/(case_id+".json"), outdir/(case_id+".npz")
    if completed_result(config, receipt_path):
        return json.loads(receipt_path.read_text())
    if receipt_path.exists() or npz_path.exists():
        raise FileExistsError("preserve previous result; recover metadata or use a resolved new identity")
    model = CoupledPilot(config)
    started = time.monotonic()
    solution = model.integrate()
    try:
        arrays, metrics, checks, endpoint = model.summarize(solution)
    except Exception as error:
        failed = plain(dict(schema=SCHEMA, status="integration_or_summary_failed",
            case_id=case_id, identity=identity, config=config, executor=executor_identity(),
            error=repr(error), solver_message=solution.message, solver_success=solution.success,
            nfev=solution.nfev, njev=solution.njev, nlu=solution.nlu,
            retained_state_semantics="actual solver-returned saved states; incomplete or ungated",
            npz=npz_path.name))
        atomic_npz(npz_path, dict(x=solution.t, state=solution.y,
                                  metadata_json=np.asarray(canonical(failed).decode())))
        failed["npz_sha256"] = file_sha(npz_path)
        atomic_json(receipt_path, failed, replace=False)
        raise
    receipt = plain(dict(schema=SCHEMA, status="completed" if all(checks.values()) else "gate_failed",
        case_id=case_id, identity=identity, config=config, executor=executor_identity(),
        created_utc=datetime.now(timezone.utc).isoformat(),
        solver=dict(success=solution.success, message=solution.message, nfev=solution.nfev,
                    njev=solution.njev, nlu=solution.nlu),
        elapsed_wall_seconds=time.monotonic()-started,
        metrics=metrics, checks=checks, endpoint=endpoint,
        source_stress_semantics=dict(matter="nonbaryonic collisionless, fm=0.1; isotropic baryonic gas pi=0",
            radiation="signed photon+neutrino sum before absolute value"),
        npz=npz_path.name))
    # Embed all metadata before output publication. A later JSON write failure can
    # be repaired from this NPZ without any scientific reintegration.
    arrays["metadata_json"] = np.asarray(canonical(receipt).decode())
    atomic_npz(npz_path, arrays)
    receipt["npz_sha256"] = file_sha(npz_path)
    atomic_json(receipt_path, receipt, replace=False)
    if not all(checks.values()):
        raise RuntimeError("trajectory retained but gates failed: " + repr(checks))
    return receipt


def recover_receipt(npz_path):
    """Metadata-only recovery after a post-integration JSON write interruption."""
    npz_path = Path(npz_path)
    with np.load(npz_path, allow_pickle=False) as archive:
        receipt = json.loads(str(archive["metadata_json"]))
    if receipt["identity"] != case_identity(receipt["config"]):
        raise ValueError("executor changed; preserve the original source before recovery")
    receipt["npz_sha256"] = file_sha(npz_path)
    atomic_json(npz_path.with_suffix(".json"), receipt, replace=False)
    return receipt
