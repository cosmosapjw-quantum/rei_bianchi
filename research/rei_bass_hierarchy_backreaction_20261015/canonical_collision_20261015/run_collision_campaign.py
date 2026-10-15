"""Measured bounded positive collision-event + gas-recoil consistency campaign.

Reads actual PR145 source trajectory at zbar~9.24695 as frozen geometry,
never re-integrates C15, old native H/He or uses a cross section not supplied
by original provider. Nonzero tau are explicitly conditional *control*
values for a source-agnostic collision transaction, not observed gas rates.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
import time
from pathlib import Path

import numpy as np
from canonical_fv import CanonicalMomentumFV
from paired_collision import PositiveCanonicalAngularCollision
from run_hierarchy import source_lock

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"canonical_fv_20261015"
PREVIOUS_SHA="54e29dff5a90c0a785cb6dcfb004403614ca403b"
# Original source FLRW conditional xHII=2e-4, He neutral, REI-matched
# gas specific energy, at zbar20 (PR94) using the REI nH/fHe convention.
ADIABATIC_REI_CONDITIONAL_Z20_THERMAL_J_M3=3.1885009560495904e-19


def backgrounds():
    p=PARENT/"CANONICAL_FV_HISTORY.csv"
    data=list(csv.DictReader(p.open()))
    if len(data)!=968:
        raise ValueError("actual PR145 8x121 saved source not present")
    desired=("massive_plus","signed_shear_plus","signed_shear_minus")
    return [{
        "case":case,
        "actual_saved_PR145_row":60,
        "source_zbar":float(row["zbar"]),
        "eta":float(row["eta"]),
        "b":float(row["b"]),
        "source_Sigma":float(row["Sigma"]),
        "source_gas_is_conditional":
          "REI fixed adiabatic baseline only, not actual C15 photoheated gas",
    } for case in desired
       for row in [next(r for i,r in enumerate(
              x for x in data if x["case"]==case) if i==60)]]


def scalar_source_rhs(pop,w):
    """Independent slow original collision generator, no NumPy row batching."""
    result=np.empty_like(pop)
    for i in range(pop.shape[0]):
        shell=float(np.sum(pop[i,:]))
        for j in range(pop.shape[1]):
            result[i,j]=shell*w[j]-pop[i,j]
    return result


def benchmark(C):
    packets=C.populations()
    expected=scalar_source_rhs(packets,C.wmu)
    obtained=C.source_rhs(packets)
    residual=float(np.max(np.abs(expected-obtained)))
    if residual>3e-16*max(float(np.max(packets)),1e-300):
        raise AssertionError("vectorized Markov generator differs from scalar owner")
    timers={}
    for label,fn,count in [
        ("scalar",lambda:scalar_source_rhs(packets,C.wmu),30),
        ("vector",lambda:C.source_rhs(packets),500)
    ]:
        records=[]
        for _ in range(5):
            start=time.perf_counter_ns()
            for j in range(count):fn()
            records.append((time.perf_counter_ns()-start)/count*1e-9)
        timers[label]=dict(median_s=statistics.median(records),
                           repeat_per_call_s=records)
    return {
        "source_cells":C.source.radial_cells*C.source.angular_cells,
        "quadrature_packets":C.source.packet_count,
        "max_absolute_rhs_difference":residual,
        "one_thread_same_process":True,
        "scalar_source":timers["scalar"],
        "numpy_vector":timers["vector"],
        "relative_speedup":timers["scalar"]["median_s"]/
                            timers["vector"]["median_s"],
        "scope":"Only conditional angular Markov generator, NOT REI chemistry or Einstein total solve",
    }


def run(output:Path):
    lock=source_lock()
    # Exactly the same nonbaryonic parent budget as PR145, no new Omega_m.
    kinetic_ref=lock.rhocrit_j_m3*lock.omega_m*.1/lock.aref**3
    cfg=CanonicalMomentumFV(30.,.5,32,16,gauss_order=3)
    kernel=PositiveCanonicalAngularCollision(cfg,kinetic_ref)
    pop=kernel.populations()
    real_cases=backgrounds()
    taus=(0.,.02,.1,.7,3.,30.)
    rows=[]
    for background in real_cases:
        x=background["eta"];b=background["b"]
        thermal_baseline=ADIABATIC_REI_CONDITIONAL_Z20_THERMAL_J_M3*math.exp(-5*x)
        for tau in taus:
            # Artificial generous partner reserve is used to *measure* the
            # collision impulse, not to claim REI gas can actually pay it.
            after,event=kernel.event(x,b,tau,pop,1e-7)
            real_rejection=False
            try:
                kernel.event(x,b,tau,pop,thermal_baseline)
            except ValueError as e:
                if "insufficient" not in str(e):
                    raise
                real_rejection=True
            required=max(event.massive_delta_energy_J_m3,0.)
            rows.append({
                "source_case":background["case"],
                "zbar":background["source_zbar"],
                "eta":x,"b":b,
                "Sigma_original_PR145":background["source_Sigma"],
                "tau_conditioned":tau,
                "cell_number_before":event.count_before,
                "cell_number_after":event.count_after,
                "radial_shell_max_abs_leak":event.max_radial_shell_count_abs_error,
                "KL_before":event.relative_entropy_before,
                "KL_after":event.relative_entropy_after,
                "Pi_m_before_J_m3":event.Pi_m_before_J_m3,
                "Pi_m_after_J_m3":event.Pi_m_after_J_m3,
                "Q0_massive_impulse_J_m3":event.massive_delta_energy_J_m3,
                "Q0_partner_impulse_J_m3":event.gas_delta_energy_J_m3,
                "Qz_massive_impulse_J_m3_over_c":
                    event.massive_delta_zmomentum_J_m3_over_c,
                "Qz_partner_impulse_J_m3_over_c":
                    event.gas_delta_zmomentum_J_m3_over_c,
                "adiabatic_REI_conditional_u_g_J_m3":thermal_baseline,
                "minimum_gas_reserve_to_pay_event_J_m3":required,
                "required_over_source_adiabatic_gas":
                    required/max(thermal_baseline,1e-300),
                "source_adiabatic_gas_must_REJECT":real_rejection,
                "status":"MATHEMATICAL_CONDITIONAL_COLLISION_NOT_ASTROPHYSICAL_RATE",
            })
    if not len(rows)==18: raise AssertionError("incomplete sampled source events")
    assert max(abs(z["Q0_massive_impulse_J_m3"]+
                   z["Q0_partner_impulse_J_m3"]) for z in rows)==0
    assert max(abs(z["Qz_massive_impulse_J_m3_over_c"]+
                   z["Qz_partner_impulse_J_m3_over_c"]) for z in rows)==0
    if not any(z["source_adiabatic_gas_must_REJECT"] for z in rows):
        raise AssertionError("energy-starved gas source should fail closed")
    if any(z["source_adiabatic_gas_must_REJECT"] for z in rows if z["tau_conditioned"]==0):
        raise AssertionError("collision-free identity should always be allowed")
    output.mkdir(parents=True,exist_ok=True)
    with (output/"COLLISION_EVENTS.csv").open("w") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    result={
      "schema":"rei.canonical_fv.conditional_paired_angular_collision.v1",
      "date":"2026-10-15",
      "source_parent_PR145":"https://github.com/cosmosapjw-quantum/rei_bianchi/pull/145",
      "source_parent_sha":PREVIOUS_SHA,
      "source_original_REI_background":
          "true PR145 Einstein model at snapshot row60, not modified by test collisions",
      "kinetic_fmass_initial":.1,
      "mass_over_Tref":30.,
      "source_massive_reference_energy_J_m3":kinetic_ref,
      "generator":"dN(q,mu)/dtau = W_mu sum_mu N(q,mu) - N(q,mu)",
      "source_tau_status":"CONDITIONED_GIVEN_OPTICAL_DEPTH_NO_MICROPHYSICAL_RATE_OWNER",
      "partner_gas_source":"separate HHe adiabatic conditional reference energy only, NOT gas thermodynamic evolution/actual C15 donor",
      "charge_number_energy_momentum_scope":
        "Massive number and positive cell populations, paired finite-event tetrad Q0 and Qz, isotropic Markov KL dissipation, no chemical reactions.",
      "total_events":len(rows),
      "actual_PR145_background_cases":real_cases,
      "collision_events":rows,
      "benchmark":benchmark(kernel),
      "admitted":"SCOPED_MATHEMATICAL_POSITIVE_PAIR_CONSERVATIVE_EVENT_KERNEL",
      "not_admitted":[
        "physical collision cross section, thermal detailed balance at b≠0 or measured rate",
        "source-compatible real H/He baryonic recoil Euler equation",
        "actual REI full gamma/nu/HHe/stellar feedback time re-integration",
        "polarized Thomson redistribution, recombination photon escape stress or full 4-vector source",
        "gas reserve sufficiency for a realistic source: many controlled events REJECT",
      ],
    }
    (output/"RESULTS.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    _plot(rows,output)
    print(json.dumps({
        "status":result["admitted"],
        "source_cases":len(real_cases),"events":len(rows),
        "max_radial_shell_count_abs_error":
             max(z["radial_shell_max_abs_leak"] for z in rows),
        "source_real_adia_gas_REJECT_count":
             sum(z["source_adiabatic_gas_must_REJECT"] for z in rows),
        "largest_required_gas_reserve_ratio":
             max(z["required_over_source_adiabatic_gas"] for z in rows),
        "vector_speedup":result["benchmark"]["relative_speedup"],
    },indent=2))
    return result


def _plot(rows,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for column, label, name in [
        ("Pi_m_after_J_m3","Massive Pi_s after conditional angular jump [Pa]",
          "PAIRED_COLLISION_PI_RELAXATION.png"),
        ("Q0_massive_impulse_J_m3","Massive collision event Delta energy [J/m^3]",
          "PAIRED_COLLISION_ENERGY_PARTNER.png"),
        ("KL_after","Canonical relative entropy KL after collision",
          "PAIRED_COLLISION_ENTROPY.png"),
    ]:
        fig,ax=plt.subplots(figsize=(7.5,4.4))
        for case in ("massive_plus","signed_shear_plus","signed_shear_minus"):
            sub=[r for r in rows if r["source_case"]==case]
            ax.plot([r["tau_conditioned"] for r in sub],
                    [r[column] for r in sub],marker="o",lw=1,label=case)
        ax.set_xscale("symlog",linthresh=.02)
        ax.set_xlabel("Supplied collision optical depth tau (NOT measured)")
        ax.set_ylabel(label)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out/name,dpi=160)
        plt.close(fig)


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    run(args.output)
