#!/usr/bin/env python3
"""Independent repeated-step frozen oracle using the restored original inputs."""
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path

from independent_birth_study import age_moment_decimal, gl, phi_decimal, rule

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument("--input",type=Path,default=HERE.parent/"recovery/reactive02/REI_BASS_REACTIVE02_LONGSPAN_20261019/evidence/FROZEN_SOURCE_INPUTS.csv")
SSOT=parser.parse_args().input.resolve()
data=list(csv.DictReader(SSOT.open()))
duration=8e12
thresholds=[13.598434599702,24.5873888,54.417765,13.602134599702]
source=math.fsum(float(x["total_birth_com3"]) for x in data)
exact_components=[]
for x in data:
    rates=[float(x[k]) for k in ["k_HI","k_HeI","k_HeII","k_DI"]]
    kappa=math.fsum(rates)
    total=float(x["total_birth_com3"])
    exact_n=total*float(phi_decimal(kappa*duration))
    exact_m1=exact_n*duration*float(age_moment_decimal(kappa*duration,1))
    exact_m2=exact_n*duration**2*float(age_moment_decimal(kappa*duration,2))
    exact_components.append((exact_n,exact_m1,exact_m2))
exact_n=math.fsum(x[0] for x in exact_components)
exact_m1=math.fsum(x[1] for x in exact_components)
exact_m2=math.fsum(x[2] for x in exact_components)
rows=[]
for nsteps in [16,32,64,128]:
    dt=duration/nsteps
    for method,refinements in [("legacy_gl",[2,4]),("positive_symmetric_exp_fit",[1,2,4,8])]:
        for refinement in refinements:
            outputs=[]
            cohort_counts=[]
            for x in data:
                rates=[float(x[k]) for k in ["k_HI","k_HeI","k_HeII","k_DI"]]
                kappa=math.fsum(rates);tau=kappa*dt
                born=float(x["total_birth_com3"])/nsteps
                energy=float(x["energy_ev"])
                pairs=gl(refinement) if method=="legacy_gl" else rule(tau,refinement)
                cohort_counts.append(len(pairs))
                qs=[math.fsum(w*(a**p)*math.exp(-tau*a) for a,w in pairs) for p in range(3)]
                qa=math.fsum(w*(-math.expm1(-tau*a)) for a,w in pairs)
                n=m1=m2=absorbed=0.
                attenuation=math.exp(-tau)
                for _ in range(nsteps):
                    absorbed += n*(-math.expm1(-tau))+born*qa
                    m2=attenuation*(m2+2*dt*m1+dt*dt*n)+born*dt*dt*qs[2]
                    m1=attenuation*(m1+dt*n)+born*dt*qs[1]
                    n=attenuation*n+born*qs[0]
                species=[absorbed*k/kappa for k in rates]
                heat=math.fsum(a*(energy-chi) for a,chi in zip(species,thresholds))
                chemical=math.fsum(a*chi for a,chi in zip(species,thresholds))
                outputs.append((n,m1,m2,absorbed,n*energy,heat,chemical,species))
            n=math.fsum(x[0] for x in outputs)
            m1=math.fsum(x[1] for x in outputs)
            m2=math.fsum(x[2] for x in outputs)
            absorption=math.fsum(x[3] for x in outputs)
            photon_energy=math.fsum(x[4] for x in outputs)
            heat=math.fsum(x[5] for x in outputs)
            chem=math.fsum(x[6] for x in outputs)
            source_energy=math.fsum(float(x["total_birth_com3"])*float(x["energy_ev"]) for x in data)
            output={"nsteps":nsteps,"method":method,"refinement":refinement,"exact_survivor":exact_n,"survivor":n,"survivor_relative_error":(n-exact_n)/exact_n,"survivor_mean_age_relative_error":(m1/n)/(exact_m1/exact_n)-1,"survivor_second_age_moment_relative_error":(m2/n)/(exact_m2/exact_n)-1,"photon_number_ledger_relative":(n+absorption-source)/source,"energy_ledger_relative":(photon_energy+heat+chem-source_energy)/source_energy,"birth_cohorts_per_macrostep":sum(cohort_counts),"species_absorbed":[math.fsum(x[7][sp] for x in outputs) for sp in range(4)]}
            if method=="positive_symmetric_exp_fit":
                assert abs(output["survivor_relative_error"])<2e-14
                assert abs(output["photon_number_ledger_relative"])<5e-15
                assert abs(output["energy_ledger_relative"])<5e-15
                assert all(x>=0 for x in output["species_absorbed"])
            rows.append(output)
result={"status":"PASS_SCOPED","input_sha256":hashlib.sha256(SSOT.read_bytes()).hexdigest(),"input_rows":len(data),"duration_s":duration,"source_com3":source,"exact_survivor":exact_n,"exact_survivor_mean_age_s":exact_m1/exact_n,"exact_survivor_second_age_moment_s2":exact_m2/exact_n,"max_positive_relative_survivor_error":max(abs(x["survivor_relative_error"]) for x in rows if x["method"]=="positive_symmetric_exp_fit"),"scope":"restored original H/He/D opacity rates and source weights, held constant; no re-evaluation of atomic providers and no evolving thermochemistry","cases":rows}
(HERE/"RESTORED_SOURCE_FROZEN_COMPARISON.json").write_text(json.dumps(result,indent=2)+"\n")
fields=["nsteps","method","refinement","survivor","survivor_relative_error","survivor_mean_age_relative_error","survivor_second_age_moment_relative_error","photon_number_ledger_relative","energy_ledger_relative","birth_cohorts_per_macrostep"]
with (HERE/"RESTORED_SOURCE_FROZEN_GRID.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
print(json.dumps({k:result[k] for k in ["status","input_sha256","input_rows","exact_survivor","exact_survivor_mean_age_s","max_positive_relative_survivor_error"]},indent=2))
for x in rows:
    if x["nsteps"]==32:
        print(x["method"],x["refinement"],x["survivor_relative_error"],x["survivor_mean_age_relative_error"],x["survivor_second_age_moment_relative_error"],x["birth_cohorts_per_macrostep"])
