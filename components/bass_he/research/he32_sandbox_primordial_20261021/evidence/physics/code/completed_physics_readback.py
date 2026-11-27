"""Independent saved-array readback of the HE32 completed pilot.

No solver or project scientific module is imported.  This reads saved NPZs,
reconstructs censuses and algebraic identities, and writes a bounded report.
It deliberately does not certify the IVP error or the omitted microphysics.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"

import numpy as np
from scipy.constants import atomic_mass, sigma as stefan_boltzmann

UNIT = Path(__file__).resolve().parents[3]
G = 6.67430e-11
C = 299792458.
NUCLEI = ("n", "H1", "D", "T", "He3", "He4", "Li6", "Li7")
AS = np.array([1, 1, 2, 3, 3, 4, 6, 7])
ZS = np.array([0, 1, 1, 1, 2, 2, 3, 3])
FRACTIONS = ("H_I", "H_II", "He_I", "He_II", "He_III",
             "Li_I", "Li_II", "Li_III", "Li_IV")
GATES = {"finite", "isotope_charge_simplex", "sampled_radiation_positivity",
         "comoving_number", "component_shear_budget", "opacity_monotone",
         "frozen_Li_high_states", "physical_chart", "freezeout_envelope"}
RECOVERY_REFERENCE = {
    "Sigma_F_endpoint_max": .03254372520844899,
    "signed_Sigma_endpoint_min": -.00044172683070029277,
    "Pi_m_endpoint_max": 2.8469475533524753e-5,
    "Pi_r_endpoint_max": .0006995211078292423,
    "tau_T_endpoint_min": .053138680070019574,
    "tau_T_endpoint_max": .05320756262475463,
    "budget_max_abs_residual": 1.7391013906742359e-9,
    "fraction_sum_max_abs_error": 4.107825191113079e-15,
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def atomic_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def maxabs(value):
    return float(np.max(np.abs(value)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=UNIT / "results")
    parser.add_argument("--out", type=Path, default=UNIT / "evidence/physics")
    args = parser.parse_args()
    results = args.results.resolve()
    catalog_path = results / "CATALOG.json"
    catalog = json.loads(catalog_path.read_text())
    assert catalog["count"] == len(catalog["cases"]) == 392
    assert len({c["case_id"] for c in catalog["cases"]}) == 392
    scenario_path = UNIT / "data/ISOTOPE_SCENARIO.json"
    scenario = json.loads(scenario_path.read_text())
    assert scenario == catalog["scenario"]
    cosmology_path = UNIT / "vendor/REI_BACKGROUND_FAMILY_LOCK.json"
    cosmo = json.loads(cosmology_path.read_text())["cosmology"]
    cp = scenario["composition"]
    r4 = cp["YPBBN"] * (1 + 2*cp["DoH"] + 3*cp["He3oH"]
        + 6*cp["Li6oH"] + 7*cp["Li7oH"]) / (4*(1-cp["YPBBN"]))
    ratios = np.array([0., 1., cp["DoH"], 0., cp["He3oH"], r4, cp["Li6oH"], cp["Li7oH"]])
    baryons_per_H = float(AS @ ratios)
    h0 = cosmo["H0_per_s"]
    rho_c = 3*h0*h0/(8*math.pi*G)
    nh0 = rho_c*cosmo["Omega_b"]/(atomic_mass*baryons_per_H)
    href = h0*math.sqrt(cosmo["Omega_m"]*21**3 + cosmo["Omega_r"]*21**4 + cosmo["Omega_lambda"])
    omega_gamma = (4*stefan_boltzmann/C * 2.7255**4) / (rho_c*C*C)
    omega_nu = cosmo["Omega_r"] - omega_gamma
    expected_species, charges, masses, blocks = [], [], [], []
    for name, a, z in zip(NUCLEI, AS, ZS):
        lo = len(expected_species)
        for charge in range(int(z)+1):
            expected_species.append(f"{name}_q{charge}")
            charges.append(charge)
            masses.append(int(a))
        blocks.append(slice(lo, len(expected_species)))
    charges, masses = np.asarray(charges), np.asarray(masses)
    source_hashes = {p: sha(UNIT/p) for p in catalog["executor"]["files"]}
    assert source_hashes == catalog["executor"]["files"], "science source differs from recorded executor"
    executor_id = hashlib.sha256(canonical(catalog["executor"])).hexdigest()
    extrema = {}
    history_extrema = {}
    metrics = {}
    inputs = []
    rows = []
    saved = {}
    min_fraction = math.inf
    min_brightness = math.inf
    min_tau_increment = math.inf
    total_samples = 0
    sign_reversal_cases = []

    def update_metric(name, value):
        metrics[name] = max(metrics.get(name, 0.), float(value))

    def update_range(target, name, value, case_id):
        value = np.atleast_1d(value)
        lo, hi = float(value.min()), float(value.max())
        if name not in target:
            target[name] = {"min": lo, "max": hi, "min_case": case_id, "max_case": case_id}
        if lo < target[name]["min"]:
            target[name].update(min=lo, min_case=case_id)
        if hi > target[name]["max"]:
            target[name].update(max=hi, max_case=case_id)

    for case in catalog["cases"]:
        case_id = case["case_id"]
        path, receipt_path = results/case["npz"], results/case["receipt"]
        digest = sha(path)
        receipt = json.loads(receipt_path.read_text())
        assert digest == case["npz_sha256"] == receipt["npz_sha256"]
        assert receipt["status"] == "completed"
        assert GATES <= receipt["checks"].keys()
        assert all(receipt["checks"][key] is True for key in GATES)
        assert receipt["executor"] == catalog["executor"]
        config = case["config"]
        identity = hashlib.sha256(canonical({"config": {k: v for k, v in config.items()
                if k not in ("case_id", "role")}, "executor": catalog["executor"]})).hexdigest()
        assert identity == case["identity"] == receipt["identity"]
        with np.load(path, allow_pickle=False) as data:
            x, state = data["x"], data["state"]
            f, y = data["ion_fractions"], data["abundance_per_H"]
            electron = data["electron_by_nuclide_cm3"]
            obs = {str(k): data["observables"][:, i] for i, k in enumerate(data["observable_names"])}
            assert list(data["species_names"]) == expected_species
            assert tuple(data["nuclide_names"]) == NUCLEI
            assert x.shape == (201,) and state.shape == (52, 201)
            assert y.shape == (21, 201) and f.shape == (9, 201)
            assert electron.shape == (8, 201)
            assert all(np.isfinite(a).all() for a in (x, state, f, y, electron, data["observables"]))
            assert abs(x[0]) < 1e-15 and abs(x[-1]-math.log(7)) < 1e-15
            total_samples += len(x)
            assert config["ellmax"] == 16
            nt = 39
            update_metric("fraction_state_abs_error", maxabs(f-state[nt:nt+9]))
            sums = np.array([f[:2].sum(axis=0), f[2:5].sum(axis=0), f[5:].sum(axis=0)])
            update_metric("fraction_sum_max_abs_error", maxabs(sums-1))
            min_fraction = min(min_fraction, float(f.min()))
            min_brightness = min(min_brightness, float(data["brightness_min_sampled"].min()))
            min_tau_increment = min(min_tau_increment, float(np.diff(obs["tau_T"]).min()))
            a = np.exp(x)/21
            nh = nh0*1e-6/a**3
            electron_rebuilt = np.stack([nh*(charges[b] @ y[b]) for b in blocks])
            ne = nh*(charges @ y)
            update_metric("electron_census_max_relative_error", maxabs(ne/obs["ne_cm3"]-1))
            update_metric("nuclide_electron_sum_relative_error", maxabs(electron.sum(axis=0)/obs["ne_cm3"]-1))
            update_metric("nuclide_electron_census_scaled_abs_error", maxabs((electron_rebuilt-electron)/obs["ne_cm3"]))
            update_metric("baryon_census_relative_error", maxabs((masses @ y)/baryons_per_H-1))
            for i, block in enumerate(blocks):
                total = y[block].sum(axis=0)
                if ratios[i] > 0:
                    update_metric("isotope_inventory_relative_error", maxabs(total/ratios[i]-1))
                    start = {1: 0, 2: 2, 3: 5}[int(ZS[i])]
                    update_metric("isotope_lift_absolute_fraction_error", maxabs(y[block]/ratios[i]-f[start:start+int(ZS[i])+1]))
                else:
                    update_metric("zero_n_T_inventory_abs", maxabs(y[block]))
            update_metric("high_Li_fraction_abs", maxabs(f[7:9]))
            update_metric("mean_redshift_abs_error", maxabs(obs["z"]-(1/a-1)))
            update_metric("scale_factor_abs_error", maxabs(obs["a"]-a))
            update_metric("H_Href_abs_error", maxabs(obs["H_Href"]-obs["H_per_s"]/href))
            update_metric("elapsed_time_relative_error", maxabs((obs["elapsed_s"][1:]*href)/state[0, 1:]-1))
            signed_shear = math.sqrt(6)*state[2]*href/obs["H_per_s"]
            update_metric("signed_shear_reconstruction_abs_error", maxabs(signed_shear-obs["signed_Sigma"]))
            update_metric("shear_frobenius_abs_error", maxabs(np.abs(signed_shear)-obs["Sigma_F"]))
            pg = math.sqrt(6)*h0*h0*omega_gamma*a**-4*state[4]/obs["H_per_s"]**2
            pn = math.sqrt(6)*h0*h0*omega_nu*a**-4*state[22]/obs["H_per_s"]**2
            update_metric("photon_stress_reconstruction_abs_error", maxabs(pg-obs["P_gamma"]))
            update_metric("neutrino_stress_reconstruction_abs_error", maxabs(pn-obs["P_nu"]))
            for name, expected in (("P_r", obs["P_gamma"]+obs["P_nu"]),
                    ("Pi_m", np.abs(obs["P_m"])), ("Pi_r", np.abs(obs["P_gamma"]+obs["P_nu"])),
                    ("Pi_total", np.abs(obs["P_m"]+obs["P_gamma"]+obs["P_nu"]))):
                update_metric(name+"_norm_or_sum_abs_error", maxabs(obs[name]-expected))
            q0 = config["orientation"]*config["Sigma_F"]/math.sqrt(6-config["Sigma_F"]**2)
            lhs = np.exp(3*x)*state[2]
            budget = lhs-q0-state[49:52].sum(axis=0)
            update_metric("budget_max_abs_residual", maxabs(budget))
            update_metric("budget_saved_residual_abs_error", maxabs(budget-obs["budget_residual"]))
            update_metric("shear_budget_lhs_abs_error", maxabs(lhs-obs["I_shear"]))
            for j, name in enumerate(("I_m", "I_gamma", "I_nu")):
                update_metric("budget_component_state_abs_error", maxabs(obs[name]-state[49+j]))
            update_metric("budget_initial_abs_error", maxabs(obs["I_s_initial"]-q0))
            update_metric("optical_depth_state_abs_error", maxabs(obs["tau_T"]-state[48]))
            update_metric("matter_number_relative_error", maxabs(obs["matter_number_comoving"]/obs["matter_number_comoving"][0]-1))
            update_metric("radiation_number_monopole_abs_error", max(maxabs(obs["N_gamma_0"]-1), maxabs(obs["N_nu_0"]-1)))
            update_metric("chart_b_max_abs", maxabs(obs["b"]))
            update_metric("proper_baryon_max_cm3", float((nh*baryons_per_H).max()))
            endpoint = {}
            for name in ("Sigma_F", "signed_Sigma", "P_m", "P_gamma", "P_nu", "P_r", "Pi_m", "Pi_r", "Pi_total", "ne_cm3", "tau_T", "elapsed_s"):
                value = float(obs[name][-1])
                endpoint[name] = value
                update_range(extrema, name, value, case_id)
                update_range(history_extrema, name, obs[name], case_id)
                assert value == receipt["endpoint"][name] == case["endpoint"][name]
            if np.max(signed_shear) > 1e-15 and np.min(signed_shear) < -1e-15:
                sign_reversal_cases.append(case_id)
            rows.append({"case_id": case_id, "endpoint": endpoint})
            saved[case_id] = {"z": obs["z"].copy(), "ne": obs["ne_cm3"].copy(),
                "fractions": f.copy(), "electron": electron.copy(), "endpoint": endpoint,
                "budget": {name: float(obs[name][-1]) for name in ("I_s_initial", "I_m", "I_gamma", "I_nu", "I_shear", "budget_residual")}}
        inputs.append({"case_id": case_id, "npz": case["npz"], "npz_sha256": digest,
                       "receipt": case["receipt"], "receipt_sha256": sha(receipt_path), "identity": identity})

    iso = saved["s00_m03_r03"]
    k = int(np.argmax(iso["fractions"][5]))
    iso_report = {"case_id": "s00_m03_r03", "endpoint": iso["endpoint"],
        "ion_fraction_endpoint": dict(zip(FRACTIONS, map(float, iso["fractions"][:, -1]))),
        "electron_contribution_cm3_endpoint": dict(zip(NUCLEI, map(float, iso["electron"][:, -1]))),
        "electron_contribution_fraction_endpoint": dict(zip(NUCLEI, map(float, iso["electron"][:, -1]/iso["ne"][-1]))),
        "Li_I_peak_saved_sample": {"fraction": float(iso["fractions"][5, k]), "mean_z": float(iso["z"][k]), "sample_index": k},
        "threshold_crossing_saved_brackets": {}}
    for row, name in ((1, "H_II"), (4, "He_III")):
        for threshold in (.5, .9, .99):
            ids = np.flatnonzero(iso["fractions"][row] >= threshold)
            if len(ids):
                j = int(ids[0])
                iso_report["threshold_crossing_saved_brackets"][name+"_"+str(threshold)] = {
                    "z_bracket": [float(iso["z"][max(0,j-1)]), float(iso["z"][j])],
                    "fraction_bracket": [float(iso["fractions"][row,max(0,j-1)]), float(iso["fractions"][row,j])]}
    comparisons = []
    for case_id in ("s07_m00_r00", "s07_m03_r03", "s07_m06_r06"):
        item = saved[case_id]
        difference = np.abs(item["ne"]/iso["ne"]-1)
        j = int(np.argmax(difference))
        comparisons.append({"case_id": case_id,
            "max_ne_history_relative_difference_from_isotropic": float(difference[j]),
            "mean_z_at_maximum": float(item["z"][j]),
            "ne_endpoint_relative_difference_from_isotropic": float(item["ne"][-1]/iso["ne"][-1]-1),
            "tau_endpoint_difference_from_isotropic": item["endpoint"]["tau_T"]-iso["endpoint"]["tau_T"],
            "endpoint": item["endpoint"], "budget_endpoint": item["budget"]})
    previous_comparison = {}
    for key, previous in RECOVERY_REFERENCE.items():
        if "_endpoint_" in key:
            quantity, limit = key.split("_endpoint_")
            current = extrema[quantity][limit]
        else:
            current = metrics[key]
        previous_comparison[key] = {"previous_tool_output_reference": previous,
            "current_npz_readback": current, "absolute_difference": abs(current-previous)}
    guard_path = results / "ANGULAR_GUARDS.json"
    angular = json.loads(guard_path.read_text())
    assert angular["passed"] is True and len(angular["records"]) == 2
    for item in angular["records"]:
        assert sha(results/"cases"/(item["nominal"]+".npz")) == item["nominal_sha256"]
        assert sha(results/"cases"/(item["guard"]+".npz")) == item["guard_sha256"]
        assert all(value is True for value in item["checks"].values())
    checks = {
        "all_392_npz_and_receipt_hashes_verified": True,
        "all_392_executor_and_case_identities_verified": True,
        "all_recorded_solver_gates_true": True,
        "all_21_state_names_and_8_nuclide_names_verified": True,
        "all_saved_data_finite": True,
        "two_corner_guard_evidence_hashes_verified": True,
        "fractions_nonnegative": min_fraction >= 0,
        "simplex_conservation": metrics["fraction_sum_max_abs_error"] <= 2e-9,
        "baryon_census": metrics["baryon_census_relative_error"] < 2e-12,
        "isotope_inventory": metrics["isotope_inventory_relative_error"] < 2e-12,
        "electron_census": metrics["electron_census_max_relative_error"] < 2e-12,
        "structural_zero_n_T_high_Li": metrics["zero_n_T_inventory_abs"] == metrics["high_Li_fraction_abs"] == 0,
        "saved_norm_conventions": max(metrics[k] for k in metrics if "norm_or_sum" in k) < 2e-14,
        "signed_shear_reconstruction": metrics["signed_shear_reconstruction_abs_error"] < 2e-14,
        "photon_neutrino_stress_reconstruction": max(metrics["photon_stress_reconstruction_abs_error"], metrics["neutrino_stress_reconstruction_abs_error"]) < 2e-14,
        "component_shear_budget": metrics["budget_max_abs_residual"] <= 3e-8,
        "optical_depth_monotone": min_tau_increment >= -2e-12,
        "sampled_brightness_nonnegative": min_brightness >= 0,
        "freezeout_density_and_time_envelope": metrics["proper_baryon_max_cm3"] < .01 and extrema["elapsed_s"]["max"] < 1.1e17,
    }
    report = {"schema": "he32.completed_physics_readback.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_SCOPED_SAVED_DATA_READBACK" if all(checks.values()) else "FINDING",
        "science_ivp_runs": 0, "benchmark_runs": 0, "scientific_source_edits": 0,
        "recovery_context": "Original 394-IVP outputs were lost during a scratch reset after a blocked backup. This report reads the actual recovered execution arrays; prior tool-output numbers are comparison references only, not restored raw evidence.",
        "source_executor_identity_sha256": executor_id,
        "catalog_sha256": sha(catalog_path), "readback_script_sha256": sha(__file__),
        "science_sources": source_hashes, "cases": 392, "samples_per_case": 201,
        "saved_time_samples_read": total_samples,
        "normalization": {"n_H1_z0_m3": nh0, "baryons_per_H": baryons_per_H,
            "Y_He4_reconstructed": 4*r4/baryons_per_H, "H_ref_per_s": href,
            "mass_convention": "A*m_u baryon census", "atomic_mass_kg": atomic_mass,
            "pi_m_scope": "nonbaryonic collisionless sector, mass fraction 0.1 of Omega_m; separate baryonic gas closure pi_b=0",
            "radiation_norm": "abs(P_gamma+P_nu), with signed components summed first",
            "redshift": "mean 1/a-1; not directional observed redshift",
            "elapsed_time": "proper time elapsed since mean z20; not absolute age"},
        "inventory": [{"name": name, "A": int(a), "Z": int(z), "states": int(z)+1, "ratio_per_H1": float(r)}
                for name,a,z,r in zip(NUCLEI, AS, ZS, ratios)],
        "checks": checks, "maximum_errors_and_envelope": metrics,
        "minimum_ion_fraction": min_fraction, "minimum_sampled_brightness": min_brightness,
        "minimum_tau_increment": min_tau_increment, "endpoint_extrema": extrema,
        "saved_history_extrema": history_extrema, "initial_grid": catalog["grid"],
        "shear_sign_reversal": {"threshold": 1e-15, "count": len(sign_reversal_cases), "cases": sign_reversal_cases,
            "negative_endpoint_count": sum(row["endpoint"]["signed_Sigma"] < -1e-15 for row in rows)},
        "angular_guard_record": {"path": "results/ANGULAR_GUARDS.json", "sha256": sha(guard_path),
                                 "evidence": angular, "recomputed_IVPs": 0},
        "isotropic_reference": iso_report, "strong_shear_comparisons": comparisons,
        "previous_lost_output_scalar_comparison": previous_comparison,
        "scope_limits": ["Selected primordial positive atomic species through Li: n,H,D,T,He3,He4,Li6,Li7 with21 charge populations; not every nuclear isotope or every chemical species.",
            "Photo plus total RR only; prescribed T=20000K and external GammaHI=1e-12 expit((6-z)/0.3), E5.392..60eV. No observational fit.",
            "n=T=0; LiIII/IV=0 because of initial conditions, bounded UV support and absent electron-impact ionization; these zeros do not represent universal cosmic absence.",
            "Nuclear freezeout is conditional on the documented S-factor envelope, density, temperature and duration; arbitrary19-channel nuclear source evolution is not computed.",
            "Algebraic consistency of saved arrays and two L16/L24 corner guards do not constitute a global truncation or physical-model error certificate.",
            "Matter stress is not an isotope-resolved baryonic anisotropic stress; isotropic atomic closure is an additional assumption beyond non-tilted geometry.",
            "Radiation brightness positivity is checked on201 saved times and257 angles; no all-time/all-angle theorem follows from it.",
            "This readback does not independently reconstruct the massive-sector phase-space quadrature or re-solve any evolution equation."],
        "input_files": inputs}
    output = args.out / "COMPLETED_PHYSICS_READBACK.json"
    atomic_text(output, json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+"\n")
    write_report(args.out / "COUPLED_PHYSICS_REPORT_KO.md", report)
    print(json.dumps({"status": report["status"], "cases": report["cases"],
        "output": str(output), "max_census_error": metrics["electron_census_max_relative_error"],
        "max_budget_residual": metrics["budget_max_abs_residual"],
        "source_identity": executor_id}, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


def write_report(path, r):
    e, m, iso = r["endpoint_extrema"], r["maximum_errors_and_envelope"], r["isotropic_reference"]
    f = iso["ion_fraction_endpoint"]
    lines = ["# HE32 완료 pilot의 독립 물리 readback", "",
        "## 판정과 근거", "",
        f"**{r['status']}**. 실제 복구 실행의 392개 nominal NPZ와 각각의 receipt를 모두 읽었다. "
        f"z=20→2의 201개 저장 시점, 총 {r['saved_time_samples_read']:,}개 case–time에서 "
        "21개 핵종·전하 population, 전자 census, Frobenius norm 및 응력별 shear budget을 재구성했다. "
        "이 검토는 새 IVP 0회, 성능 benchmark 0회, 과학 소스 수정 0건이다.", "",
        "원 실행의 394개 IVP 및 그림은 완료 뒤 백업 호출 정지와 scratch reset 사이에 사라졌다. "
        "이 보고서는 같은 P2 과학 코드와 입력으로 다시 만든 실제 결과 파일을 읽는다. "
        "이전 도구 출력에 남은 요약 숫자는 JSON의 별도 비교 항목에 보존하며 원 NPZ가 복원되었다고 표시하지 않는다.", "",
        f"- CATALOG SHA256: `{r['catalog_sha256']}`",
        f"- 과학 executor identity: `{r['source_executor_identity_sha256']}`",
        f"- readback script SHA256: `{r['readback_script_sha256']}`",
        "- 각 NPZ/receipt의 SHA256 및 392개 case identity: `COMPLETED_PHYSICS_READBACK.json`의 `input_files`.",
        "- 선행 이론: `HE32_THEORY_KO.md`, 원자·조성 입력: `data/ATOMIC_PHOTO_RR.json`, `data/ISOTOPE_SCENARIO.json`.",
        "- Jacobian 독립 검토의 최초 실패와 수선: `evidence/coupled/independent_v1/` 및 `independent_v2/`; 실패 기록을 유지한다.", "",
        "## 1. 계산 범위와 넓은 sweep", "",
        "초기값은 Σ₀의 8개 값 `[0, 10⁻⁴, 10⁻³, 0.01, 0.03, 0.1, 0.3, 0.6]`, "
        "signed Pₘ₀의 7개 값 `[-0.0006,-0.0003,-0.0001,0,0.0001,0.0003,0.0012]`, "
        "signed Pᵣ₀의 7개 값 `[-0.0024,-0.001,-0.0003,0,0.0003,0.001,0.0048]`의 곱이다. "
        "총392개이며, 초기 각분포의 양성성 범위 안에서 방향이 다른 stress와 shear를 함께 비교한다. "
        "강한Σ₀=0.6은 반응이 보이는 예비 시나리오이며 관측적으로 허용된 초기 우주 값이라는 주장이 아니다.", "",
        "| z=2 관측량 | 최소 | 최대 | 최대 case |", "|---|---:|---:|---|" ]
    for key in ("Sigma_F", "signed_Sigma", "Pi_m", "Pi_r", "Pi_total", "tau_T", "ne_cm3", "elapsed_s"):
        row = e[key]
        lines.append(f"| {key} | {row['min']:.12g} | {row['max']:.12g} | `{row['max_case']}` |")
    lines += ["", "시간축 z는 평균 scale factor의 `z=1/a−1`이고, elapsed time은 평균 z20 이후 흐른 고유시간이다. "
        "이는 절대 우주 나이나 모든 방향에 공통인 관측 적색편이가 아니다. "
        "LRS에서 방향별 적색편이는 방출·관측 시점의 β 차이에도 의존한다. "
        "그림은 계산된 시점의 값을 사용하며 이산 7×7 parameter 위치를 연속 균일 격자의 좌표로 해석하지 않는다.", "",
        f"z20→2의 경과시간 범위는 {e['elapsed_s']['min']/3.15576e16:.9g}–{e['elapsed_s']['max']/3.15576e16:.9g} Gyr이다. "
        f"등방 기준의 잔류Σ={iso['endpoint']['Sigma_F']:.6g}는 수치 대조군의 잔류로 취급하며 물리적 최소 shear로 해석하지 않는다.", "",
        "## 2. shear와 응력의 부호·정규화", "",
        r"공간 정규직교 기저에서 $D=\mathrm{diag}(-1,-1,2)$, $\sigma=sD$, $\pi_X=p_XD$를 사용한다. 따라서",
        "", r"\[\Sigma_F=\sqrt6|s|/H,\qquad P_X=\kappa_T\sqrt6\,p_X/H^2,\qquad\kappa_T=8\pi G/c^2.\]", "",
        "H는 s⁻¹, 응력은 J m⁻³이다. 저장된 signedΣ는 √6s/H이며, tensor Frobenius normΣ는 그 절댓값이다. "
        "방사선은 `P_r=P_gamma+P_nu`를 먼저 만들고 `Pi_r=abs(P_r)`를 취한다. "
        "`Pi_total=abs(P_m+P_gamma+P_nu)`이며 서로 다른 성분의 norm을 먼저 더하지 않는다.", "",
        f"저장 state의 q와 H에서 재구성한 signedΣ의 최대 절대 차이는 {m['signed_shear_reconstruction_abs_error']:.4g}, "
        f"photon/neutrino E₂에서 직접 재구성한 Pγ/Pν의 최대 차이는 각각 "
        f"{m['photon_stress_reconstruction_abs_error']:.4g}/{m['neutrino_stress_reconstruction_abs_error']:.4g}이다. "
        f"±10⁻¹⁵의 표시 기준 양쪽을 통과하는 signed shear 반전 case는 {r['shear_sign_reversal']['count']}개다. "
        "norm만으로는 응력에 의한 상쇄나 방향 반전을 알 수 없으므로 signed history도 함께 보아야 한다.", "",
        "여기서 πₘ은 Ωₘ의10%를 차지하는 별도 collisionless nonbaryonic massive sector의 stress다. "
        "H/He/Li atomic gas는 추가 closure π_b=0을 사용한다. non-tilted라는 조건만으로 baryonic stress가0이라는 결론은 나오지 않는다. "
        "따라서 이 결과를 각 isotope의 비등방 압력을 직접 계산한 결과라고 해석하지 않는다.", "",
        "## 3. 21개 핵종·전하 상태와 전자 기여", "",
        "| 핵종 | A | 전하 q | 상태 수 | 핵종/H1 초기 abundance |", "|---|---:|---|---:|---:|"]
    for row in r["inventory"]:
        lines.append(f"| {row['name']} | {row['A']} | 0…{row['Z']} | {row['states']} | {row['ratio_per_H1']:.12g} |")
    lines += ["", "이는 선택한8개 원시 핵종의21개 중성·양이온 population이다. 짧은 수명의 모든 동위원소, 음이온, 분자까지 포함하는 총망은 아니다. "
        "n과T의 초기 abundance는0이다. Be7 late progenitor는 채택한Li7/H 조성에 포함한 초기조건이며 별도로 시간 적분하지 않는다. "
        "동위원소의 전자율과 초기 charge fraction을 같게 놓았으므로 9개 원소별 fraction slot이21개 population으로 정확히 올라간다. "
        "단순히 원소 목록만 저장하는 대신 모든 nonzero isotope의 전자가 photon opacity에 포함된다.", "",
        r"독립 재구성은 $n_e=n_{H,0}a^{-3}\sum_{A,q}qY_{A,q}$ 및 $n_b=n_{H,0}a^{-3}\sum_{A,q}AY_{A,q}$를 사용했다. "
        "밀도 변환 m⁻³→cm⁻³의10⁻⁶을 명시적으로 적용했다. A m_u baryon census이며 mass-defect EOS는 아니다.", "",
        f"- nH1(z0)={r['normalization']['n_H1_z0_m3']:.14g} m⁻³; baryons/H={r['normalization']['baryons_per_H']:.15g}.",
        f"- 전자 census 최대 상대 차이: {m['electron_census_max_relative_error']:.5g}.",
        f"- A-가중 baryon census 최대 상대 차이: {m['baryon_census_relative_error']:.5g}.",
        f"- 각 핵종 inventory 최대 상대 drift: {m['isotope_inventory_relative_error']:.5g}.",
        f"- 원소별 simplex 합 최대 오차: {m['fraction_sum_max_abs_error']:.5g}; 최소 저장 ion fraction={r['minimum_ion_fraction']:.5g}.", "",
        "### 등방 기준 case의 실제 z2 값", "",
        "기준은 `s00_m03_r03`이다. 다음 fraction은 동일 원소의 각 isotope에 공통으로 적용되지만 핵종 abundance와 전자 기여량은 다르다.", "",
        "| 이온 | z=2 charge fraction |", "|---|---:|"]
    for key, value in f.items():
        lines.append(f"| {key} | {value:.12g} |")
    lines += ["", f"총 ne={iso['endpoint']['ne_cm3']:.14g} cm⁻³에서 핵종별 전자 기여는 다음과 같다.", "",
        "| 핵종 | ne 기여 / 총 ne | 기여 cm⁻³ |", "|---|---:|---:|"]
    for name in NUCLEI:
        lines.append(f"| {name} | {iso['electron_contribution_fraction_endpoint'][name]:.12g} | {iso['electron_contribution_cm3_endpoint'][name]:.12g} |")
    peak = iso["Li_I_peak_saved_sample"]
    lines += ["", f"LiI fraction은 저장 시점 기준 평균z={peak['mean_z']:.8g}에서 최대 {peak['fraction']:.10g}가 되고 "
        f"z2에는 {f['Li_I']:.10g}까지 내려간다. LiII는 z2에 {f['Li_II']:.12g}이다. "
        "LiIII/IV는 전체392개 history에서 정확히0이다. 선택 UV 상한60eV가 LiII/LiIII의 다음 photoionization 문턱보다 낮고, "
        "초기 high-charge population과 electron-impact CI를0으로 놓았기 때문이다. 이0은 해당 시나리오의 해이며 우주에서 해당 이온이 "
        "항상 없다는 주장이 아니다.", "",
        "## 4. 물리 반응과 외부 closure의 영향", "",
        r"온도는 $T_g=20000\,K$, $\Gamma_{HI}=10^{-12}\operatorname{expit}[(6-z)/0.3]\,s^{-1}$로 고정한 외부 입력이다. "
        "photon-number spectrum은 E⁻²⋅⁵, support는5.392–60eV이다. Photoionization과 total RR(caseA)만 계산한다. "
        "CI/DR/charge exchange 누락의 작음을 입증한 오차계산은 아니다. 광원 및 열균형을 자체적으로 진화시키지 않으므로 "
        "H/He의 ionization 시점이나 τ를 관측 재이온화의 적합값으로 취급하지 않는다. Γ의 중심z6은 ion fraction의 중간값 위치와 동일하지 않다.", "",
        "| Σ₀=0.6 case | 등방 대비 ne history 최대 상대 변화 | 해당 평균z | z2 ne 상대 변화 | τ(z20→2) 차이 |",
        "|---|---:|---:|---:|---:|"]
    for row in r["strong_shear_comparisons"]:
        lines.append(f"| `{row['case_id']}` | {row['max_ne_history_relative_difference_from_isotropic']:.8g} | {row['mean_z_at_maximum']:.8g} | {row['ne_endpoint_relative_difference_from_isotropic']:.8g} | {row['tau_endpoint_difference_from_isotropic']:.8g} |")
    lines += ["", "끝점의 ne가 거의 같은 경우에도 ionization 전이 도중 targetH와 경과시간의 변화가 누적되어 history와 optical depth가 달라진다. "
        "따라서 z2 한 점만으로 화학·팽창 결합의 크기를 판단하지 않는다. 이 비교는 선택한 UV/temperature/입력 조성에 대한 결과다.", "",
        "## 5. source budget, 보존량과 검증의 범위", "",
        r"$\eta=\ln(a/a_{20})$, $q=s/H_{ref}$에서 $I_s=e^{3\eta}q$를 정의했다. "
        r"진화방정식과 함께 적분한 성분은 $I_X'=e^{3\eta}(H/H_{ref})P_X/\sqrt6$이며",
        "", r"\[I_s=I_{s,0}+I_m+I_\gamma+I_\nu\]", "",
        f"이다. 저장 state의 세 budget을 다시 더했을 때 최대 절대 residual은 {m['budget_max_abs_residual']:.12g} "
        "(기존 gate3×10⁻⁸)이다. 이는 저장 history의 사후 trapezoid 적분이 아니다. "
        "다만 단일 conservation residual이 각 성분의 독립 정확도를 모두 인증하지는 않는다.", "",
        f"샘플 brightness 최소={r['minimum_sampled_brightness']:.12g}, τ의 최소 증가분={r['minimum_tau_increment']:.12g}. "
        "양성성은201개 저장 시점과257개 각도에서 확인한 것이며 전 시간·전 각도의 증명과 구별한다. "
        "L16/L24의 두 강한-shear corner 비교는 `results/ANGULAR_GUARDS.json`에 보존하며 전체 sweep의 엄밀한 resolution bound가 아니다.", "",
        f"proper baryon density 최대={m['proper_baryon_max_cm3']:.12g} cm⁻³<0.01, "
        f"경과시간 최대={e['elapsed_s']['max']:.12g} s<1.1×10¹⁷ s로 theory의 freezeout density/time 조건 안에 있다. "
        "핵융합 감소의 S(E)≤10⁶keV barn envelope와 온도 조건은 여전히 명시적 가정이다. "
        "이 결과를 arbitrary19-channel fully reactive nuclear network 실행으로 재표시하지 않는다.", "",
        "## 6. 재현 및 다음 DAG", "",
        "다음 명령은 저장된 데이터를 읽고 이 두 보고서를 다시 만든다. 과학 solver를 import하거나 IVP를 실행하지 않는다.", "",
        "```bash", "python research/he32_sandbox_primordial_20261021/evidence/physics/code/completed_physics_readback.py", "```", "",
        "현재 DAG는 `F.C8 실제 recovery pilot → F.C9 saved-data 물리 readback/그림 검토 → F.C10 최종 evidence/backup/publication`이다. "
        "이 분담 검토의 산출물은 두 보고서와 readback 스크립트이며 외부 push·백업 성공 여부는 parent의 publication/backup receipt를 따른다. "
        "사용자가 선택한 광원·열·충돌 closure를 확장할 때는 해당 의존성을 새로운 연구 단위로 다룬다.", ""]
    atomic_text(path, "\n".join(lines))


if __name__ == "__main__":
    main()
