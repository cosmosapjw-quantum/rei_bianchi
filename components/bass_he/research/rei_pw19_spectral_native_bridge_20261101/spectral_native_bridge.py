#!/usr/bin/env python3
"""PW19 spectral UVB x original REI tick160 frozen H/He matter: source donor only.
No photon current substitution, no cosmological IVP and no canonical admission.
"""
from __future__ import annotations
import hashlib, json, math, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/"research/rei_rux04_p19_native_source_cone_20261101"))
import source_cone_verifier as native_cone
import spectral_physics as spectra

EV_ERG=1.602176634e-12
C_CGS=2.99792458e10
SOURCE_STATE="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
SOURCE_REPORT_SHA="5d8976e0a6ddafda60ab90146e59dfc59f31905edb1da372eb032b9cb8899312"
SCENARIOS=("z5p95_log","z5p95_linear")
SPECIES=("HI","HeI","HeII")

def load_inputs():
    spec_path=HERE/"PW19_VER96_SOURCE_CONDITIONAL_PHYSICS.json"
    if hashlib.sha256(spec_path.read_bytes()).hexdigest()!=SOURCE_REPORT_SHA:
        raise ValueError("Original spectral science result has changed")
    src=spectra.read_source()   # checks Zenodo raw ZIP identity and both 626-point members
    spec=json.loads(spec_path.read_text())
    if spec["original_zip_sha256"]!=spectra.ZIP_SHA or spec["REI_central"]!="28/88_REPORTED":
        raise ValueError("PW19 source lineage invalid")
    for scenario in SCENARIOS:
        _,reproduced=spectra.quadrature(src,scenario,16)
        for s in SPECIES:
            recorded=spec["science"][scenario]["rates_16_substeps"][s]
            for key in ("photo_rate_per_s","excess_heat_eV_per_s"):
                if not math.isclose(reproduced[s][key],recorded[key],rel_tol=4e-14,abs_tol=0):
                    raise ValueError("Spectral numerical readback disagreement")
    sci,_,_=native_cone.load(REPO)
    cone=native_cone.compute(REPO)
    if sci["native_source_state_array_sha256"]!=SOURCE_STATE or sci["physical_nodes"]!=46080:
        raise ValueError("Native REI accepted state mismatch")
    counts=sci["native_global_neutral_counts"]
    if not all(counts[s]>0 for s in SPECIES):
        raise ValueError("Native neutral group counts invalid")
    if abs(cone["r_min_HeI_per_HI"]-.695234932510958)>1e-13:
        raise ValueError("REI photon cone has changed")
    return spec,sci,cone

def compute():
    spec,sci,cone=load_inputs()
    neutral=sci["native_global_neutral_counts"]
    data={"schema":"BASS_HE_PW19_SPECTRAL_ACCEPTED_REI_T160_MATTER_RESPONSE_V1",
          "status":"SPECTRAL_SOURCE_DONOR_FROZEN_MATTER_CONDITIONAL_NOT_REI_SOURCE_ADMITTED",
          "pw19_zenodo":spec["original_zenodo_record"],
          "pw19_original_zip_sha256":spec["original_zip_sha256"],
          "native_source_array_sha256":SOURCE_STATE,
          "native_frozen_z":sci["z"],"native_cells_reused":sci["physical_nodes"],
          "claim":"External isotropic PW19 spectral UVB imposed on original REI tick160 neutral populations; NOT an actual native photon source",
          "native_current_only_cone_min_HeI_over_HI":cone["r_min_HeI_per_HI"],
          "native_HI_min_excess_eV":cone["native_HI_mean_excess_min_eV"],
          "neutral_counts":neutral,
          "source_scenarios":{}, "source_ownership":{"RUX02":"PW19_SPECTRAL_DONOR_FOUND",
          "RUX03":"LOCAL_CAUSAL_PHOTON_OPACITY_OWNER_UNBOUND",
          "RUX04":"NOT_ADMITTED"},
          "central_DAG":"28/88_REPORTED", "working_DAG":"33/88_REPORTED",
          "BASS_HE_physical_DAG":"14/18_REPORTED", "canonical_delta":0,
          "original_tick":"160/131072","production":"HOLD",
          "no_new_ionization_ivp":True,"no_original_source_mutation":True}
    for name in SCENARIOS:
        source=spec["science"][name]
        species={}
        moments={"photoionizations_per_s":0.0,"electron_birth_photoonly_per_s":0.0,
                 "binding_energy_storage_rate_erg_s":0.0,
                 "excess_heat_erg_s":0.0,
                 "absorbed_photon_power_erg_s":0.0}
        for s in SPECIES:
            x=source["rates_16_substeps"][s]
            n=neutral[s]
            count=n*x["photo_rate_per_s"]
            heat=n*x["excess_heat_eV_per_s"]*EV_ERG
            binding=count*spectra.CHI[s]*EV_ERG
            abs_energy=heat+binding
            if min(count,heat,binding,abs_energy)<0:raise ValueError("Negative physical rate")
            species[s]={"neutral_nuclei_count":n, "photoionizations_per_s":count,
                         "photo_excess_heat_erg_s":heat,
                         "ionization_binding_energy_storage_erg_s":binding,
                         "absorbed_photon_power_erg_s":abs_energy,
                         "mean_excess_eV":x["mean_excess_eV"]}
            moments["photoionizations_per_s"]+=count
            moments["electron_birth_photoonly_per_s"]+=count
            moments["excess_heat_erg_s"]+=heat
            moments["binding_energy_storage_rate_erg_s"]+=binding
            moments["absorbed_photon_power_erg_s"]+=abs_energy
        bands=[]
        for row in source["bands_16_substeps"]:
            b={k:row[k] for k in ("band","energy_low_eV","energy_high_eV",
                                 "exposure_photon_cm2_s","exposure_erg_cm2_s")}
            b["isotropic_photon_number_density_cm3"]=row["exposure_photon_cm2_s"]/C_CGS
            b["isotropic_radiation_energy_density_erg_cm3"]=row["exposure_erg_cm2_s"]/C_CGS
            b["source_photoionizations_per_s"]={s:neutral[s]*row[f"gamma_{s}_per_s"] for s in SPECIES}
            b["source_photoheat_erg_s"]={s:neutral[s]*row[f"heat_{s}_erg_per_atom_s"] for s in SPECIES}
            bands.append(b)
        ratio=species["HeI"]["photoionizations_per_s"]/species["HI"]["photoionizations_per_s"]
        r=cone["r_min_HeI_per_HI"]
        if not (0<ratio<r):raise ValueError("Frozen REI current-only cone no longer separated")
        minmax=(r-ratio)/(r+ratio)
        strong_ratio=(r*species["HI"]["photoionizations_per_s"])/species["HeI"]["photoionizations_per_s"]
        native_heat=sci["native_total_photoheat_erg_s"]
        if not math.isclose(moments["excess_heat_erg_s"]+moments["binding_energy_storage_rate_erg_s"],
                            moments["absorbed_photon_power_erg_s"],rel_tol=3e-15):
            raise ValueError("photoheat+binding vs photon absorption inconsistency")
        data["source_scenarios"][name]={"species":species,"bands":bands,
             "global":moments,
             "comparison_native_photoheat_scale_only":moments["excess_heat_erg_s"]/native_heat,
             "fixed_native_current_only_photon_cone":{
                 "spectral_HeI_over_HI_events":ratio,"native_min_HeI_over_HI_events":r,
                 "event_deficit_if_HI_matched_factor":strong_ratio,
                 "rate_pair_minimax_lower_bound":minmax,
                 "spectral_HI_mean_excess_eV":species["HI"]["mean_excess_eV"],
                 "native_HI_min_excess_eV":cone["native_HI_mean_excess_min_eV"],
                 "spectral_HeII_mean_excess_eV":species["HeII"]["mean_excess_eV"],
                 "native_HeII_fixed_excess_eV":cone["native_HeII_excess_eV"],
                 "current_only_adapter_feasible":False,
                 "new_photon_spectrum_or_opacity_owner_required":True}}
    return data

