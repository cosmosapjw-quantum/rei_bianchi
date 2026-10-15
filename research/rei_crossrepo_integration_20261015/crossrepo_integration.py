#!/usr/bin/env python3
"""Real five-supplier consumers for an isolated REI C11 scientific integration.

Consumes immutable files byte-identical to specified Git blob refs. Positive
C10 packet -> original bass_cr shape-free envelope; original BASS AX03 clock
-> verified REI kinematics; REC original HyRec donor -> opt-in-only z20
sensitivity; WU source guard -> HH unavailable; HE warm P01 -> source-specific
tau reproducibility, NO reassignment to C10.
"""
from __future__ import annotations

from decimal import Decimal,localcontext
from fractions import Fraction
import csv,hashlib,json,math,os,sys,time
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SUP=HERE/"suppliers"
sys.path.insert(0,str(ROOT/"research/source07_c9_heii_vector_20261015"))
sys.path.insert(0,str(ROOT/"research/source07_c10_dynamic_20261015"))
import experiment as c9
import dynamic as c10


def validate_mirror():
    manifest=json.loads((HERE/"SUPPLIER_SOURCE_MANIFEST.json").read_text())
    seen=set()
    for rec in manifest["sources"]:
        p=HERE/rec["local_path"]
        raw=p.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        assert sha==rec["sha256"] and blob==rec["git_blob_sha1"]
        seen.add(rec["provider"])
    assert seen=={"bass","bass_cr","rec_bianchi","WU088_HH","BASS_HE"}
    return {"suppliers":sorted(seen),"file_count":len(manifest["sources"]),
            "all_downloaded_git_blobs_match":True}


def background_photon_source():
    """Directly execute original BASS source models and 4th order shortstep."""
    base=SUP/"bass"/"rei_axbi_shortstep_20261015"
    sys.path.insert(0,str(base))
    from shortstep import (Family,Background,gauss_increment,
                           photon_short_logmap,stable_dx)
    model=c9.Scenario(ROOT)
    sampled=[]
    for q in (-.01,-.005,0.,.005,.01):
        bg=Background(Family(q))
        for a0,a1 in ((.1,math.nextafter(.1,math.inf)),(.1,.100000001),(.1,.1001)):
            dt,db=gauss_increment(bg,a0,a1,order=4)
            dx=stable_dx(a0,a1)
            localH=float(bg.mean_hubble(a0))
            locals=float(bg.shear(a0))
            # Limit check only for small increments. It is NOT a full
            # mathematical quadrature error bound.
            dt_linear=dx/localH
            db_linear=locals*dt_linear
            sameH=abs(model.hubble(a0,q)-localH)/localH
            assert sameH<2e-12
            assert dt>0 and abs(dt-dt_linear)/dt < .002
            if q==0:
                assert db==0.
            else:
                assert math.copysign(1,db)==math.copysign(1,q)
            char=photon_short_logmap(bg,a0,a1,np.array([-.8,0.,.8]))
            assert abs(float(char["number_phase_volume_log_residual"][1]))<2e-14
            assert np.isfinite(char["log_energy_early_over_late"]).all()
            sampled.append({"q":q,"a0":a0,"a1":a1,"proper_dt_s":dt,
                            "delta_b":db,"dt_local_linear_s":dt_linear,
                            "db_local_linear":db_linear,"H_relative_vs_C9":sameH,
                            "energy_log_directional":char["log_energy_early_over_late"].tolist(),
                            "phase_volume_residual_max":float(np.max(abs(
                                char["number_phase_volume_log_residual"])))})
    return {"status":"SOURCE_MATCHED_KERNEL_CONSUMED","count":len(sampled),
            "max_rel_source_H":max(x["H_relative_vs_C9"] for x in sampled),
            "sample":sampled[:5],"max_phase_volume_residual":max(x["phase_volume_residual_max"] for x in sampled)}


