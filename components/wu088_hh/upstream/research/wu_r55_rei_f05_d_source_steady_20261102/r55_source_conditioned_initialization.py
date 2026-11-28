#!/usr/bin/env python3
"""WU R55: original REI F05 deuterium charge-exchange/instantaneous-kinetic initial states.

Uses ONLY WU R54's byte-locked original 46,080-cell source, 17 original photon
knots, Savin (2002) 47-pair charge-exchange rates, and R54's conservative
four-group photo-chemical solver. These are conditional INITIAL states, not
a reconstructed D history or production tick161.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, io, json, sys
from pathlib import Path
import numpy as np

EXPECTED_R54_CODE_SHA256 = "ded9c2542d05d4734370d10819d544986c89c06ef57064ea7e376f3580770885"
EXPECTED_WU_PARENT_SHA = "5933f3fb4432bee7f2268c62873132a0d741f054"
WU_DAG = "34/49"
REI_DAG = "28/88"
REI_WORKING = "33/88"
FAST_DAG = "4/7"

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def load_r54(root):
    root = Path(root).resolve()
    if digest(root / "r54_group_photon_perturbation.py") != EXPECTED_R54_CODE_SHA256:
        raise RuntimeError("IMMUTABLE_R54_CODE_MISMATCH")
    sys.path.insert(0, str(root))
    import r54_group_photon_perturbation as m
    v = m.load()  # byte-verifies all 12 original upstream source files
    prev = json.loads((root / "results/R54_RESULTS.json").read_text())
    if prev["WU_parent_HEAD"] != "6f2f532b46ea153795d6aebeed7b73765b6482ac":
        raise RuntimeError("R54_SOURCE_PARENT_MISMATCH")
    if prev["original_REI_accepted_tick"] != "160/131072":
        raise RuntimeError("ORIGINAL_REI_TICK_CHANGED")
    if prev["source_SHA256"] != json.loads((root / "SOURCE_CONTRACT.json").read_text())["source_sha256"]:
        raise RuntimeError("R54_SOURCE_CONTRACT_CHANGED")
    return m,v,prev

def initial_conditions(m,v):
    """Source CX equilibrium and full instantaneous steady state, no past-D assumption."""
    x = v["x0"]; nH = v["nH"]; ne = v["ne0"]; T = v["T0"]
    kf,kr = m.rates(T,v)
    photo = float(v["source_gam"](v["t0"]))
    alpha = m.alpha_B(T)
    beta = m.beta_H(T)
    cf = kf*nH*x
    cr = kr*nH*(1.-x)
    cx_eq = cf/(cf+cr)
    # D+ contributes electrons even at the initial state. Thus local
    # instantaneous full chemistry steady state is quadratic, not simply a/(a+b).
    p = cf + photo + beta*ne
    q = (beta+alpha)*m.ETA_D*nH
    b = cf + cr + photo + (beta+alpha)*ne - beta*m.ETA_D*nH
    full_eq = 2.*p/(b+np.sqrt(b*b+4.*q*p))  # stable positive quadratic root
    e_full = ne + m.ETA_D*nH*full_eq
    cx_resid = cf*(1.-cx_eq)-cr*cx_eq
    full_resid = (cf+photo+beta*e_full)*(1.-full_eq)-(cr+alpha*e_full)*full_eq
    scale = np.maximum(p,1.e-300)
    cx_rel = np.max(abs(cx_resid)/(cf+cr))
    full_rel = np.max(abs(full_resid)/scale)
    if not np.all((cx_eq>=0)&(cx_eq<=1)&(full_eq>=0)&(full_eq<=1)):
        raise ArithmeticError("SOURCE_INITIAL_STEADY_FRACTIONS_NONPHYSICAL")
    if cx_rel > 2.e-15 or full_rel > 3.e-14:
        raise ArithmeticError("INITIAL_STATIONARY_RATE_IDENTITY_FAIL")
    return {"CX":cx_eq,"FULL":full_eq,"H_MATCHED":x}, {
        "CX_start_rate_residual_relative":float(cx_rel),
        "full_start_rate_residual_relative":float(full_rel),
        "source_HII":m.qq(x),"initial_CX":m.qq(cx_eq),
        "initial_FULL":m.qq(full_eq),
        "full_local_relaxation_exposure":m.qq((b+2.*q*full_eq)*v["dt"]),
        "CX_local_relaxation_exposure":m.qq((cf+cr)*v["dt"]),
        "initial_CX_nucleus_weighted":float(np.average(cx_eq,weights=v["NH"])),
        "initial_FULL_nucleus_weighted":float(np.average(full_eq,weights=v["NH"])),
        "source_T_K":m.qq(T),"source_nH_cm3":m.qq(nH),
        "original_HI_gamma_s_minus_1":photo,
        "original_first_tick_duration_s":float(v["dt"]),
    }

def scenario(m,v,z):
    photo=z["photo"]
    ptotal=photo.sum(axis=0)
    energy = np.asarray(v["meanE"][:3])@photo
    heat = m.ETA_D*m.EV_ERG*(energy-m.CHI_D_PHYS_EV*ptotal)
    latent = m.ETA_D*m.EV_ERG*m.CHI_D_PHYS_EV*ptotal
    photon_gross = m.ETA_D*m.EV_ERG*energy
    electron_created = m.ETA_D*(ptotal+z["eii"]-z["recomb"])
    return {
        "heat":heat,"latent":latent,"gross":photon_gross,
        "heat_ratio":heat/abs(v["dU"]),"electron_created":electron_created,
        "P_per_D":ptotal,
    }

def run(root,out,step_count=64):
    m,v,prev = load_r54(root)
    initials,init_stats = initial_conditions(m,v)
    # Two new physical realizations: CX-only stationary and full-chemistry
    # instantaneous stationary initial conditions. All-neutral/all-ionized
    # benchmarks already exist in source R54 and are reused, not rerun.
    zfull=m.evolve(v,initials["FULL"].copy(),steps=step_count,feedback=True)
    zcx=m.evolve(v,initials["CX"].copy(),steps=step_count,feedback=True)
    z32=m.evolve(v,initials["FULL"].copy(),steps=32,feedback=True)
    znofb=m.evolve(v,initials["FULL"].copy(),steps=step_count,feedback=False)
    sfull=scenario(m,v,zfull); scx=scenario(m,v,zcx)
    full_charge = m.ETA_D*(zfull["y"]-initials["FULL"]-zfull["cx"])
    if np.max(abs(full_charge-sfull["electron_created"])) > 5.e-17:
        raise ArithmeticError("NONZERO_INITIAL_DI_ELECTRON_BOOKKEEPING_FAIL")
    for z in (zfull,zcx):
        if np.max(abs(z["ledger"])) > 4.e-12 or np.any((z["y"]<0)|(z["y"]>1)):
            raise ArithmeticError("DEUTERIUM_CONSERVATION_OR_CONE_FAIL")
        if np.max(abs(z["photon_residual"][:3])/np.maximum(z["pg"][:3],1.e-300))>1.e-12:
            raise ArithmeticError("NATIVE_PHOTON_GROUP_CONSERVATION_FAIL")
        if np.any(z["pg"]<0) or z["pg"][3]!=0 or z["D"][3]!=0 or z["B"][3]!=0:
            raise ArithmeticError("FOUR_GROUP_PHOTON_CONE_FAIL")
    photon_source = json.loads((Path(root)/"source_inputs/R53_PHOTON_BUDGET.json").read_text())
    emission=float(photon_source["native_source_integrated_counts_per_cMpc3"]["emission_rate_s-1_cMpc-3"])
    r54_neutral=prev["numeric"]["initial_neutral_DI_gross_photo_count_total"]
    r54_ionized=prev["numeric"]["initial_ionized_DI_photo_count_total"]
    if not r54_ionized <= sum(zfull["pg"]) <= r54_neutral:
        raise ArithmeticError("STATIONARY_PHOTON_DEMAND_OUTSIDE_SOURCE_EXTREMES")
    group=[]
    for i,g in enumerate(m.GROUPS):
        group.append({"group":g,"source_initial_N_photons_per_cMpc3":float(v["source_N"](v["t0"])[i]),
          "source_final_N_photons_per_cMpc3":float(v["source_N"](v["t1"])[i]),
          "mean_absorbed_photon_energy_eV":float(v["meanE"][i]),
          "FULL_DI_gross_photoevents_per_cMpc3":float(zfull["pg"][i]),
          "FULL_DI_group_deficit_per_cMpc3":float(zfull["D"][i]),
          "FULL_native_absorption_displaced_per_cMpc3":float(zfull["B"][i]),
          "FULL_group_ledger_residual_per_cMpc3":float(zfull["photon_residual"][i]),
          "CX_DI_gross_photoevents_per_cMpc3":float(zcx["pg"][i]),
          "CX_DI_group_deficit_per_cMpc3":float(zcx["D"][i]),
          "CX_native_absorption_displaced_per_cMpc3":float(zcx["B"][i]),
          "original_ALL_NEUTRAL_DI_gross_photoevents_per_cMpc3":float(prev["numeric"]["group_source_photon_records"][i]["initial_neutral_DI_photo_event_count"])})
    cols={
        "node":np.arange(m.N), "original_H_N":v["NH"],
        "proper_nH_cm3":v["nH"],"original_T160_K":v["T0"],
        "source_original_xHII160":v["x0"],
        "CX_equilibrium_initial_y_DII":initials["CX"],
        "full_instantaneous_stationary_initial_y_DII":initials["FULL"],
        "source_original_HII_matched_initial_y_DII":initials["H_MATCHED"],
        "CX_final_y_DII":zcx["y"],"FULL_final_y_DII":zfull["y"],
        "FULL_photo_G1_per_D":zfull["photo"][0],
        "FULL_photo_G2a_per_D":zfull["photo"][1],
        "FULL_photo_G2b_per_D":zfull["photo"][2],
        "FULL_CX_per_D":zfull["cx"],"FULL_RR_per_D":zfull["recomb"],
        "FULL_EII_per_D":zfull["eii"],
        "FULL_new_electrons_per_H_since_initial":sfull["electron_created"],
        "FULL_Dplus_electrons_per_H_including_initial":m.ETA_D*(zfull["y"]-zfull["cx"]),
        "FULL_initial_Dplus_electrons_per_H":m.ETA_D*initials["FULL"],
        "FULL_photo_excess_heat_gross_erg_per_H":sfull["heat"],
        "FULL_photo_latent_binding_gross_erg_per_H":sfull["latent"],
        "FULL_photo_photon_energy_gross_erg_per_H":sfull["gross"],
        "FULL_gross_photoheat_over_abs_native_F05_deltaU":sfull["heat_ratio"],
        "CX_photo_excess_heat_gross_erg_per_H":scx["heat"],
        "CX_gross_photoheat_over_abs_native_F05_deltaU":scx["heat_ratio"],
        "original_native_F05_deltaU_erg_per_H":v["dU"],
        "FULL_5flux_population_ledger_residual":zfull["ledger"]
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    data=out/"R55_REI_F05_INITIAL_DI_PHYSICS_46080.csv.gz"
    m.write_gz(data,cols)
    group_path=out/"R55_PHOTON_GROUPS_4.csv"
    with group_path.open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(group[0]),lineterminator="\n")
        wr.writeheader(); wr.writerows(group)
    # A 24-node source-native witness, sampled across ranked original H densities.
    order=np.argsort(v["nH"])
    ix=np.unique(order[np.linspace(0,m.N-1,24,dtype=int)])
    witness=out/"R55_SOURCE_WITNESS_24.csv"
    with witness.open("w",newline="") as f:
        w=csv.writer(f,lineterminator="\n")
        chosen=["node","proper_nH_cm3","source_original_xHII160",
                "CX_equilibrium_initial_y_DII","full_instantaneous_stationary_initial_y_DII",
                "FULL_final_y_DII","FULL_photo_excess_heat_gross_erg_per_H"]
        w.writerow(chosen)
        for i in ix:
            w.writerow([int(i) if k=="node" else format(float(cols[k][i]),".17g") for k in chosen])
    stats={
       "schema":"WU_R55_ORIGINAL_REI_F05_SAVIN_CHARGE_EXCHANGE_STEADY_INITIAL_DI_V1",
       "status":"ORIGINAL_46K_SOURCE_CONDITIONAL_EXPLORATORY_NOT_HISTORICAL_D_INITIAL_STATE",
       "WU_immutable_parent_PR":194,"WU_immutable_parent_head":EXPECTED_WU_PARENT_SHA,
       "REI_original_F05_26event_PR":352,"REI_original_accepted_tick":"160/131072",
       "REI_tick161":"PREVIEW_HOLD",
       "R54_source_code_sha256":EXPECTED_R54_CODE_SHA256,
       "R54_source_contract_sha256":digest(Path(root)/"SOURCE_CONTRACT.json"),
       "original_source_sha256":prev["source_SHA256"],
       "Savins_rates_47_pairs_original_source":True,
       "assumption":"SOURCE_CONDITIONAL_STEADY_AT_T160_NOT_COSMOLOGICAL_D_HISTORY",
       "isotope_eta_D_hypothetical":m.ETA_D,
       "source_interpolation":"T_LOG_AND_X_ELECTRON_ENDPOINT_T160_ACCEPTED_T161_PREVIEW",
       "photon_opacity_model":"R54_FROZEN_NATIVE_HHE_OPACITY",
       "D_photo_cross_section":"ORIGINAL_HI_CLONE_APPROX_NOT_AB_INITIO_DI",
       "initial_condition_analysis":init_stats,
       "original_extremes":{"ALL_NEUTRAL_DI_gross_photons":float(r54_neutral),
          "ALL_IONIZED_DI_gross_photons":float(r54_ionized),
          "ALL_NEUTRAL_DI_photons_over_original_source_emission":float(r54_neutral/emission)},
       "numeric":{"physical_real_cells":m.N,"rk4_steps":step_count,
        "ALL_SOURCE_PHOTON_EMISSION_per_cMpc3":emission,
        "FULL_final_DI_ion_fraction":m.qq(zfull["y"]),
        "CX_final_DI_ion_fraction":m.qq(zcx["y"]),
        "FULL_gross_DI_photons_per_cMpc3":float(np.sum(zfull["pg"])),
        "CX_gross_DI_photons_per_cMpc3":float(np.sum(zcx["pg"])),
        "FULL_DI_photons_over_source_emission":float(np.sum(zfull["pg"])/emission),
        "CX_DI_photons_over_source_emission":float(np.sum(zcx["pg"])/emission),
        "FULL_photon_demand_over_R54_ALL_NEUTRAL":float(np.sum(zfull["pg"])/r54_neutral),
        "FULL_group_max_depletion_fraction":float(max(zfull["D"][i]/v["source_N"](v["t1"])[i] for i in range(3))),
        "FULL_HHE_native_absorption_displaced_per_cMpc3":float(np.sum(zfull["B"])),
        "FULL_gross_photoheat_over_abs_native_deltaU":m.qq(sfull["heat_ratio"]),
        "CX_gross_photoheat_over_abs_native_deltaU":m.qq(scx["heat_ratio"]),
        "FULL_photoheat_exceeds_1pct_native_abs_deltaU_cells":int(np.count_nonzero(sfull["heat_ratio"]>0.01)),
        "CX_photoheat_exceeds_1pct_native_abs_deltaU_cells":int(np.count_nonzero(scx["heat_ratio"]>0.01)),
        "FULL_ion_fraction_feedback_minus_frozen_max_abs":float(np.max(abs(zfull["y"]-znofb["y"]))),
        "FULL_ion_fraction_RK32_vs_RK64_max_abs":float(np.max(abs(z32["y"]-zfull["y"]))),
        "FULL_global_group_photon_ledger_max_rel":float(np.max(abs(zfull["photon_residual"][:3])/np.maximum(zfull["pg"][:3],1.e-300))),
        "CX_global_group_photon_ledger_max_rel":float(np.max(abs(zcx["photon_residual"][:3])/np.maximum(zcx["pg"][:3],1.e-300))),
        "FULL_cell_5flux_ledger_max_abs":float(np.max(abs(zfull["ledger"]))),
        "FULL_electron_created_since_initial_ledger_max_abs":float(np.max(abs(full_charge-sfull["electron_created"]))),
        "FULL_cell_photon_energy_split_max_abs_erg_per_H":float(np.max(abs(sfull["gross"]-sfull["latent"]-sfull["heat"])))},
       "four_original_source_groups":group,
       "files":{"physical_full_csv_name":data.name,"physical_full_csv_sha256":digest(data),
         "group_csv_name":group_path.name,"group_csv_sha256":digest(group_path),
         "24_cell_witness_name":witness.name,"24_cell_witness_sha256":digest(witness)},
       "DAG":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88",
         "physical_fast":"4/7","canonical_delta":0},
       "gates":{"full_original_26event_reexecution":"NOT_RUN",
         "historical_D_evolution":"NOT_RUN","native_coupled_HHeDI_photons_OTS_heat":"NOT_RUN",
         "source_CONDITIONED_DI_perturbation":"NUMERICALLY_CHECKED",
         "official_tick161_acceptance":"HOLD","CMB_observables":"NOT_RUN",
         "native_subagent":"NOT_RUN","distinct_author_referee":"NOT_RUN",
         "production":"HOLD","HH_R10":False,"REI_L4":False}}
    (out/"R55_RESULTS.json").write_text(json.dumps(stats,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"gamma":init_stats["original_HI_gamma_s_minus_1"],
      "median_x_HII":init_stats["source_HII"]["median"],
      "median_y0_CX":init_stats["initial_CX"]["median"],
      "median_y0_FULL":init_stats["initial_FULL"]["median"],
      "FULL_photons":stats["numeric"]["FULL_gross_DI_photons_per_cMpc3"],
      "FULL_photon_emission_ratio":stats["numeric"]["FULL_DI_photons_over_source_emission"],
      "FULL_over_ALL_NEUTRAL":stats["numeric"]["FULL_photon_demand_over_R54_ALL_NEUTRAL"],
      "FULL_heat_materiality_median":stats["numeric"]["FULL_gross_photoheat_over_abs_native_deltaU"]["median"],
      "FULL_heat_materiality_cell_gt1pct":stats["numeric"]["FULL_photoheat_exceeds_1pct_native_abs_deltaU_cells"],
      "FULL_RK32_RK64":stats["numeric"]["FULL_ion_fraction_RK32_vs_RK64_max_abs"],
      "MAIN_PHYSICAL_DATA_SHA256":stats["files"]["physical_full_csv_sha256"]},sort_keys=True))
    return stats

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--r54-root",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    run(args.r54_root,args.out)