def write_group_donor_csv(data):
    """Source-conditional optically thin, angle-integrated band moments.
    A c*n_gamma*<sigma> local rate requires a separate *proper* n_s and
    local radiation transport; it is not a native REI group-current replacement.
    """
    import csv
    outfile=HERE/"PW19_T160_SPECTRAL_THREE_BAND_SOURCE_DONOR_18ROWS.csv"
    fields=["spectrum","band","energy_low_eV","energy_high_eV","species",
            "photon_exposure_cm2_s","photon_n_cm3","mean_band_E_eV",
            "photo_gamma_per_s","effective_sigma_cm2","photo_excess_eV_per_event",
            "photo_absorbed_eV_per_event","frozen_native_events_per_s",
            "frozen_native_photoheat_erg_s","claim_scope"]
    rows=[]
    for scenario in SCENARIOS:
        for band in data["source_scenarios"][scenario]["bands"]:
            phi=band["exposure_photon_cm2_s"]
            mean_e=band["exposure_erg_cm2_s"]/phi/EV_ERG if phi>0 else None
            for sp in SPECIES:
                n=data["neutral_counts"][sp]
                events=band["source_photoionizations_per_s"][sp]
                photoheat=band["source_photoheat_erg_s"][sp]
                gamma=events/n
                sigma=gamma/phi if phi>0 else 0.0
                excess=photoheat/(events*EV_ERG) if events>0 else None
                if events and not math.isclose(gamma, C_CGS*band["isotropic_photon_number_density_cm3"]*sigma,rel_tol=3e-15):
                    raise ValueError("effective cross section closure failed")
                rows.append(dict(zip(fields,[scenario,band["band"],band["energy_low_eV"],
                    band["energy_high_eV"],sp,phi,
                    band["isotropic_photon_number_density_cm3"],mean_e,
                    gamma,sigma,excess,spectra.CHI[sp]+excess if excess is not None else None,
                    events,photoheat,"EXPLORATORY_NONAUTHORITATIVE_NO_LOCAL_REI_PHOTON_OWNER"])))
    if len(rows)!=18:raise ValueError("expected 2 spectra x 3 bands x 3 species")
    with outfile.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
    return outfile

def main():
    a=compute()
    out=HERE/"NATIVE_T160_PW19_SPECTRAL_DONOR_PHYSICS.json"
    out.write_text(json.dumps(a,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    donor_csv=write_group_donor_csv(a)
    print("DONOR_CSV_SHA256",hashlib.sha256(donor_csv.read_bytes()).hexdigest())
    print("RESULT_SHA256",hashlib.sha256(out.read_bytes()).hexdigest())
    for k in SCENARIOS:
        x=a["source_scenarios"][k]
        print(k,"EVENTS",x["global"]["photoionizations_per_s"],
              "PHOTOHEAT_ERG_S",x["global"]["excess_heat_erg_s"],
              "HeI_to_HI",x["fixed_native_current_only_photon_cone"]["spectral_HeI_over_HI_events"],
              "MINIMAX_LOWER",x["fixed_native_current_only_photon_cone"]["rate_pair_minimax_lower_bound"])
    print("DAG",a["central_DAG"],a["BASS_HE_physical_DAG"],"DELTA",a["canonical_delta"])
if __name__=="__main__":main()
