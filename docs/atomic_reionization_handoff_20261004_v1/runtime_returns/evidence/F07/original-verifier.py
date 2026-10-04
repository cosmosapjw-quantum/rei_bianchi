"""Pre-output validator for the explicitly prescribed REI S0 experiment.

Schema and analytic source/geometry screening only; no chemistry/history or
physical accuracy inference. Uses Decimal(80) independently of the Rust API.
"""
import argparse
from decimal import Decimal as D, localcontext
import json
import math
from pathlib import Path


def require(condition, label):
    if not condition:
        raise ValueError(label)


def validate(value, spec, path="scenario"):
    kind = spec.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool,
             "null": type(None), "number": (int, float)}
    require(isinstance(value, types[kind]), path + ": type")
    if kind == "number":
        require(not isinstance(value, bool) and math.isfinite(value), path + ": finite")
    if kind == "object":
        require(all(k in value for k in spec["required"]), path + ": missing field")
        require(set(value) <= set(spec["properties"]), path + ": extra field")
        for key, item in value.items():
            validate(item, spec["properties"][key], path + "." + key)
    if kind == "array":
        require(spec["minItems"] <= len(value) <= spec["maxItems"], path + ": shape")
        for item in value:
            validate(item, spec["items"], path + "[]")
    if kind == "string":
        require(len(value) >= spec["minLength"], path + ": empty")


