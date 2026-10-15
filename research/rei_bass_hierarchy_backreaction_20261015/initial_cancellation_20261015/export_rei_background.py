"""REI opt-in coupled Einstein background supplier for independent initial Σ and π.

The table does NOT reinterpret original REI AxbiBackground as stress-coupled:
that production provider hardcodes s∝a^-3, invalid for Pi!=0.
This exports full physical proper-time, H, signed shear, b, source Pi_a
and gamma/nu/massive energy/number components, leaving original HHe owner
unchanged. Its source identity MUST differ from the original AX03 clock.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from initial_cancellation import source_identity,SCENARIOS,new_model,actual_electrons

HERE=Path(__file__).resolve().parent
CSV_COLUMNS=[
"scenario_id","study_mode","physics_family","original_q_ref_compatibility",
"Sigma_ref_abs","orientation_ref","kappa_gamma","kappa_nu","A_massive",
"mass_fraction_of_original_omega_m","mass_over_Tref","row",
"x_ln_a_over_aref","a","mean_redshift","proper_elapsed_s","b",
"H_per_s","s_per_s","signed_s_over_H","Sigma_abs","H_perp_per_s",
"H_parallel_per_s","Pi_gamma_Pa","Pi_nu_Pa","Pi_massive_Pa",
"Pi_total_Pa","photon_energy_norm","massless_nu_energy_norm",
"rad_energy_norm","massive_energy_norm","dust_energy_norm",
"omega_lambda","rhocrit0_Jm3","source_n_e_cm3",
"gamma_number_mono","nu_number_mono","massive_J00","massive_J20",
"Hamiltonian_relative_error"
]

def produce(destination:Path,manifest_path:Path):
    if destination.exists() or manifest_path.exists():
        raise FileExistsError("create-only background science table")
    parent=source_identity()
    previous=json.loads((HERE/"evidence/INITIAL_CANCELLATION_NO_THOMSON.json").read_text())
    scattered=json.loads((HERE/"evidence/INITIAL_CANCELLATION_REAL_HHE_THOMSON.json").read_text())
    root0={r["tag"]:r for r in previous["signed_initial_shear_cancellation_roots"]}
    root1={r["tag"]:r for r in scattered["signed_initial_shear_cancellation_roots"]}
    electron,ne_meta=actual_electrons(Path.home()/"Dropbox/bianchi/rei_bianchi")
    assert ne_meta["history_sha256"]=="4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f"
    output=[]
    cases=[]
    for mode in ("stress_only_zero_shear","cancellation_no_thomson","cancellation_real_HHe_Thomson"):
        for tag,kw in SCENARIOS:
            config=dict(kw,nrad=64,nmu=24)
            if mode=="stress_only_zero_shear":
                q=0.
                source_ne=None
            elif mode=="cancellation_no_thomson":
                q=root0[tag]["q_ref_internal"]
                source_ne=None
            else:
                q=root1[tag]["q_ref_internal"]
                source_ne=electron
            model=new_model(q,ne_source=source_ne,**config)
            sol,states,wall=model.integrate(n=161,rtol=4e-11,atol=2e-13)
            qrows=[]
            N=model.imax+1
            for j,x in enumerate(sol.t):
                f=states[j]
                H=f["H"];s=f["s"]
                ap=f["a"]
                energy_norm=(f["dust_energy_norm"]+f["massive_energy_norm"]+
                     f["rad_energy_norm"]+model.source.omega_lambda)
                hc=model.source.h0**2*energy_norm+s*s
                con=abs(H*H-hc)/(H*H)
                row={
                 "scenario_id":tag,"study_mode":mode,
                 "physics_family":"REI_BASS_PR140_Einstein_massive_gamma_nu",
                 "original_q_ref_compatibility":q,
                 "Sigma_ref_abs":model.Sigma_ref,"orientation_ref":model.orientation,
                 "kappa_gamma":kw["kappa_gamma"],
                 "kappa_nu":kw["kappa_nu"],"A_massive":kw["Am"],
                 "mass_fraction_of_original_omega_m":model.fmass,
                 "mass_over_Tref":model.massive.mass,
                 "row":j,"x_ln_a_over_aref":float(x),
                 "a":ap,"mean_redshift":1/ap-1,
                 "proper_elapsed_s":float(sol.y[0,j]/model.source.href),
                 "b":float(sol.y[1,j]),"H_per_s":H,"s_per_s":s,
                 "signed_s_over_H":s/H,"Sigma_abs":f["Sigma"],
                 "H_perp_per_s":H-s,"H_parallel_per_s":H+2*s,
                 "Pi_gamma_Pa":f["Pi_gamma_J_m3"],
                 "Pi_nu_Pa":f["Pi_nu_J_m3"],
                 "Pi_massive_Pa":f["Pi_matter_J_m3"],
                 "Pi_total_Pa":f["Pi_gamma_J_m3"]+f["Pi_nu_J_m3"]+f["Pi_matter_J_m3"],
                 "photon_energy_norm":model.omega_gamma*f["E_gamma"][0]/ap**4,
                 "massless_nu_energy_norm":model.omega_nu*f["E_nu"][0]/ap**4,
                 "rad_energy_norm":f["rad_energy_norm"],
                 "massive_energy_norm":f["massive_energy_norm"],
                 "dust_energy_norm":f["dust_energy_norm"],
                 "omega_lambda":model.source.omega_lambda,
                 "rhocrit0_Jm3":model.source.rhocrit_j_m3,
                 "source_n_e_cm3":f["n_e_cm3"],
                 "gamma_number_mono":f["N_gamma"][0],
                 "nu_number_mono":f["N_nu"][0],
                 "massive_J00":float(sol.y[model.main_size,j]),
                 "massive_J20":float(sol.y[model.main_size+N,j]),
                 "Hamiltonian_relative_error":con
                }
                qrows.append(row)
            if max(r["Hamiltonian_relative_error"] for r in qrows)>4e-14:
                raise RuntimeError("LIVE_EINSTEIN_HAMILTONIAN_INVALID")
            if abs(qrows[0]["proper_elapsed_s"])>0 or abs(qrows[0]["b"])>0:
                raise RuntimeError("WRONG_INITIAL_B_OR_CLOCK")
            if abs(qrows[-1]["signed_s_over_H"])>3e-10 and mode!="stress_only_zero_shear":
                raise RuntimeError("MISSING_SIGNED_SHEAR_CANCELLATION_IN_EXPORT")
            cases.append({"scenario_id":tag,"study_mode":mode,"q_ref_input":q,
              "n":len(qrows),"Sigma_ref":model.Sigma_ref,
              "endpoint_signed_s_over_H":qrows[-1]["signed_s_over_H"],
              "endpoint_b":qrows[-1]["b"],"runtime_source_secs":wall})
            output.extend(qrows)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("w",newline="") as f:
        c=csv.DictWriter(f,fieldnames=CSV_COLUMNS,lineterminator="\n")
        c.writeheader();c.writerows(output)
    src_lock="46f818c2f9de890c72f71fa3cc70366b28c42ca0d65190bd905b6310023e7af0"
    return_data={
      "schema":"rei.BASS_PR140.initial_Sigma_Pi_background_supplier.opt_in_v1",
      "parent_source_modules_SHA256":parent,
      "original_REI_source_background_family_sha256":src_lock,
      "real_HHe_electron_one_way_source":ne_meta,
      "metric_signature":"(-,+,+,+)",
      "Sigma_definition":"sqrt(3)*abs(s)/H; separate sign(s) and input q",
      "physical_pressure_definition":"Pi_s=(p_parallel-p_perp)/3; tensor diag(-Pi_s,-Pi_s,2Pi_s)",
      "Einstein_shear_evolution":"ds/dt+3Hs=(8piG/c^2)*(Pi_gamma+Pi_nu+Pi_massive)",
      "scope":"source-coupled gamma+nu+finite_mass exact high-moment Vlasov and one-way saved HHe Thomson source, not native chemistry/ionizing RT",
      "original_AxbiBackground_replaceable":False,
      "original_production_checkpoint_compatible":False,
      "n_cases":len(cases),"rows_per_case":161,
      "n_rows":len(output),"columns":CSV_COLUMNS,
      "csv_sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
      "cases":cases,
      "units":{
        "proper_elapsed_s":"SI proper seconds since mean z20, not global age",
        "H_per_s,s_per_s,H_perp_per_s,H_parallel_per_s":"SI 1/seconds",
        "Pi_gamma_Pa,Pi_nu_Pa,Pi_massive_Pa,Pi_total_Pa":"SI J/m^3 = Pa (pressure tensor amplitude)",
        "photon_energy_norm,massless_nu_energy_norm,rad_energy_norm,massive_energy_norm,dust_energy_norm":"dimensionless energies / rhoCrit0",
        "source_n_e_cm3":"proper electrons cm^-3; original frozen HHe donor one-way only",
        "Sigma_abs":"nonnegative shear magnitude",
        "signed_s_over_H":"signed axis shear component / H",
        "b":"dimensionless integrated anisotropy; nonzero when final shear cancels"
      },
      "scientific_admission":"OPT_IN_RESEARCH_SUPPLIER_ONLY_NO_NATIVE_CHEMISTRY",
      "next_interface":"source-unique Einstein-Boltzmann native background with interpolation/clock source gate, not old AX03 stressfree s~a^-3 driver"
    }
    manifest_path.write_text(json.dumps(return_data,indent=2)+"\n")
    print("AXBI_INITIAL_PI_SUPPLIER",return_data["n_cases"],return_data["n_rows"],
          return_data["csv_sha256"],flush=True)
    return return_data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--contract",type=Path,required=True)
    args=p.parse_args()
    produce(args.csv,args.contract)