def source_packet_envelopes():
    """Original bass_cr adaptive_q.py on genuine C10 source-resolved packets."""
    sys.path.insert(0,str(SUP/"cr"))
    from adaptive_q import PositivePacketOracle,AdaptiveQGrid
    model=c9.Scenario(ROOT)
    gas=c10.Gas.initial(model)
    # ONE emission epoch at receiver a=.2, ONE reference ray mu=0:
    # source owns complete E and positive weights. No angle/age mixing here.
    packet=c9.build_packets(model,c9.Spectrum(),np.array([.2]),q=0.,
                            n_mu=1,n_energy=8)[0]
    energies,weights,sigma,heat_sigma=packet
    truth=c10.reactions_vector(weights,energies,sigma,heat_sigma,gas.neutral,1e10)
    A=truth[0]
    tau=c9.C_CGS*1e10*(sigma@gas.neutral)
    absfrac=-np.expm1(-tau)
    rates=sigma*gas.neutral[None,:]
    frac=np.zeros_like(rates)
    np.divide(rates,tau[:,None]/(c9.C_CGS*1e10),
              where=tau[:,None]>0,out=frac)
    species_heat=np.sum(weights[:,None]*absfrac[:,None]*frac*
                        np.maximum(energies[:,None]-c9.BIND[None,:],0.),axis=0)
    observed=np.concatenate([A,species_heat])
    assert abs(species_heat.sum()-truth[1])<1e-11
    oracle=PositivePacketOracle(energies,weights,
        source_id="MD14_Z002_FESC_BB50K_13P6_100_V1",
        ray_id="C10_Q0_MU0_A0P2_SOURCE_SINGLE_AGE",
        proper_epoch_s=0.)
    t0=time.perf_counter()
    grid=AdaptiveQGrid(oracle,[13.6,100.],1.,gas.neutral,1e10,
                       [1e-7]*3+[1e-5]*3,nodes_per_branch=2)
    initial=grid.summary()
    final=grid.run(8)
    wall=time.perf_counter()-t0
    for j,(lo,hi) in enumerate(final["event"]+final["heat"]):
        if not (lo-1e-12<=observed[j]<=hi+1e-12):
            raise AssertionError(f"true packet event escaped outer envelope: j={j} {observed[j]} ∉ [{lo},{hi}]")
    assert all(new<=old+1e-12 for new,old in zip(final["widths"],initial["widths"]))
    assert final["mass"]==initial["mass"]
    assert final["reference_energy_eV"]==initial["reference_energy_eV"]
    return {"status":"ACTUAL_SOURCE_PACKETS_WITH_POSITIVE_DYADIC_ADAPTIVE_BOUNDS",
            "original_gas_cm3":gas.neutral.tolist(),"t_s":1e10,
            "single_ray_mu":0.,"one_source_a":.2,
            "n_packets":len(energies),"oracle_events_and_heat":observed.tolist(),
            "initial":initial,"final":final,"wall_s":wall,
            "precision_admission":final["precision_gate"],
            "mass_energy_conserved_exact_dyadics":final["exact_dyadic_partition"]}


def recombination_initial_counterfactual():
    """Actual HyRec donor artifact and source REI boundary. No scenario replacement."""
    sys.path.insert(0,str(SUP/"rec"))
    from rei_initial_boundary import REIConditionalIC,_state_metrics
    src=ROOT/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json"
    ic=REIConditionalIC.from_scenario(src)
    donor=json.loads((SUP/"rec/REI_DONOR_CANDIDATE_OPTIN_ONLY.json").read_text())
    assert donor["source_rei_scenario_sha256"]==ic.scenario_sha256
    assert donor["activation"]=="DISABLED_REQUIRES_SEPARATE_REI_SENSITIVITY_CAMPAIGN"
    start=_state_metrics(ic,x_e=ic.actual_electron_fraction,Tgas_K=ic.Tgas_K)
    dr=donor["candidate_initial_gas"]
    other=_state_metrics(ic,x_e=dr["electron_fraction_xe_per_H"],
                         Tgas_K=dr["Tgas_K"])
    delta={key:other[key]-start[key] for key in (
         "electron_density_m3","electron_density_cm3",
         "thomson_optical_depth_rate_per_ln_a","thermal_energy_J_m3")}
    tau_ratio=other["thomson_optical_depth_rate_per_ln_a"] / start["thomson_optical_depth_rate_per_ln_a"]-1
    assert abs(tau_ratio-0.0517459)<2e-6
    assert all(math.isfinite(v) for v in delta.values())
    return {"status":"DISABLED_SOURCE_MATCHED_INITIAL_SENSITIVITY",
            "donor_source_method":donor["model"],
            "donor_REI_zbar":ic.z_ref,
            "source_scenario_sha256":ic.scenario_sha256,
            "baseline":start,"donor_conditional":other,"delta":delta,
            "relative_thomson_rate_delta":tau_ratio,
            "ionizing_stock_changed":False,"production_IC_changed":False}


