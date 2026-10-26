"""Affected native REC callback controls at one matched PW19 donor snapshot."""
import json
import math
import os
from pathlib import Path

import numpy as np

from matched_snapshot import read_matched_snapshot
from pw19_rec_callback import (BANDS, CHI_EV, EVENT_OWNER, HEII, HEIII,
                               ISOTOPE_POLICY, ROUTE, PW19HeIINetwork, EV_J,
                               C_M_S, MOMENTS_SHA256)


def _array(values):
    return np.asarray(values).tolist()


def run():
    network = PW19HeIINetwork(source_z=2.479, source_route=ROUTE,
                              isotope_policy=ISOTOPE_POLICY,
                              photo_owners=(EVENT_OWNER,))
    snap = read_matched_snapshot(network)
    y, t, nb = snap["Y"], snap["temperature_K"], snap["nb_m3"]
    on = network.evaluate(y,t,1.0,nb)
    off = network.evaluate(y,t,0.0,nb)
    rates = network.rates(t,1.0)
    ledger = network.selected_photo_ledger(y,nb)
    checks = []

    def check(name, residual, limit):
        checks.append({"name":name, "residual":float(residual), "limit":limit,
                       "pass":bool(math.isfinite(residual) and residual <= limit)})

    def reject(call, exception=ValueError):
        try:
            call()
        except exception:
            return True
        return False

    def scaled(a,b,scale):
        assert scale > 0 and math.isfinite(scale)
        return float(np.max(np.abs(np.asarray(a)-np.asarray(b)))/scale)

    assert y.shape == (21,) and np.all(np.isfinite(y)) and np.all(y >= 0)
    check("source_node_and_exact_native_mapping", 0.0 if (snap["source_z"] == 2.479 and
          tuple(network.names[i] for i in (8,9,11,12)) ==
          ("He3II","He3III","He4II","He4III") and
          all(network.transition_energy_eV[i] == CHI_EV for i in HEII)) else math.inf, 0.0)
    check("matched_baryon_normalization", abs(float(network.A@y)-1.0), 2e-14)
    check("matched_density_xY", scaled(nb*y,snap["reference_density_m3"]*snap["x_per_Href"],nb), 2e-14)
    check("matched_free_electron_count", abs(on["ne"]-snap["reference_density_m3"]*float(network.q@snap["x_per_Href"]))/on["ne"], 2e-14)
    check("matched_temperature_native_range", 0.0 if 100 <= t <= 1e6 else math.inf, 0.0)
    check("nT_actual_zero", 0.0 if all(y[i] == 0 for i in (0,5,6)) else math.inf, 0.0)
    check("matched_geometry_finite_positive_H",0.0 if snap["geometry"]["H_s_inverse"]>0 and all(math.isfinite(v) for v in snap["geometry"].values()) else math.inf,0.0)
    eps128 = 128*np.finfo(float).eps
    for name,group in snap["isotope_totals"].items():
        left,right = group["endpoints"]
        expect = (1-snap["theta"])*left+snap["theta"]*right
        scale = (1-snap["theta"])*abs(left)+snap["theta"]*abs(right)
        residual = abs(group["snapshot"]-expect)/scale if scale>0 else (0.0 if group["snapshot"]==0 else math.inf)
        check(f"matched_{name}_convex_inventory",residual,eps128)
    check("other_photo_routes_deselected", 0.0 if all(network._photo_s[i] == 0 for i in range(21) if i not in HEII) else math.inf, 0.0)
    check("native_rates_and_evaluate_inherited", 0.0 if all(getattr(PW19HeIINetwork,key) is getattr(network.__class__.__bases__[0],key) for key in ("rates","evaluate")) else math.inf, 0.0)

    source = network.admitted_moments
    parts = source["partition_moments"]
    check("source_bands_exact", 0.0 if tuple(tuple(p["band_eV"]) for p in parts) == BANDS else math.inf, 0.0)
    for i,p in enumerate(parts):
        check(f"band_{i}_incident_Phi_SI", abs(network.photon_flux_bins_base[i]-p["Phi_cm2_s"]*1e4)/(p["Phi_cm2_s"]*1e4), 2e-14)
        check(f"band_{i}_number_rate", abs(network.photo_sigma_m2[8,i]*network.photon_flux_bins_base[i]-p["Gamma_s"])/p["Gamma_s"], 2e-14)
        check(f"band_{i}_energy_partner", abs(math.fsum((ledger["bands"][i]["binding_W_m3"],ledger["bands"][i]["primary_W_m3"],ledger["bands"][i]["external_radiation_W_m3"])))/(-ledger["bands"][i]["external_radiation_W_m3"]), 2e-14)
    mean_flux_energy = float(network.photon_flux_bins_base @ (network.photon_energy_eV*EV_J))
    exact_psi = math.fsum(p["Psi_eV_cm2_s"]*1e4*EV_J for p in parts)
    check("mean_only_exact_energy_density", abs(mean_flux_energy-exact_psi)/exact_psi, 2e-14)
    check("native_energy_density_diagnostic", abs(on["uv_energy_density_J_m3"]-mean_flux_energy/C_M_S)/(mean_flux_energy/C_M_S), 2e-14)
    check("full_rate_reused", abs(network.selected_Gamma_s-source["full_atomic_moments"]["Gamma_s"])/source["full_atomic_moments"]["Gamma_s"], 2e-14)
    check("no_core_or_inner_shell", 0.0 if all(np.count_nonzero(a) == 0 for a in
          (network._core_W,network._li1s_photo_s,network._inner_absorbed_W)) else math.inf, 0.0)
    check("unknown_atomic_tail_null", 0.0 if ledger["radiation_above_atomic_domain"]["HeII_primary_Gamma_s"] is None else math.inf, 0.0)
    check("primary_not_heat", 0.0 if ledger["primary_is_thermal_heat"] is False else math.inf, 0.0)

    gy = network._Gphoto@y
    event = network.selected_Gamma_s*float(y[list(HEII)].sum())
    check("native_photo_RHS", scaled(on["photo_rhs"],gy,event), 2e-14)
    check("source_on_off_RHS", scaled(on["dY_dt"]-off["dY_dt"],gy,event), 2e-8)
    check("source_on_off_Jacobian", scaled(on["jac"]-off["jac"],network._Gphoto,network.selected_Gamma_s), 2e-8)
    check("source_off_exact", 0.0 if np.count_nonzero(off["photo_rhs"]) == 0 else math.inf, 0.0)
    check("RR_DR_decay_unchanged", scaled(on["rr_rhs"]+on["dr_rhs"]+on["decay_rhs"],off["rr_rhs"]+off["dr_rhs"]+off["decay_rhs"],max(float(np.max(np.abs(off["dY_dt"]))),event)), 0.0)
    for name,indices in network.isotope_groups.items():
        check(f"photo_{name}_nuclei", abs(float(np.sum(gy[list(indices)])))/event, 2e-14)
    check("photo_baryons", abs(float(network.A@gy))/event, 2e-14)
    check("photo_electron_event", abs(float(network.q@gy)-event)/event, 2e-14)
    check("proper_SI_photo_electron", abs(nb*event-ledger["total"]["events_m3_s"])/ledger["total"]["events_m3_s"], 2e-14)
    check("proper_SI_external_energy", abs(math.fsum((ledger["total"]["binding_W_m3"],ledger["total"]["primary_W_m3"],ledger["total"]["external_radiation_W_m3"])))/(-ledger["total"]["external_radiation_W_m3"]), 2e-14)
    check("native_absorption_diagnostic", abs(on["photo_absorbed_power_W_m3"]+ledger["total"]["external_radiation_W_m3"])/on["photo_absorbed_power_W_m3"], 2e-14)
    check("native_primary_diagnostic", abs(on["primary_kinetic_power_W_m3"]-ledger["total"]["primary_W_m3"])/on["primary_kinetic_power_W_m3"], 2e-14)

    h = 1e-4
    v_a = np.zeros(21)
    for indices in ((7,8,9),(10,11,12)):
        total = float(np.sum(y[list(indices)]))
        v_a[indices[1]] = -.1*total
        v_a[indices[2]] = +.1*total
    v_b = np.zeros(21); v_b[1] = -1e-5; v_b[2] = 1e-5
    beta = snap["beta_baryons_per_Href"]
    x = snap["x_per_Href"]
    r = snap["reference_density_m3"]
    d = (np.eye(21)-np.outer(y,network.A))/beta
    check("projective_A_left_null",float(np.max(np.abs(network.A@d)))*beta/max(float(np.max(network.A)),1.0),eps128)
    check("projective_radial_null",scaled(d@x,np.zeros(21),float(np.max(np.abs(y)))),eps128)
    check("projective_idempotent",scaled((beta*d)@(beta*d),beta*d,float(np.max(np.abs(beta*d)))),eps128)
    dx = beta*v_a
    dr = .3
    dbeta = float(network.A@dx)
    dy = (dx-y*dbeta)/beta
    dnb = beta*dr+r*dbeta
    reconstructed = dnb*y+nb*dy
    expected_reconstruction = r*dx+x*dr
    check("variable_inventory_reconstruction_JVP",scaled(reconstructed,expected_reconstruction,float(np.max(np.abs(expected_reconstruction)))),eps128)
    check("fixed_isotope_direction_maps",scaled(dy,v_a,float(np.max(np.abs(v_a)))),eps128)
    jvp = {}
    for label,v in (("helium",v_a),("hydrogen_electron_feedback",v_b)):
        plus = network.evaluate(y+h*v,t,1.0,nb)
        minus = network.evaluate(y-h*v,t,1.0,nb)
        reference = on["jac"]@v
        if label == "hydrogen_electron_feedback":
            assert np.count_nonzero(network._Gphoto@v) == 0
            fd = ((plus["rr_rhs"]+plus["dr_rhs"]+plus["decay_rhs"])-
                  (minus["rr_rhs"]+minus["dr_rhs"]+minus["decay_rhs"]))/(2*h)
        else:
            fd = (plus["dY_dt"]-minus["dY_dt"])/(2*h)
        scale = float(np.max(np.abs(reference)))
        check(f"full_native_{label}_JVP", scaled(fd,reference,scale), 2e-8)
        check(f"native_{label}_electron_tangent", abs(nb*float(network.q@v)-(plus["ne"]-minus["ne"])/(2*h))/abs(nb*float(network.q@v)), 2e-8)
        jvp[label] = {"direction":_array(v),"analytic":_array(reference),
                       "finite_difference":_array(fd)}
    rmat = rates["Gne"]
    nb_direction = float(network.q@y)*(rmat@y)
    nb_plus = network.evaluate(y,t,1.0,nb+h)
    nb_minus = network.evaluate(y,t,1.0,nb-h)
    nb_fd = ((nb_plus["rr_rhs"]+nb_plus["dr_rhs"]+nb_plus["decay_rhs"])-
             (nb_minus["rr_rhs"]+nb_minus["dr_rhs"]+nb_minus["decay_rhs"]))/(2*h)
    check("native_nb_JVP", scaled(nb_fd,nb_direction,float(np.max(np.abs(nb_direction)))), 2e-8)
    lam_plus = network.evaluate(y,t,1+h,nb)
    lam_minus = network.evaluate(y,t,1-h,nb)
    lam_fd = (lam_plus["dY_dt"]-lam_minus["dY_dt"])/(2*h)
    check("native_lambda_JVP",scaled(lam_fd,gy,event),2e-8)
    for label,v,dn,dl in (("Y",v_a,0.,0.),("density",np.zeros(21),.3,0.),
                          ("amplitude",np.zeros(21),0.,.3)):
        tangent = network.selected_photo_ledger(y,nb,1.0,v=v,dnb=dn,damplitude=dl)
        ds = float(v[list(HEII)].sum())
        s = float(y[list(HEII)].sum())
        factor = nb*ds+s*dn+nb*s*dl
        for k,coefficient in (("events_m3_s",network.selected_Gamma_s),
                              ("binding_W_m3",network.selected_binding_J_s),
                              ("primary_W_m3",network.selected_K_J_s),
                              ("external_radiation_W_m3",-network.selected_A_J_s)):
            actual = tangent["total"]["tangent_"+k]
            expected = factor*coefficient
            check(f"{label}_{k}_energy_JVP",abs(actual-expected)/abs(expected),2e-14)

    check("wrong_z_rejected",0.0 if reject(lambda: PW19HeIINetwork(source_z=20,source_route=ROUTE,isotope_policy=ISOTOPE_POLICY,photo_owners=(EVENT_OWNER,))) else math.inf,0.0)
    check("isotope_policy_required",0.0 if reject(lambda: PW19HeIINetwork(source_z=2.479,source_route=ROUTE,isotope_policy="missing",photo_owners=(EVENT_OWNER,))) else math.inf,0.0)
    check("duplicate_owner_rejected",0.0 if reject(lambda: PW19HeIINetwork(source_z=2.479,source_route=ROUTE,isotope_policy=ISOTOPE_POLICY,photo_owners=(EVENT_OWNER,EVENT_OWNER))) else math.inf,0.0)
    check("cutoff_rejected",0.0 if reject(lambda: PW19HeIINetwork(source_z=2.479,source_route=ROUTE,isotope_policy=ISOTOPE_POLICY,photo_owners=(EVENT_OWNER,),uv_cutoff_eV=200)) else math.inf,0.0)
    check("full_150eV_grid_rejected",0.0 if reject(lambda: network.certify_full_kinetic_grid(150)) else math.inf,0.0)
    check("native_negative_nb_guard",0.0 if reject(lambda: network.evaluate(y,t,1,-1)) else math.inf,0.0)
    check("native_shape_guard",0.0 if reject(lambda: network.evaluate(y[:-1],t,1,nb)) else math.inf,0.0)
    check("unknown_uncertainties_null",0.0 if all(ledger["uncertainty_ledger"].get(k) is None for k in
          ("provider_uncertainty","physical_model_uncertainty","interpolation_error_relative_to_unprovided_continuum","isotope_rate_uncertainty")) else math.inf,0.0)

    control = np.array(network.initial_Y,copy=True)
    for indices in ((7,8,9),(10,11,12)):
        total = float(control[list(indices)].sum())
        control[list(indices)] = np.array((.2,.5,.3))*total
    control_eval = network.evaluate(control,10000,1,1.0)
    check("secondary_control_uses_native_callback",0.0 if np.all(np.isfinite(control_eval["dY_dt"])) and float(np.sum(control[list(HEII)]))>0 else math.inf,0.0)

    snapshot_record = {k:(_array(v) if isinstance(v,np.ndarray) else v) for k,v in snap.items()}
    raw = {"scope":"actual GRID044 adjacent-interpolated snapshot at PW19 z2.479; one local native callback, no trajectory",
           "snapshot":snapshot_record,
           "source":{"route":ROUTE,"isotope_policy":ISOTOPE_POLICY,"event_owner":EVENT_OWNER,
                     "source_sha256":source["source"]["spectrum_sha256"],
                     "admitted_moments_sha256":MOMENTS_SHA256,
                     "full_Gamma_s":network.selected_Gamma_s},
           "native_on":{"dY_dt":_array(on["dY_dt"]),"jac":_array(on["jac"]),
                        "ne_m3":on["ne"],
                        "radiation_energy_density_J_m3":on["uv_energy_density_J_m3"],
                        "radiation_energy_density_domain_eV":[54.42,50000.0],
                        "photo_rhs":_array(on["photo_rhs"]),
                        "rr_rhs":_array(on["rr_rhs"]),"dr_rhs":_array(on["dr_rhs"]),
                        "decay_rhs":_array(on["decay_rhs"])},
           "native_off":{"dY_dt":_array(off["dY_dt"]),"jac":_array(off["jac"]),
                         "photo_rhs":_array(off["photo_rhs"])},
           "source_on_off_dY_dt":_array(on["dY_dt"]-off["dY_dt"]),
           "analytic_photo_action":_array(gy),
           "JVP":jvp,"ledger":ledger,
           "secondary_arithmetic_control":{"label":"native_initial_inventory_redistributed_He_not_cosmological_state",
                                           "Y":_array(control),"dY_dt":_array(control_eval["dY_dt"])},
           "limitations":{"no_IVP":True,"no_history_claim":True,
                          "gas_heat_from_primary":None,
                          "continuum_state_interpolation_accuracy":None,
                          "source_time_derivative":None}}
    return raw,{"passed":all(c["pass"] for c in checks),"check_count":len(checks),"checks":checks}


if __name__ == "__main__":
    output = Path(os.environ["PW19_REC_OUTPUT_DIR"])
    raw, validation = run()
    (output/"CALLBACK.json").write_text(json.dumps(raw,indent=2,allow_nan=False)+"\n")
    (output/"CHECKS.json").write_text(json.dumps(validation,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"passed":validation["passed"],"check_count":validation["check_count"],
                      "failed":[x for x in validation["checks"] if not x["pass"]]},allow_nan=False))
    raise SystemExit(0 if validation["passed"] else 1)
