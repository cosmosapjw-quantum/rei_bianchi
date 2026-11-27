"""Reproduce HE32 source-oracle comparison and conditional physics bounds.

This is a short derivation calculator, not a performance benchmark or a new
cosmological solver.  Run from any working directory; outputs remain beside
the theory note.  All upper bounds carry the assumptions that make them true.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.constants import G, c, k, atomic_mass, electron_volt, fine_structure

from atomic_photo_rr import AtomicPhotoRR

BASE = Path(__file__).resolve().parents[1]


def write(name, payload):
    (BASE/name).write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n")


def main():
    p = AtomicPhotoRR()
    coeff = p.rates(20000., 1.e-12)
    wl = json.loads((BASE/"WOLFRAM_ATOMIC_ORACLE.json").read_text())
    raw = wl["result"]["content"][0]["text"]
    oracle = json.loads(json.loads(raw.removeprefix("Out[1]= ")))
    wl_rr = np.asarray(oracle["rr_20k_cm3_s"])
    wl_photo = np.asarray(oracle["photo_ratios"])
    oracle_comparison = {
        "schema": "he32.atomic_source_oracle_comparison.v1",
        "data_sha256": p.data_sha256,
        "code_sha256": hashlib.sha256((BASE/"code/atomic_photo_rr.py").read_bytes()).hexdigest(),
        "method": "independent Wolfram Language exact-decimal source transcription, 40-digit adaptive integration, versus binary64 NumPy Gauss-Legendre implementation",
        "rr_max_relative_error": float(np.max(np.abs(coeff["recombination_cm3_s"]/wl_rr-1))),
        "photo_ratio_max_absolute_error": float(np.max(np.abs(p.photo_ratios-wl_photo))),
        "rr_20k_cm3_s": coeff["recombination_cm3_s"].tolist(),
        "photo_ratios": p.photo_ratios.tolist(),
        "rr_tolerance": 2.e-14,
        "photo_ratio_tolerance": 2.e-12,
    }
    oracle_comparison["result"] = "pass_scoped" if (
        oracle_comparison["rr_max_relative_error"] < oracle_comparison["rr_tolerance"]
        and oracle_comparison["photo_ratio_max_absolute_error"] < oracle_comparison["photo_ratio_tolerance"]
    ) else "fail"
    write("ATOMIC_SOURCE_ORACLE_COMPARISON.json", oracle_comparison)

    tmax = 20000.
    mu = 2/3*atomic_mass
    smax = 1.e6*1.e3*electron_volt*1.e-28  # 1e6 keV barn -> J m^2
    eg = 2*mu*c*c*(math.pi*fine_structure)**2
    exponent = 3*(eg/(8*k*tmax))**(1/3)
    rate = 2*math.sqrt(8/(math.pi*mu))*smax/math.sqrt(k*tmax)*math.exp(-exponent)*1.e6
    # H^2 >= H0^2 [(1-fm) Omega_m] a^-3 for positive remaining sectors.
    # The exact dust-only time upper bound is 1.043600894e17 s; 1.1e17 is
    # a convenient conservative envelope covering the whole positive family.
    elapsed_bound_s = 1.1e17
    dust_only_elapsed_upper_s = 2/(3*2.1842852410855026e-18*math.sqrt(.9*.315))*((1/3)**1.5-(1/21)**1.5)
    fluence = .01*elapsed_bound_s*rate
    freezeout = {
        "schema": "he32.conditional_charged_nuclear_freezeout.v1",
        "basis": ["derived", "numerically checked"],
        "assumptions": {
            "relative_velocity_distribution": "Maxwellian at gas T",
            "T_max_K": tmax,
            "reduced_mass_min_amu": 2/3,
            "Z1_Z2_min": 1,
            "S_max_keV_barn": 1.e6,
            "S_envelope_status": "explicit adopted condition for all E>0, not a measured universal bound",
            "screening": "bare point Coulomb factor; additional enhancement not included",
            "n_partner_max_cm3": .01,
            "elapsed_time_max_s": elapsed_bound_s,
            "dust_only_elapsed_upper_s": dust_only_elapsed_upper_s,
            "initial_free_neutrons_and_tritium": "zero",
            "nuclear_photodisintegration": "zero for prescribed photon support below 60 eV",
        },
        "rate_bound_formula": "2 sqrt(8/(pi mu)) Smax / sqrt(kB T) exp[-3(EG/(8 kB T))^(1/3)]",
        "Gamow_energy_keV": eg/(1.e3*electron_volt),
        "exponent_at_Tmax": exponent,
        "sigma_v_upper_cm3_s": rate,
        "single_channel_events_per_baryon_upper": fluence,
        "unique_charged_entrance_channels_in_image19": 8,
        "charged_events_upper": 8*fluence,
        "neutron_consumption_events_upper": 8*fluence,
        "tritium_decays_upper": 16*fluence,
        "all_image_nuclear_events_upper": 32*fluence,
        "nuclear_population_baryon_weighted_l1_change_upper": 448*fluence,
        "event_budget_proof": "Each of 8 distinct charged entrance channels has events/baryon <= nmax dt rate. Each produces at most one free neutron; neutron capture or decay consumes it once. Tritium production is bounded by charged events plus neutron captures. Thus total events <=4*8*epsilon. Each event has baryon-weighted stoichiometric l1 <=14.",
        "elapsed_time_proof": "Positive radiation, massive sector, Lambda and shear imply H>=H0 sqrt((1-fm) Omega_m) a^(-3/2); integrate dt=da/(aH) between1/21 and1/3. Withfm=.1 gives1.043600894e17 s <1.1e17 s.",
        "scope": "The 19 displayed channels with inverse radiative captures de-duplicated. Additional Li6 nuclear channels require an explicit finite channel count if a summed error bound is claimed.",
    }
    write("NUCLEAR_FREEZEOUT_BOUND.json", freezeout)

    h0 = 2.1842852410855026e-18
    omega_b = .049309230511847414
    omega_m, omega_r, omega_lambda = .315, 9.2e-5, .684908
    r_d, r_he3, r_li6, r_li7, y_he4 = 2.503248144e-5, 1.049996333e-5, 1.e-14, 5.36802116e-10, .2468382676
    b_other = 1+2*r_d+3*r_he3+6*r_li6+7*r_li7
    r_he4 = y_he4*b_other/(4*(1-y_he4))
    baryons_per_h = b_other+4*r_he4
    nuclei_per_h = 1+r_d+r_he3+r_he4+r_li6+r_li7
    electrons_max_per_h = 1+r_d+2*(r_he3+r_he4)+3*(r_li6+r_li7)
    rho_c = 3*h0*h0/(8*math.pi*G)
    u_uv_max = p.uv_energy_density_J_m3(1.e-12)
    u_b_min = rho_c*omega_b*27*c*c
    u_iso_z2 = rho_c*(omega_m*27+omega_r*81+omega_lambda)*c*c
    ionization_ev_per_b = (13.6*(1+r_d)+(24.59+54.42)*(r_he3+r_he4)+(5.392+75.64+122.5)*(r_li6+r_li7))/baryons_per_h
    energy = {
        "schema": "he32.prescribed_uv_gas_energy_accounting.v1",
        "rho_critical0_kg_m3": rho_c,
        "r_He4_over_H": r_he4,
        "baryon_mass_convention": "n_b m_u; mass number A weighting, not a nuclide mass-defect model",
        "baryons_per_H1": baryons_per_h,
        "n_H1_z0_m3": rho_c*omega_b/(atomic_mass*baryons_per_h),
        "n_baryons_z20_cm3": rho_c*omega_b*21**3/atomic_mass*1.e-6,
        "u_UV_max_J_m3": u_uv_max,
        "u_baryon_rest_z2_J_m3": u_b_min,
        "u_total_isotropic_comparison_z2_J_m3": u_iso_z2,
        "UV_to_baryon_rest_upper_z20_z2": u_uv_max/u_b_min,
        "UV_to_total_isotropic_comparison_z2": u_uv_max/u_iso_z2,
        "thermal_to_baryon_rest_upper": 1.5*(nuclei_per_h+electrons_max_per_h)*k*tmax/(baryons_per_h*atomic_mass*c*c),
        "atomic_ionization_energy_max_eV_per_baryon": ionization_ev_per_b,
        "atomic_ionization_energy_to_baryon_rest_upper": ionization_ev_per_b*electron_volt/(atomic_mass*c*c),
        "interpretation": "Bounds on omitted instantaneous UV/thermal/atomic-binding energy in the prescribed-background closure. They do not bound CI/DR model error or establish a self-consistent source/thermal history.",
    }
    write("UV_GAS_ENERGY_BOUND.json", energy)

    isotopes = [dict(label="n", A=1, Z=0, ratio_to_H=0),
                dict(label="H1", A=1, Z=1, ratio_to_H=1),
                dict(label="D2", A=2, Z=1, ratio_to_H=r_d),
                dict(label="T3", A=3, Z=1, ratio_to_H=0),
                dict(label="He3", A=3, Z=2, ratio_to_H=r_he3),
                dict(label="He4", A=4, Z=2, ratio_to_H=r_he4),
                dict(label="Li6", A=6, Z=3, ratio_to_H=r_li6),
                dict(label="Li7", A=7, Z=3, ratio_to_H=r_li7)]
    states = [dict(label=f"{iso['label']}_q{q}", isotope=iso["label"], A=iso["A"], q=q)
              for iso in isotopes for q in range(iso["Z"]+1)]
    assert len(states) == 21
    contract = {
        "schema": "he32.primordial_atomic_contract.v1",
        "workflow_version": "1.0.0",
        "metric_signature": "(-,+,+,+)",
        "z_interval": [20., 2.],
        "time_variable": "N=ln(a/a_z20); dz/dN=-(1+z); dt/dN=1/H_target",
        "temperature_K": tmax,
        "temperature_policy": "prescribed isothermal external thermal closure",
        "uv": dict(support_eV=[5.392,60.], photon_number_power=2.5,
                   gamma_HI_s_inverse="1e-12/(1+exp((z-6)/0.3))"),
        "atomic_provider": "code/atomic_photo_rr.py:AtomicPhotoRR.rates",
        "atomic_data": "data/ATOMIC_PHOTO_RR.json",
        "isotopes": isotopes,
        "states": states,
        "electron_census": "n_e=sum(q*n_{A,q}); tracked electron is optional redundant output",
        "full_number_density": "n_{A,q}=n_H1_z0*(1+z)^3*ratio_A*f_{Z,q}",
        "isotope_rate_equality": "elemental electronic photo/RR rates, isotope shifts neglected",
        "reduction": "9 independent group slots (H2,He3,Li4) lifted to all21 isotope-charge populations; simplex constraints reduce formal degrees of freedom to6",
        "reduction_validity": "same elemental initial charge fractions, equal electronic coefficients, n=T=0, no nuclear sources; nonzero weak-decay control uses full21 state",
        "initial_charge_fractions_z20": {"H":[.9998,.0002],"He":[1.,0.,0.],"Li":[0.,1.,0.,0.]},
        "lithium_initial_status": "explicit z20 ionized initial scenario motivated by Switzer-Hirata high-z radiation result, not a calculated z20 primordial charge solution",
        "abundance_prior_status": "REI PR151 central mechanical result used as prescribed composition; no covariance or calibrated BBN claim; its Omega_b h^2=0.02205 differs from receiver cosmology",
        "Li6_prior_status": "fixed 1e-14 trace scenario inspired by order1e-14 Cyburt et al 2016 Table II (which gives1.288e-14 at its fiducial cosmology)",
        "Be7_policy": "late-decayed progenitor absorbed into adopted Li7/H input; absent dynamic z20 state",
        "excluded_chemistry": ["electron-impact ionization","dielectronic recombination","charge exchange","negative ions","molecules","excited-level radiative transfer","isotope shifts"],
        "weak_decay": {"neutron_mean_lifetime_s":878.4,"tritium_half_life_s":4500*86400.,
                       "neutron_operator":"n_q0 -> H1_q1 + free_electron",
                       "tritium_operator":"T3_q -> He3_(q+1) + free_electron forq0,1"},
        "nuclear_model": "retained19-channel registry; exact bounded-UV photodisintegration zeros; charged fusion removed under stated S-envelope freezeout approximation",
        "stress_closure": {"baryonic_atomic_gas":"pi_b=0, isotropic collisional closure",
                           "matter":"separate existing collisionless nonbaryonic massive sector, fm=0.1",
                           "radiation":"existing photon+neutrino sectors, photon Thomson term uses live n_e/H_target"},
        "normalizations": {"Sigma":"sqrt(sigma_ab sigma^ab)/H", "Pi_i":"kappa_T sqrt(pi_i_ab pi_i^ab)/H^2", "signed_LRS_component":"D=diag(-1,-1,2); sigma=beta_dot D, pi_i=p_i D; Sigma=sqrt6 abs(beta_dot)/H, Pi_i=sqrt6 abs(kappa_T p_i/H^2)","SI_energy_density_coupling":"kappa_T=8 pi G/c^2, since stresses are J/m^3"},
        "positivity": {"angular_form":"1+A P2(mu)","A_min":-1.,"A_max":2.,"shear_Friedmann_factor":"1-Sigma^2/6 > 0"},
        "wide_parameter_design": {"Sigma0":[0,1e-4,1e-3,.01,.03,.1,.3,.6],"Pi_m_signed0":[-.0006,-.0003,-.0001,0,.0001,.0003,.0012],"Pi_r_signed0":[-.0024,-.001,-.0003,0,.0003,.001,.0048]},
        "physical_scope_label":"primordial H-through-Li positive atomic-ion preliminary pilot, including all21 selected isotope/charge populations",
    }
    write("PHYSICS_CONTRACT.json", contract)
    print(json.dumps({"atomic_oracle":oracle_comparison["result"],"nuclear_single_channel_fluence":fluence,
                      "nuclear_image19_baryon_l1_upper":448*fluence,"uv_fraction_upper":u_uv_max/u_b_min,
                      "species":len(states)}, indent=2))


if __name__ == "__main__":
    main()