def wu_coulomb_source_guard():
    """Invoke original WU088 consumer gate using original local WU HH provider."""
    sys.path.insert(0,str(SUP/"wu"))
    from phys44_rei_guard import read_rei_guard,ft03_manufactured_response
    default_wu=Path.home()/"chat_research"/"WU088_HH"
    provider=Path(os.environ.get("WU088_HH_LOCAL_REPO",str(default_wu)))
    if not provider.is_dir():
        raise FileNotFoundError("WU088_HH_LOCAL_REPO_REQUIRED_FOR_NATIVE_GUARD")
    # A relocated source archive has no .git metadata. In that case an
    # independently checked original native REI checkout supplies the real
    # repository identity; verify all source surfaces byte for byte first.
    consumer=Path(os.environ.get("REI_NATIVE_CONSUMER_ROOT",str(ROOT)))
    if consumer.resolve()!=ROOT.resolve():
        for rel in ("rust/rei_microphysics/src/coverage.rs",
                    "rust/rei_microphysics/src/axbi_sources.rs",
                    "rust/rei_microphysics/src/ft03_controlled.rs",
                    "research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json"):
            left=(ROOT/rel).read_bytes()
            right=(consumer/rel).read_bytes()
            if hashlib.sha256(left).digest()!=hashlib.sha256(right).digest():
                raise ValueError("REI_NATIVE_CONSUMER_SOURCE_IDENTITY_MISMATCH: "+rel)
    result=read_rei_guard(consumer,provider)
    assert result["consumer_actual_existing_HH_R10_excluded"]
    assert result["physical_rate_admission"]=="HOLD"
    assert result["rate_table_status"]=="NOT_AVAILABLE_FROM_BOUND_SOURCES"
    try:
        ft03_manufactured_response(nH_cm3=".001",xHII=".2",yHeII=".1",
            yHeIII=".1",nHe_over_nH=".08",w_eV_per_H="3",
            kHHeffective_cm3_s="1e-15",kB_eV_K="8.617333262145e-5",
            chiH_eV="13.6")
    except PermissionError:
        refused=True
    else:refused=False
    assert refused
    return {"status":"ACTUAL_WU_GUARD_EXECUTED_HH_PHYSICAL_RATE_HOLD",
            "consumer_source_identity":result["consumer_source_identity"],
            "consumer_actual_source_declines_HH":True,
            "unit_test_without_approval_refused":refused,
            "wu_source_ledger":result["provider_PHYS19_contract_sha256"]}


def he_tau_source_bound():
    """Check the 16 actual HE warm-source cumulative bounds without conflation."""
    status=json.loads((SUP/"he/RESULT_STATUS.json").read_text())
    with (SUP/"he/warm_P01_cumulative_tau.csv").open(newline="") as fp:
        rows=list(csv.DictReader(fp))
    assert len(rows)==status["completed_saved_cells"]==16
    bounds=[(Decimal(x["cumulative_tau_lower"]),
             Decimal(x["cumulative_tau_upper"])) for x in rows]
    assert all(0<a<=b for a,b in bounds)
    assert all(bounds[i][0]>=bounds[i-1][0] and bounds[i][1]>=bounds[i-1][1]
               for i in range(1,len(bounds)))
    assert str(bounds[-1][0])==str(Decimal(status["final_tau_outward"][0]))
    assert str(bounds[-1][1])==str(Decimal(status["final_tau_outward"][1]))
    with localcontext() as ctx:
        ctx.prec=60
        one=Decimal(1)
        mid=(bounds[-1][0]+bounds[-1][1])/2
        # Stable Decimal formulation via full exponential, at 1e-7 precision.
        prob=one-(-mid).exp()
    declared=Decimal(status["first_collision_mid_display"])
    assert abs(prob-declared)<Decimal("2e-23")
    assert status["original_source_commit"]!="26177f10d2c3264189980af2de26b3f63a9227fc"
    return {"status":"SOURCE_SCOPED_WARM_P01_INTERVAL_REUSED_AS_INDEPENDENT_REFERENCE",
            "source_commit":status["original_source_commit"],
            "cells":len(rows),"tau_interval":[str(x) for x in bounds[-1]],
            "single_collision_probability":str(prob),
            "no_cold_C10_observable_transfer":True}


def run():
    t=time.perf_counter()
    out={"schema":"rei.c11.crossrepo.integration.v1",
         "source_integrity":validate_mirror(),
         "bass_background_photons":background_photon_source(),
         "rec_conditional_IC":recombination_initial_counterfactual(),
         "wu_admission_gate":wu_coulomb_source_guard(),
         "BASS_HE_warm_tau":he_tau_source_bound(),
         "bass_cr_actual_source_packets":source_packet_envelopes()}
    out["wall_s"]=time.perf_counter()-t
    (HERE/"CROSSREPO_CONSUMER_RESULTS.json").write_text(json.dumps(out,indent=2)+"\n")
    for key in out:
        print(key,json.dumps(out[key])[:950],flush=True)
    return out

if __name__=="__main__":run()
