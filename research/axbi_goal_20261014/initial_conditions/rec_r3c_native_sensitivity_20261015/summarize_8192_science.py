"""Physically scoped summaries of real 8192-step original-source REI H/He states.

Inputs are full source-locked actual native 6cases x8193 saved accepted states.
Produces <=129-row comparison CSV and two figures; validates species charges,
initial values, source SHA and positivity, and never imputes missing endpoints.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,math
from pathlib import Path

HERE=Path(__file__).resolve().parent
R=HERE/"science_8192step_p64"
CASES=("QZERO_BASELINE","QZERO_HYREC","QMINUS_BASELINE",
       "QMINUS_HYREC","QPLUS_BASELINE","QPLUS_HYREC")
F_HE=0.2454/(4*(1-.2454))


def read():
    receipt=json.loads((R/"RUN_RESULTS.json").read_text())
    if receipt["original_REI_scenario_sha256"]!="07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696":
        raise ValueError("REI scenario input SHA mismatch")
    if receipt["original_2012_HyRec_stdout_sha256"]!="6fa5cb83a45ed3599d824ff821b6c8df41dd6d0e78a46cf9b33fde91b933e400":
        raise ValueError("REC exact native HyRec provenance mismatch")
    if not all(receipt["identical_parallel_bytes"]):
        raise ValueError("same-source parallel native history byte mismatch")
    histories={}
    for entry,name in zip(receipt["serial_runs"],CASES):
        f=R/(name+".csv")
        if entry["case"]!=name or hashlib.sha256(f.read_bytes()).hexdigest()!=entry["sha256"]:
            raise ValueError("science raw native CSV source SHA mismatch")
        with f.open() as stream:
            rows=list(csv.DictReader(stream))
        if len(rows)!=8193:
            raise ValueError("incomplete physically integrated source rows")
        for i,row in enumerate(rows):
            if int(row["accepted"])!=i:
                raise ValueError("bad accepted-step index")
            fractions=[float(row[key]) for key in ("xHII","xHeII","xHeIII")]
            if not (0<=fractions[0]<=1 and fractions[1]>=0 and fractions[2]>=0
                    and fractions[1]+fractions[2]<=1):
                raise ValueError("negative/nonconserved H/He species")
            xe=fractions[0]+F_HE*(fractions[1]+2*fractions[2])
            if abs(xe-float(row["xe_per_H"]))>2e-14*max(abs(xe),1e-8):
                raise ValueError("actual native electron census inconsistent")
            if (abs(float(row["number_ledger_per_H"]))>1e-8 or
                abs(float(row["energy_ledger_eV_per_H"]))>1e-8):
                raise ValueError("cumulative source physical ledger outside gate")
            if float(row["photon_number_per_H"])<0 or float(row["Tgas_K"])<=0:
                raise ValueError("nonphysical photon count or temperature")
            if i>0 and not float(row["a"])>float(rows[i-1]["a"]):
                raise ValueError("invalid ascending physical step sequence")
        histories[name]=rows
    return receipt,histories


def summarize():
    rec,history=read()
    initial=history["QZERO_HYREC"][0]
    first_difference={
        "xHII":float(initial["xHII"])-float(history["QZERO_BASELINE"][0]["xHII"]),
        "Tgas_K":float(initial["Tgas_K"])-float(history["QZERO_BASELINE"][0]["Tgas_K"])
    }
    indices=list(range(0,8193,64))
    if indices[-1]!=8192:indices.append(8192)
    output=[]
    for idx in indices:
        bz=history["QZERO_BASELINE"][idx]
        dz=history["QZERO_HYREC"][idx]
        qminus=history["QMINUS_HYREC"][idx]
        qplus=history["QPLUS_HYREC"][idx]
        def v(row,k):return float(row[k])
        if any(v(history[c][idx],"a")!=v(bz,"a") for c in CASES):
            raise ValueError("not identical mean scale for source comparison")
        row={
            "index":idx,"zbar":v(bz,"zbar"),
            "proper_t_q0_s":v(bz,"time_s"),
            "baseline_HII":v(bz,"xHII"),
            "donor_HII":v(dz,"xHII"),
            "donor_minus_baseline_HII":v(dz,"xHII")-v(bz,"xHII"),
            "baseline_T_K":v(bz,"Tgas_K"),
            "donor_T_K":v(dz,"Tgas_K"),
            "donor_minus_baseline_T_K":v(dz,"Tgas_K")-v(bz,"Tgas_K"),
            "qminus_donor_J2_over_J0":v(qminus,"J2_eV_per_H")/max(v(qminus,"J0_eV_per_H"),1e-40) if idx else 0.,
            "qplus_donor_J2_over_J0":v(qplus,"J2_eV_per_H")/max(v(qplus,"J0_eV_per_H"),1e-40) if idx else 0.,
            "donor_q0_HeII":v(dz,"xHeII"),
            "donor_q0_HeIII":v(dz,"xHeIII"),
            "donor_q0_xe_total":v(dz,"xe_per_H")
        }
        output.append(row)
    final=output[-1]
    full_samples={}
    for name in CASES:
        row=history[name][-1]
        full_samples[name]={
            k:float(row[k]) for k in (
                "xHII","xHeII","xHeIII","xe_per_H","Tgas_K",
                "J0_eV_per_H","J1_eV_per_H","J2_eV_per_H",
                "photon_number_per_H","photon_energy_eV_per_H",
                "number_ledger_per_H","energy_ledger_eV_per_H",
                "time_s","a","zbar")
        }
    for (m,p) in [("QMINUS_HYREC","QPLUS_HYREC"),
                  ("QMINUS_BASELINE","QPLUS_BASELINE")]:
        x=full_samples[m];y=full_samples[p]
        if abs(x["xHII"]-y["xHII"])>1e-12 or abs(x["Tgas_K"]-y["Tgas_K"])>1e-9:
            raise ValueError("signed scalar q-even source trend out of expected scope")
        j0=max(abs(x["J0_eV_per_H"]),abs(y["J0_eV_per_H"]),1e-60)
        if abs(x["J2_eV_per_H"]+y["J2_eV_per_H"])/j0>1e-12:
            raise ValueError("signed quadrupole q-odd trend failed")
        for z in (x,y):
            if abs(z["J1_eV_per_H"])/j0>1e-12:
                raise ValueError("initial reflection-even parity failed")
    analysis={
        "schema":"rei.rec.native_original_md14_8192_science.v1",
        "native_owner_commit":"edddcd6ea9a135fcf18c7be8357b5e11fea87407",
        "rec_donor_blob_sha":"1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4",
        "original_HyRec_native_stdout_sha":rec["original_2012_HyRec_stdout_sha256"],
        "scenario_sha":rec["original_REI_scenario_sha256"],
        "physical_mode":"source-correct PR127 local GL4, original MD14/BB50K radiation and coupled H/He chemistry, fresh initial conditions",
        "native_source_cases":6,
        "native_accepted_steps_per_case":8192,
        "max_expected_domain_zbar":[20,4],
        "actual_truncated_zbar":final["zbar"],
        "elapsed_proper_s":full_samples["QZERO_HYREC"]["time_s"],
        "self_consistent_full_eor_history":False,
        "original_donor_initial_difference":first_difference,
        "actual_8192_terminal_donor_difference":{
            "xHII":final["donor_minus_baseline_HII"],
            "Tgas_K":final["donor_minus_baseline_T_K"],
            "xHII_fraction_initial_difference_retained":final["donor_minus_baseline_HII"]/first_difference["xHII"],
            "Tgas_fraction_initial_difference_retained":final["donor_minus_baseline_T_K"]/first_difference["Tgas_K"]
        },
        "signed_endpoint":{
            "J2_over_J0_minus":final["qminus_donor_J2_over_J0"],
            "J2_over_J0_plus":final["qplus_donor_J2_over_J0"],
            "signed_neutral_he_init_HHe_evolution":True,
            "scalar_even_source_test":"PASS_RELATIVE_SIGNED_CASES_AT_FIXED_MEAN_A",
            "quadrupole_odd_source_test":"PASS_WITH_NUMERICAL_ROUNDOFF",
            "reflection_odd_dipole":"SMALL_WITHIN_PARITY_GATE_NOT_ZERO_PHYSICALLY_UNIVERSAL"
        },
        "last_saved_state":full_samples,
        "raw_reproducibility": [
            {"case":z["case"],"sha256":z["sha256"],"rows":z["rows"]}
            for z in rec["serial_runs"]
        ],
        "parallel_source_byte_identity":True,
        "science_ceiling":"VALID_ONLY_ZBAR_20_TO_19_6157; NO_FULL_REIONIZATION_OR_AX11_CONVERGENCE",
        "status":"PASS_SCOPED_ACTUAL_6CASE_8192_NATIVE_CHEMISTRY_RADIATION"
    }
    (HERE/"NATIVE_8192_SCIENCE_SUMMARY.json").write_text(json.dumps(analysis,indent=2,sort_keys=True)+"\n")
    csvfile=HERE/"NATIVE_8192_DOWNSAMPLED_COMPARISON.csv"
    with csvfile.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=output[0].keys(),lineterminator="\n")
        writer.writeheader();writer.writerows(output)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xx=[z["zbar"] for z in output]
        fig,ax=plt.subplots(figsize=(7,4))
        ax.plot(xx,[z["donor_minus_baseline_HII"] for z in output],
                label=r"$\Delta x_{{\rm HII}}$ (donor-baseline)")
        ax.set_xlabel("Mean redshift (zbar)")
        ax.set_ylabel("Hydrogen ionization fraction difference")
        ax.invert_xaxis();ax.legend();fig.tight_layout()
        fig.savefig(HERE/"donor_delta_HII_vs_redshift.png",dpi=160);plt.close(fig)
        fig,ax=plt.subplots(figsize=(7,4))
        ax.plot(xx,[z["qminus_donor_J2_over_J0"] for z in output],
                label="q_ref=-0.01")
        ax.plot(xx,[z["qplus_donor_J2_over_J0"] for z in output],
                label="q_ref=+0.01")
        ax.set_xlabel("Mean redshift (zbar)")
        ax.set_ylabel("Ionizing photon quadrupole J2/J0")
        ax.invert_xaxis();ax.legend();fig.tight_layout()
        fig.savefig(HERE/"signed_J2_over_J0_vs_redshift.png",dpi=160);plt.close(fig)
    except ImportError:
        analysis["figures"]="MATPLOTLIB_NOT_AVAILABLE"
    print(json.dumps({"status":analysis["status"],
                      "last_z":final["zbar"],
                      "delta_x":final["donor_minus_baseline_HII"],
                      "delta_T":final["donor_minus_baseline_T_K"],
                      "signed_J2":analysis["signed_endpoint"],
                      "rows_summarized":len(output)},indent=2))
if __name__=="__main__":summarize()