def screen(c):
    require(c["schema"] == "rei.science-scenario.v1" and c["task_id"] == "REI-F07", "identity")
    require(c["classification"] == "NON_OBSERVATIONAL_PRESCRIBED_BACKGROUND_EXPERIMENT", "scope")
    require(c["preregistration"]["before_paired_anisotropy_observables"], "pre-output")
    require(c["preregistration"]["tuning_after_outputs"] == "FORBIDDEN", "no tuning")
    require(not c["outputs"]["observational_reproduction"], "claim ceiling")
    require(c["outputs"]["physical_claim"] == "HOLD", "physical HOLD")
    require(c["background"]["tilt"] == [0., 0., 0.], "zero tilt")
    require(c["source"]["multipoles"] == {"dipole": [0.,0.,0.], "quadrupole": [[0.,0.,0.]]*3}, "isotropic source")
    require(c["source"]["kind"] == "COMPACT_MONOCHROMATIC", "compact-source formula")
    require(c["source"]["family"] == "S0", "source family")
    require(c["atomic_model"]["closure"] == "HOMOGENEOUS_BOUND_FREE_PRIMARY_ONLY_EXPLICIT_CASE_A_ESCAPE", "closure")
    require(c["atomic_model"]["rate_moment_id"] == "REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1", "rate identity")
    require(c["atomic_model"]["optional_HH_direct"].startswith("OFF") and c["atomic_model"]["optional_He_RCT"].startswith("OFF"), "optional channels off")
    require(c["spectral"]["lower_ownership"] == "RETAIN_BELOW_THRESHOLD_NUMBER_AND_ENERGY", "no edge double count")
    require(c["secondary"]["physical_effect_bound"] == "NOT_MEASURED", "no invented secondary bound")
    require(c["atomic_model"]["physical_fit_uncertainty"].startswith("NOT_MEASURED"), "no invented fit bound")
    decimal = lambda x: D(str(x))
    with localcontext() as ctx:
        ctx.prec = 80
        t0, tend = (decimal(c["time"][k]) for k in ("t0_s", "t_end_s"))
        require(t0 == 0 and tend > 0, "time")
        require(c["source"]["time_support_s"] == [float(t0), float(tend)], "source time support")
        require(c["source"]["photons_per_H_per_s"] > 0 and c["initial_state"]["photon_number_per_H"] >= 0, "source normalization")
        require(c["initial_state"]["photon_energy_ev"] == c["source"]["energy_at_birth_ev"], "initial spectrum")
        energy = decimal(c["source"]["energy_at_birth_ev"])
        lo, hi = (decimal(c["spectral"][k]) for k in ("E_min_ev", "E_max_ev"))
        require(0 < lo < energy < hi, "source support")
        edges = list(map(decimal, c["spectral"]["mandatory_energy_edges_ev"]))
        thresholds = list(map(decimal, c["constants"]["provider_threshold_ev"]))
        require(c["constants"]["provider_threshold_ev"] == [13.5984346,24.587389,54.41776], "existing provider thresholds")
        require(all(x < y for x,y in zip(edges, edges[1:])), "edge order")
        require(edges[0] == lo and hi in edges and all(x in edges for x in thresholds), "support and threshold ownership")
        require(thresholds[0] < energy < thresholds[1], "soft HI-only photo source")
        fits = list(map(decimal,c["atomic_model"]["fit_implementation_temperature_guard_K"]))
        guard = list(map(decimal,c["atomic_model"]["scenario_temperature_guard_K"]))
        require(D(0) < fits[0] <= guard[0] < decimal(c["initial_state"]["temperature_K"]) < guard[1] <= fits[1], "temperature domains")
        fractions = c["initial_state"]["fractions"]
        require(all(0 <= x <= 1 for x in fractions.values()), "populations")
        require(sum(decimal(fractions[k]) for k in ["HeI","HeII","HeIII"]) == 1, "He closure")
        require(all(x == 1 for x in c["background"]["a0"]), "reference volume")
        n0, fhe = decimal(c["initial_state"]["nH0_cm3"]), decimal(c["initial_state"]["fHe"])
        require(n0 > 0 and fhe > 0, "FT03 nuclear densities")
        ref = c["time"]["refinement_dt_s"]
        require(ref[0] == c["time"]["initial_trial_dt_s"] and ref[1] == ref[0]/2 and ref[2] == ref[1]/2, "fixed refinement")
        require(0 < c["time"]["minimum_trial_dt_s"] <= ref[-1] <= tend, "step domain")
        require(c["numerics"]["strict_local_error_limit"] == 2e-4 and c["numerics"]["strict_public_width_limit"] == 2e-3, "old strict limits")
        rows = []
        mean = decimal(c["background"]["H_mean_per_s"])
        epsilon = decimal(c["background"]["epsilon"])
        require(0 < epsilon < 1 and mean > 0, "geometry input")
        require(list(map(decimal,c["background"]["pairs"]["FLRW"]["H_per_s"])) == [mean]*3, "FLRW")
        require(list(map(decimal,c["background"]["pairs"]["BIANCHI_I"]["H_per_s"])) == [mean*(1+epsilon),mean*(1-epsilon),mean], "fixed Bianchi rates")
        for name, pair in c["background"]["pairs"].items():
            rates = list(map(decimal, pair["H_per_s"]))
            require(len(rates) == 3 and min(rates) > 0 and sum(rates) == 3*mean, "paired mean/rate")
            scales = [(h*tend).exp() for h in rates]
            volume = (sum(rates)*tend).exp()
            emin = energy*(-max(rates)*tend).exp()
            require(emin > lo, "all old cohorts inside lower guard")
            z = (decimal(c["background"]["redshift"]["reference_z0"])+1)*(-mean*tend).exp()-1
            rows.append({"pair":name,"scale_end":[str(x) for x in scales],"volume_end":str(volume),"nH_end_cm3":str(n0/volume),"nHe_end_cm3":str(n0*fhe/volume),"oldest_cohort_E_lower_bound_ev":str(emin),"z_label_end":str(z),"HI_threshold_crossing_first_possible_s":str((energy/thresholds[0]).ln()/max(rates))})
        ne = n0*decimal(fractions["HII"])+n0*fhe*(decimal(fractions["HeII"])+2*decimal(fractions["HeIII"]))
        u0 = D('1.5')*decimal(c["constants"]["k_B_erg_K"])*decimal(c["initial_state"]["temperature_K"])*(n0+n0*fhe+ne)
        source_integral = decimal(c["source"]["photons_per_H_per_s"])*tend
        require(all(decimal(c["spectral"][k]) > 0 for k in ("source_tail_number_tolerance","source_tail_energy_tolerance")), "tail tolerances")
        return {"status":"PASS","task_id":"REI-F07","scope":"Schema and analytic pre-output screening only","source_tail_number_fraction":"0","source_tail_energy_fraction":"0","tail_basis":"Exact prescribed compact Dirac support, not a physical SED error bound","source_integral_photons_per_H":str(source_integral),"birth_energy_ev":str(energy),"HI_photoelectron_excess_ev":str(energy-thresholds[0]),"initial_electron_density_cm3":str(ne),"initial_thermal_erg_cm3":str(u0),"geometry_screen":rows,"temperature_guard":"PRESCRIBED_NOT_PROVEN_INVARIANT","secondary_accuracy":"NOT_MEASURED","physical_accuracy":"NOT_MEASURED","paired_histories_run":False,"scientific_admission":"HOLD"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="configs/rei_fastest_v1/science_scenario_v1.json")
    parser.add_argument("--schema", default="configs/rei_fastest_v1/science_scenario_v1.schema.json")
    parser.add_argument("--output")
    args = parser.parse_args()
    config = json.loads(Path(args.scenario).read_text())
    validate(config, json.loads(Path(args.schema).read_text()))
    result = json.dumps(screen(config), indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(result)
    print(result, end="")
