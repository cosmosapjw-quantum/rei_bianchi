#!/usr/bin/env python3
"""Source-owned 1965 He4(gamma,dd) experiment and CEA-1966 elemental D stopping bridge.
No target-epoch photon field, reaction event rate, or plasma heat is inferred.
"""
import csv
import json
import math
import pathlib

M_ALPHA_C2_MEV = 3727.3794118
M_DEUT_C2_MEV = 1875.61294500
Q_MEV = 2*M_DEUT_C2_MEV-M_ALPHA_C2_MEV
ROOT = pathlib.Path(__file__).resolve().parents[1]

def load_sources(root=ROOT):
    x=json.loads((pathlib.Path(root)/"inputs/SOURCE_DATA.json").read_text())
    if x["schema"]!="BASS_HE_ASBURY_CEA_SOURCE_V1":
        raise ValueError("unexpected input schema")
    if len(x["asbury"]["measurements"])!=2 or len(x["cea"]["records"])!=12:
        raise ValueError("wrong number of source records")
    for r in x["cea"]["records"]:
        if r["mass_stopping_MeV_cm2_g"]<=0 or r["range_g_cm2"]<=0:
            raise ValueError("nonpositive stopping input")
    return x

def pair_birth(E_gamma_MeV, theta_cm_deg):
    """Exact gamma+bare-He4 stationary-target -> 2 bare deuterons.
    Energies MeV, theta_cm measured from photon beam, lab=He4 rest.
    """
    E=float(E_gamma_MeV)
    mu=math.cos(math.radians(theta_cm_deg))
    s=M_ALPHA_C2_MEV**2+2*M_ALPHA_C2_MEV*E
    if s < 4*M_DEUT_C2_MEV**2:
        raise ValueError("below dd threshold")
    boost=E/2*math.sqrt(1-4*M_DEUT_C2_MEV**2/s)
    Kp=(E-Q_MEV)/2+boost*mu
    Km=(E-Q_MEV)/2-boost*mu
    return Kp,Km,boost

def interp_source_table(rows, target, energy):
    """Linear interpolation ONLY within selected author-owned neutral-matter table."""
    rr=sorted((r for r in rows if r["target"]==target),key=lambda x:x["E_MeV"])
    energy=float(energy)
    if not (rr[0]["E_MeV"]<=energy<=rr[-1]["E_MeV"]):
        raise ValueError("energy outside chosen verified CEA excerpt 50-150 MeV")
    for r in rr:
        if energy==r["E_MeV"]:
            return r["range_g_cm2"],r["mass_stopping_MeV_cm2_g"],(r["E_MeV"],r["E_MeV"])
    for lo,hi in zip(rr,rr[1:]):
        if lo["E_MeV"]<energy<hi["E_MeV"]:
            t=(energy-lo["E_MeV"])/(hi["E_MeV"]-lo["E_MeV"])
            return tuple(lo[key]+t*(hi[key]-lo[key]) for key in ("range_g_cm2","mass_stopping_MeV_cm2_g"))+( (lo["E_MeV"],hi["E_MeV"]), )
    raise RuntimeError("unreachable table selection")

def asbury_model_total_per_differential(theta_cm_deg):
    """For D_ord = C sin²θ cos²θ and sigma_event = 1/2 ∫D_ord dΩ,
    ratio sigma_event / D_ord(theta) = (4π/15)/(sin²θ cos²θ).
    Published sigma_tot is separately author fitted; check rounding only.
    """
    mu=math.cos(math.radians(theta_cm_deg))
    f=mu**2*(1-mu**2)
    return (4*math.pi/15)/f

def build():
    source=load_sources()
    measured=[]
    daughters=[]
    for i,r in enumerate(source["asbury"]["measurements"],1):
        E=r["Egamma_MeV"]
        Kp,Km,delta=pair_birth(E,r["theta_cm_deg"])
        predicted_model_total=r["DA_nb_sr"]*asbury_model_total_per_differential(r["theta_cm_deg"])
        measured.append({
            **r, "measurement_id":f"ASBURY1965_{i:02d}",
            "model_ratio_sigma_tot_to_DA_sr":asbury_model_total_per_differential(r["theta_cm_deg"]),
            "sigma_event_from_rounded_DA_nb":predicted_model_total,
            "paper_sigma_event_minus_rounded_DA_model_nb":r["sigma_event_model_nb"]-predicted_model_total,
            "Q_MeV":Q_MEV,
            "Ksum_birth_MeV":Kp+Km,
            "Egamma_minus_Q_MeV":E-Q_MEV,
            "source_number_of_experiments":1,
            "nominal_not_event_resolved":True
        })
        for label, K in (("d_plus_nominal",Kp),("d_minus_nominal",Km)):
            interpolated={}
            for target in ("H","He"):
                R,S,between=interp_source_table(source["cea"]["records"],target,K)
                interpolated[f"R_{target}_g_cm2"]=R
                interpolated[f"S_{target}_MeV_cm2_g"]=S
                interpolated[f"CEA_{target}_bracket_MeV"]="%g-%g"%between
            daughters.append({
                "measurement_id":f"ASBURY1965_{i:02d}",
                "Egamma_mean_MeV":E,
                "theta_cm_effective_deg":r["theta_cm_deg"],
                "daughter":label,
                "K_birth_MeV":K,
                "delta_MeV":delta,
                "material_model":"CEA_1966_elemental_tabulated_not_primordial_plasma",
                "kinematics":"exact_if_nominal_mean_E_angle_are_taken_as_point",
                **interpolated
            })
    return source, measured, daughters

def save_csv(name, rows):
    if not rows:
        raise ValueError("empty rows")
    p=ROOT/"results"/name
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def run():
    source, measured, daughters=build()
    save_csv("ASBURY_MEASURED_2.csv",measured)
    save_csv("CEA_ELEMENTAL_D_H_HE_12.csv",source["cea"]["records"])
    save_csv("ASBURY_DFAST_NEUTRAL_BRIDGE_4.csv",daughters)
    payload={
      "schema":"BASS_HE_ASBURY1965_CEA1966_BRIDGE_V1",
      "measured_absolute_differential_cross_sections":2,
      "measured_experiments":1,
      "reported_model_inferred_event_totals":2,
      "author_calculated_CEA_1966_stopping_rows":12,
      "derived_two_deuteron_birth_and_interpolated_neutral_stopping_rows":4,
      "energy_angle_sampling":"source effective mean E and center-of-mass angles; NOT event-level photon energy",
      "metric_signature":"(-,+,+,+)",
      "physical_claims":{"source_hard_data":"established_from_uploaded_originals","daughter_birth":"derived",
         "elemental_interpolated_stopping":"source_conditional","cosmological_ionized_plasma_deposition":"unresolved",
         "he_rest_MeV_photon_history":None,"R_event":None,"heat_rate":None,"kappa":None,
         "L4":False, "production":"HOLD"},
      "dag":{"central":"28/88","HE_physical":"14/18","source_scoped":"2/2","canonical_physical_delta":0},
      "measured":measured,"daughter_bridge":daughters,
      "source_pdf_sha256":source["pdf_sha256"]
    }
    (ROOT/"results/SCIENTIFIC_RESULT.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
    return payload

if __name__ == "__main__":
    p=run()
    print("CREATED",len(p["measured"]),"measured DA and",len(p["daughter_bridge"]),"nominal daughter stopping bridges; HE14/18 CENTRAL28/88 unchanged")
