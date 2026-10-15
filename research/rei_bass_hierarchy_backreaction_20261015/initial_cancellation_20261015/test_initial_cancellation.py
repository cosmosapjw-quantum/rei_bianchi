"""Adversarial initial shear/pi normalization and physical gravity-owner checks.

Tests include strong assertions on source-locked fresh Einstein solves, not just
replaying a JSON record. No new observational or total EoR admission is claimed.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.constants import G,c

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from initial_cancellation import (
    source_identity,source_lock,public_sigma_from_q,new_model,solve,SCENARIOS,
)

@pytest.fixture(scope="module")
def no():
    return json.loads((HERE/"evidence/INITIAL_CANCELLATION_NO_THOMSON.json").read_text())

@pytest.fixture(scope="module")
def on():
    return json.loads((HERE/"evidence/INITIAL_CANCELLATION_REAL_HHE_THOMSON.json").read_text())

@pytest.fixture(scope="module")
def paired(no,on):
    return ({v["tag"]:v for v in no["signed_initial_shear_cancellation_roots"]},
            {v["tag"]:v for v in on["signed_initial_shear_cancellation_roots"]})

def test_source_head_four_byte_locks(no):
    assert source_identity()==no["source_sha256"]
    assert len(no["source_sha256"])==4
    assert source_lock().omega_m>.049309230511847414

def test_shear_scalar_vs_signed_component_convention():
    for q in [-.01,-.001,0,.001,.01]:
        sig,orientation=public_sigma_from_q(q)
        assert sig==pytest.approx(math.sqrt(3)*abs(q)/math.sqrt(1+q*q),abs=1e-16)
        assert orientation==int(np.sign(q))
        model=new_model(q,nrad=32,nmu=16,kappa_gamma=0,kappa_nu=0,Am=0,fm=0)
        init=model.fields(0,model.initial_state())
        assert init["Sigma"]==pytest.approx(sig,abs=1e-16)
        assert math.copysign(1,init["s"])==math.copysign(1,q) if q else init["s"]==0

def test_initial_p2_quadrupole_and_positive_distributions():
    # Exact half-sphere average of P2^2 = 1/5.
    p2=lambda z:(3*z*z-1)/2
    zz=np.polynomial.legendre.leggauss(64)[0]
    for kappa in [-.2,0,.2]:
        w=1+kappa*p2(zz)
        assert w.min()>0
    for A in [-.5,0,.5]:
        w=1+A*p2(zz)
        assert w.min()>0
    z,w=np.polynomial.legendre.leggauss(64)
    assert abs(np.dot(w/2,p2(z)))<1e-14
    assert abs(np.dot(w/2,p2(z)**2)-.2)<1e-14

def test_zero_initial_shear_and_pi_produces_no_signed_shear(no):
    r=no["control_zero_stress_and_zero_shear"]
    assert r["Sigma_ref_user"]==0.
    assert abs(r["signed_s_over_H_end"])<1e-14
    assert abs(r["b_end"])<1e-14

def test_pi_alone_generates_shear(no):
    for r in no["q_zero_nonzero_initial_pi_runs"]:
        if r["tag"] in ["massive_only_negative"]:
            assert r["signed_s_over_H_end"]<0
        elif r["tag"] not in ["massive_only_negative"]:
            assert r["signed_s_over_H_end"]>0
        assert r["Sigma_ref_user"]==0.
        assert r["Sigma_end"]>1e-6

def test_radiation_gamma_nu_source_omegas(no):
    r=next(z for z in no["q_zero_nonzero_initial_pi_runs"] if z["tag"]=="radiation_only")
    # W=1+κP2, physical Pi_s=epsilon*κ/15, γ and ν independently.
    model=new_model(0.,kappa_gamma=.2,kappa_nu=.2,Am=0,fm=0,nrad=32,nmu=16)
    x=model.fields(0,model.initial_state())
    rho=model.source.rhocrit_j_m3
    gamma=rho*model.omega_gamma/model.source.aref**4*.2/15
    nu=rho*model.omega_nu/model.source.aref**4*.2/15
    assert x["Pi_gamma_J_m3"]==pytest.approx(gamma,rel=8e-15)
    assert x["Pi_nu_J_m3"]==pytest.approx(nu,rel=8e-15)
    assert x["Pi_matter_J_m3"]==0.
    assert model.omega_gamma+model.omega_nu==pytest.approx(model.source.omega_r,rel=3e-16)

def test_massive_tensor_stress_uses_one_third_difference(no):
    r=next(z for z in no["q_zero_nonzero_initial_pi_runs"]
           if z["tag"]=="rad_plus_massive_positive")
    m=new_model(0.,kappa_gamma=.2,kappa_nu=.2,
                Am=.5,fm=.1,mass=30,nrad=64,nmu=24)
    ini=m.fields(0.,m.initial_state())
    pi=ini["Pi_matter_J_m3"]
    press=m.source.rhocrit_j_m3*ini["massive_mean_pressure_norm"]
    assert pi>0 and press>0 and pi<press*2
    J=ini["exact_radial_towers"]
    # Original BASS normalized J2 axial scalar * dust fraction/3.
    norm=m.source.rhocrit_j_m3*m.fmass_norm*J.j2[0]/3
    assert pi==pytest.approx(norm,rel=1e-14)
    assert pi==pytest.approx(r["initial_pi_s_Jm3"]["Pi_matter_J_m3"],rel=1e-14)

def test_mass_fraction_does_not_double_count_omega_m():
    m=new_model(0.,fm=.1,Am=.5,nrad=64,nmu=24)
    ini=m.fields(0,m.initial_state())
    a=m.source.aref
    assert (ini["dust_energy_norm"]+ini["massive_energy_norm"])==pytest.approx(
      m.source.omega_m/a**3,rel=3e-15)
    assert m.dust_omega==pytest.approx(.9*m.source.omega_m,rel=3e-15)

def test_all_continuous_shooting_roots_scoped(paired):
    for set_ in paired:
        assert len(set_)==8
        for tag,item in set_.items():
            assert abs(item["q_ref_internal"])<.003
            assert abs(item["signed_s_over_H_end"])<1e-10
            assert item["Sigma_end"]<2e-10
            assert abs(item["b_end"])>2e-5
            assert item["orientation_ref"]==int(np.sign(item["q_ref_internal"]))
            assert item["root_type"].startswith("signed s/H")

def test_quadrupoles_remain_nonzero_at_zero_instantaneous_shear(paired):
    roots,_=paired
    r=roots["rad_plus_massive_positive"]
    assert abs(r["signed_s_over_H_end"])<2e-11
    assert r["final_pi_s_Jm3"]["Pi_gamma_J_m3"]>1e-13
    assert r["final_pi_s_Jm3"]["Pi_nu_J_m3"]>1e-13
    assert r["final_pi_s_Jm3"]["Pi_matter_J_m3"]>1e-14

def test_shear_green_source_integral(paired):
    for set_ in paired:
        for r in set_.values():
            assert r["Green_function_relative_defect"]<1e-8
            v=r["Green_function_left_endpoint_difference"]
            source=r["Green_function_einstein_source_integral"]
            assert math.copysign(1,v)==math.copysign(1,source)
            assert abs(v-source)<1e-8*max(abs(v),abs(source))

def test_angular_direction_redshift_memory(paired):
    for set_ in paired:
        for r in set_.values():
            assert r["ln_photon_directional_energy_transverse_minus_longitudinal"]==pytest.approx(-3*r["b_end"])
            assert abs(r["ln_photon_directional_energy_transverse_minus_longitudinal"])>5e-5

def test_radiation_photon_plus_nu_nearly_additive_root(paired):
    roots,_=paired
    a=roots["radiation_only"]["q_ref_internal"]
    b=roots["photon_seed_only"]["q_ref_internal"]+roots["neutrino_seed_only"]["q_ref_internal"]
    assert abs(a-b)<2e-7

def test_matter_angular_seed_can_offset_radiation(paired):
    roots,_=paired
    pos=roots["rad_plus_massive_positive"]["q_ref_internal"]
    neg=roots["rad_plus_massive_negative"]["q_ref_internal"]
    rad=roots["radiation_only"]["q_ref_internal"]
    assert pos<rad<neg<0
    assert abs(pos-neg)>2e-4

def test_mass_cold_limit_turns_off_pi(paired):
    roots,_=paired
    assert abs(roots["cold_massive_plus_rad"]["q_ref_internal"]
               -roots["radiation_only"]["q_ref_internal"])<3e-6
    a=roots["rad_plus_massive_positive"]["initial_pi_s_Jm3"]["Pi_matter_J_m3"]
    b=roots["cold_massive_plus_rad"]["initial_pi_s_Jm3"]["Pi_matter_J_m3"]
    assert 0<b<a/50

def test_initial_massive_orientation_mirror_cancel_sign(paired):
    roots,_=paired
    pos=roots["massive_only_positive"]["q_ref_internal"]
    neg=roots["massive_only_negative"]["q_ref_internal"]
    assert pos<0<neg
    assert abs(abs(pos)-abs(neg))<5e-8

def test_source_real_HHe_electron_donor_claims_are_limited(on):
    ref=on["source_rei_model_HHe_electron"]
    assert ref["history_sha256"]=="4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f"
    assert ref["original_rows"]==312238
    assert ref["source_is_test_particle_one_way"] is True
    assert ref["max_relative_electron_density_interpolation_error"]>1e-4
    assert all(r["full_HHe_chemistry_evolving_with_new_metric"]=="NOT_RUN" for r in on["signed_initial_shear_cancellation_roots"])
    assert any("not coupled recomputed HHe" in s for s in on["critical_exclusions"])

def test_actual_Thomson_shifts_initial_compensating_shear(paired):
    without,with_=paired
    for tag in ("radiation_only","rad_plus_massive_positive","rad_plus_massive_negative"):
        d=with_[tag]["q_ref_internal"]-without[tag]["q_ref_internal"]
        assert 2.8e-6<d<3.1e-6
    dm=with_["massive_only_positive"]["q_ref_internal"]-without["massive_only_positive"]["q_ref_internal"]
    assert abs(dm)<2e-8

def test_resolution_and_H_loop_source_chemistry_split(no,on):
    for data in (no,on):
        cmp=data["cancellation_target_convergence"]
        assert abs(cmp["signed_s_over_H_strict_minus_low_grid"])<5e-12
        assert abs(cmp["b_strict_minus_low_grid"])<2e-10
        assert abs(cmp["pi_massive_strict_minus_low_grid"])<2e-20
        assert cmp["strict_128r64a_L12_i4"]["nrad"]==128
        assert cmp["strict_128r64a_L12_i4"]["L"]==12

def test_replay_fresh_physical_root_without_resolver(paired):
    roots,_=paired
    q=roots["rad_plus_massive_positive"]["q_ref_internal"]
    new=solve(q,n=161,rtol=4e-11,atol=2e-13,
              kappa_gamma=.2,kappa_nu=.2,Am=.5,fm=.1,mass=30.,nrad=64,nmu=24)
    assert abs(new["signed_s_over_H_end"])<4e-11
    assert abs(new["b_end"]-roots["rad_plus_massive_positive"]["b_end"])<1e-11

def test_exact_Vlasov_gravity_oracle_at_cancel(paired):
    roots,_=paired
    q=roots["rad_plus_massive_positive"]["q_ref_internal"]
    kwargs=dict(kappa_gamma=.2,kappa_nu=.2,Am=.5,fm=.1,mass=30.,nrad=96,nmu=32)
    a=solve(q,n=161,rtol=4e-11,atol=2e-13,gravity_owner="hierarchy",**kwargs)
    b=solve(q,n=161,rtol=4e-11,atol=2e-13,gravity_owner="exact_vlasov",**kwargs)
    assert abs(a["signed_s_over_H_end"]-b["signed_s_over_H_end"])<3e-11
    assert abs(a["b_end"]-b["b_end"])<3e-11
    assert abs(a["final_pi_s_Jm3"]["Pi_matter_J_m3"]-
               b["final_pi_s_Jm3"]["Pi_matter_J_m3"])<3e-20

def test_gamma_neutrino_number_and_positive_pressure_cone(no):
    for item in no["q_zero_nonzero_initial_pi_runs"]:
        assert item["max_gamma_number_error"]<5e-11
        assert item["max_nu_number_error"]<5e-11
        assert item["initial_matter_pressure_norm"]>=0

def test_einstein_hamiltonian_original_evolved_source():
    q=-.000661
    m=new_model(q,kappa_gamma=.2,kappa_nu=.2,Am=.5,fm=.1,mass=30,nrad=64,nmu=24)
    sol,states,_=m.integrate(n=25,rtol=3e-11,atol=2e-13)
    for s in states:
        x=m.source.h0**2*(s["dust_energy_norm"]+s["massive_energy_norm"]+
                         s["rad_energy_norm"]+m.source.omega_lambda)+s["s"]**2
        assert abs(x/s["H"]**2-1)<2e-14

def test_parallel_actual_timing_is_not_native_solver_claim():
    path=HERE/"evidence/PARALLEL_BENCHMARK.json"
    data=json.loads(path.read_text())
    assert data["workers"]==[1,2,4]
    assert data["two_entire_batches_per_worker"] is True
    assert data["n_cases_per_batch"]==8
    assert data["claim_ceiling"].startswith("only independent")
    assert "whole_REI_solver_speedup" not in data
    root=data["batches"]["1"]
    for k in ("2","4"):
        for a,b in zip(data["batches"][k]["same_source_physics_outputs"],root["same_source_physics_outputs"]):
            assert a["tag"]==b["tag"]
            assert abs(a["root_q"]-b["root_q"])<2e-12

def test_trajectory_memory_csv_provenance():
    data=json.loads((HERE/"evidence/TRAJECTORY_MEMORY.json").read_text())
    assert data["total_history_rows"]==1203
    assert data["n_cases"]==3
    ci=data["summary"][1]
    assert abs(ci["s_over_H_end"])<1e-11
    assert abs(ci["b_end"])>2e-4
    assert ci["cross_direction_energy_ratio_transverse_over_axial"]>1.0005
    assert data["stellar_ionizing_history"]=="NOT_RECOMPUTED"


def test_native_stress_intake_positive_and_negative_checks():
    data=json.loads((HERE/"evidence/RUST_CONSUMER_POS_NEG.json").read_text())
    assert data["native_positive_result"]["rows"]==3864
    assert data["native_positive_result"]["cases"]==24
    assert data["native_positive_result"]["Hamiltonian_and_Pi_source_checks"]=="PASS"
    assert data["positive_exit"]==0
    assert len(data["negative_checks"])==3
    assert all(z["exit"]==3 for z in data["negative_checks"])
    assert {z["expected"] for z in data["negative_checks"]}=={
       "PUBLIC_SCALAR_SIGMA_CONTRACT","EINSTEIN_HAMILTONIAN_CONSTRAINT",
       "PI_TENSOR_AMPLITUDE_CLOSURE"
    }
    assert data["source_frozen_readback"] is True

def test_3864_source_table_sha_and_no_old_stressfree_provider():
    import csv,hashlib
    csvpath=HERE/"evidence/REI_SIGMA_PI_BACKGROUND_3864.csv"
    ctr=json.loads((HERE/"evidence/REI_SIGMA_PI_SUPPLIER_CONTRACT.json").read_text())
    assert hashlib.sha256(csvpath.read_bytes()).hexdigest()==ctr["csv_sha256"]
    assert ctr["n_cases"]==24 and ctr["n_rows"]==3864
    assert ctr["rows_per_case"]==161
    assert ctr["original_AxbiBackground_replaceable"] is False
    assert ctr["original_production_checkpoint_compatible"] is False
    with csvpath.open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==3864
    for key in ("Pi_gamma_Pa","Pi_nu_Pa","Pi_massive_Pa",
                "s_per_s","Sigma_abs","signed_s_over_H"):
        assert key in ctr["columns"]
    groups={}
    for row in rows:
        key=(row["scenario_id"],row["study_mode"])
        groups.setdefault(key,[]).append(row)
    assert len(groups)==24
    for (tag,mode),group in groups.items():
        assert len(group)==161
        assert float(group[0]["b"])==0.0
        assert float(group[0]["proper_elapsed_s"])==0.
        assert all(float(r["H_per_s"])>0 for r in group)
        if mode.startswith("cancellation"):
            assert abs(float(group[-1]["signed_s_over_H"]))<3e-10
            assert abs(float(group[-1]["b"]))>2e-5

def test_oneway_electron_input_physics_not_self_consistent_claim():
    ctr=json.loads((HERE/"evidence/REI_SIGMA_PI_SUPPLIER_CONTRACT.json").read_text())
    r=ctr["real_HHe_electron_one_way_source"]
    assert r["source_is_test_particle_one_way"] is True
    assert r["max_relative_electron_density_interpolation_error"]>1e-4
    assert ctr["scientific_admission"]=="OPT_IN_RESEARCH_SUPPLIER_ONLY_NO_NATIVE_CHEMISTRY"

def test_actual_massive_vector_chunk_memory_tradeoff():
    bench=json.loads((HERE/"evidence/MEMORY_CHUNK_BENCHMARK.json").read_text())
    assert bench["input_samples"]==768
    d={r["chunk"]:r for r in bench["measurements"]}
    assert set(d)=={4,8,16,32,64,128}
    assert all(r["max_tensor_absolute_error_vs_fair_scalar"]<8e-15
               for r in bench["measurements"])
    assert d[16]["speedup_vs_fair_scalar"]>1
    assert d[16]["tracemalloc_peak_bytes"]<d[32]["tracemalloc_peak_bytes"]*.55
    assert bench["whole_EoR_solver_speedup"] is None

def test_wolfram_green_tensor_source_seven_zeros():
    j=json.loads((HERE/"evidence/WOLFRAM_SOURCE_CHECKS.json").read_text())
    assert j["all_zero"]
    assert len(j["source_checks"])==7
    assert all(v=="0" for v in j["source_checks"].values())
