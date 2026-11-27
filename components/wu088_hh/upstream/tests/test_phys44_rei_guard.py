"""PHYS44 REI consumer: isolate LCS source from spectator scattering and fail closed."""
import json
from pathlib import Path
from decimal import Decimal as D
import pytest

from wu088_hh.phys44_rei_guard import (
    read_rei_guard,ft03_manufactured_response,
    COVERAGE_REL,SOURCE_REL,FT03_REL,LCS_REL
)


def _mock_source(tmp_path):
    rei=tmp_path/"rei"
    wu=tmp_path/"wu"
    for p in (COVERAGE_REL,SOURCE_REL,FT03_REL):
        (rei/p).parent.mkdir(parents=True,exist_ok=True)
    (rei/COVERAGE_REL).write_text(
        '"HH_R10";\nErr(ForwardError::MissingAuthority("NO_EXTERNAL_PHYSICAL_SOURCE_ADMITTED"));\n')
    (rei/SOURCE_REL).write_text('pub const SOURCE_ID: &str = "MD14_Z002_FESC_BB50K_13P6_100_V1";\n')
    (rei/FT03_REL).write_text('pub const FT03_MODEL_ID: &str = "REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1";\n')
    con=wu/LCS_REL
    con.parent.mkdir(parents=True,exist_ok=True)
    con.write_text(json.dumps({"schema":"WU088_HH_PHYS20_CONSUMER_SOURCE_CONTRACT_V1",
                               "consumer_binding":{"status":"unverified"}}))
    return rei,wu


def test_actual_source_family_and_coverage_mock(monkeypatch,tmp_path):
    rei,wu=_mock_source(tmp_path)
    monkeypatch.setattr("wu088_hh.phys44_rei_guard._git_head",lambda p:"test-commit")
    a=read_rei_guard(rei,wu)
    assert a["consumer_actual_existing_HH_R10_excluded"]
    assert a["consumer_actual_require_physical_source_fails_closed"]
    assert "MD14_Z002" in a["consumer_source_identity"]
    assert "FT03" in a["separate_ft03_model_identity"]
    assert a["physical_rate_admission"]=="HOLD"
    assert a["rate_table_status"]=="NOT_AVAILABLE_FROM_BOUND_SOURCES"
    assert a["actual_HH_source_response"]=="NOT_EVALUATED"
    assert a["rei_mutations"]==0


def test_changed_consumer_authority_contract_must_be_reassessed(monkeypatch,tmp_path):
    rei,wu=_mock_source(tmp_path)
    monkeypatch.setattr("wu088_hh.phys44_rei_guard._git_head",lambda p:"fixture")
    (rei/COVERAGE_REL).write_text("no source guard")
    with pytest.raises(ValueError,match="fail-closed"):
        read_rei_guard(rei,wu)
    rei,wu=_mock_source(tmp_path)
    p=wu/LCS_REL
    val=json.loads(p.read_text())
    val["consumer_binding"]["status"]="admitted"
    p.write_text(json.dumps(val))
    with pytest.raises(ValueError,match="changed"):
        read_rei_guard(rei,wu)


def _example(**updates):
    d=dict(nH_cm3="1e-4",xHII=".9",yHeII=".1",yHeIII=".2",
           nHe_over_nH=".0813",w_eV_per_H="1",
           kHHeffective_cm3_s="1e-10",kB_eV_K=".00008617333262",
           chiH_eV="13.598434599702",
           unit_test_only=True)
    d.update(updates)
    return ft03_manufactured_response(**d)


def test_synthetic_exact_dimensional_source_and_thermal_sign():
    r=_example()
    assert r["synthetic"] and r["admitted"] is False
    assert D(r["q_HH_per_H_s"])==D("1e-16")
    assert D(r["dot_e_HH_per_H_s"])==D("1e-16")
    assert D(r["dot_ne_HH_cm3_s"])==D("1e-20")
    assert D(r["dot_w_HH_eV_per_H_s"])==-D("13.598434599702e-16")
    assert D(r["dot_T_HH_K_per_s"])<0
    assert r["thermal_jacobian_decimal_consistency"]


def test_lambda_zero_switch_exactly_all_zero():
    r=_example(lambda_switch="0")
    assert all(D(r[k])==0 for k in (
        "q_HH_per_H_s","dot_e_HH_per_H_s",
        "dot_ne_HH_cm3_s","dot_T_HH_K_per_s","dot_w_HH_eV_per_H_s"))


@pytest.mark.parametrize("inputs",[
    {"xHII":"1.1"},{"yHeII":".7","yHeIII":".7"},
    {"nH_cm3":"-1"},{"kHHeffective_cm3_s":"-1"},
    {"lambda_switch":"1.5"},{"kB_eV_K":"0"},
    {"nH_cm3":"NaN"}])
def test_reject_unphysical_source_factor(inputs):
    with pytest.raises(ValueError):
        _example(**inputs)


def test_actual_physical_source_application_rejected():
    with pytest.raises(PermissionError,match="NO_ADMITTED_RATE_PROVIDER"):
        _example(unit_test_only=False)
