"""Driver and result-contract tests; the Rust scientific runs are not repeated."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1]/"scripts/phys68_rust_reference.py"
spec = importlib.util.spec_from_file_location("phys68_rust_reference_driver",SCRIPT)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def reference(steps=100):
    return {"steps":steps,"L":28,"m":0,"target":[21,20],"B":27,"T":65,
            "d2":{"real":7e-48,"imag":3e-48}}


def test_source_mismatch_fails_before_creating_output_or_launching_runtime(tmp_path):
    source=tmp_path/"source.npz"
    source.write_bytes(b"not the protected frozen source")
    out=tmp_path/"out"
    with pytest.raises(ValueError,match="SHA256"):
        driver.run_reference(source,out,"nonexistent-rustc")
    assert not out.exists()


def test_seed_validation_binds_consecutive_channels_and_exact_binary64(tmp_path):
    path=tmp_path/"seed.txt"
    path.write_text("# test fixture, no scientific run\n"+
                    "\n".join(f"{j} 1.00000000000000000e+00 0.0 0.0 7.00000000000000000e-01"
                              for j in range(29))+"\n")
    record=driver.validate_seed_text(path)
    assert record["L"]==28 and len(record["rows"])==29
    assert record["rows"][28]["binary64_hex"]==[float(1).hex(),float(0).hex(),float(0).hex(),float(0.7).hex()]
    assert record["sha256"]==driver.digest(path)


@pytest.mark.parametrize("text", ["0 1 0 0\n","1 1 0 0 0\n", "0 nan 0 0 0\n",
                                  "0 0 0 0 0\n", "0 1 0 0 0\n"])
def test_invalid_seed_cannot_enter_rust_contract(tmp_path,text):
    path=tmp_path/"seed.txt";path.write_text(text)
    with pytest.raises(ValueError):
        driver.validate_seed_text(path)


def test_refinement_goal_is_a_diagnostic_and_not_a_certificate():
    coarse,fine=reference(100),reference(200)
    fine["d2"]["real"]+=1e-56
    result=driver.compare_refinement(coarse,fine)
    assert result["goal_met"] and result["status"]=="NUMERICALLY_CHECKED"
    assert result["certified_error_bound"] is False
    assert result["external_validated_ball_comparison"]=="PENDING_PARENT_CERTIFICATE"
    fine["d2"]["real"]+=1e-49
    failed=driver.compare_refinement(coarse,fine)
    assert not failed["goal_met"] and failed["status"]=="REFINEMENT_GOAL_NOT_MET"


def test_refinement_rejects_changed_inputs_wrong_resolution_and_zero_scale():
    coarse=reference(100)
    fine=reference(201)
    with pytest.raises(ValueError,match="doubled"):
        driver.compare_refinement(coarse,fine)
    fine=reference(200);fine["L"]=64
    with pytest.raises(ValueError,match="inputs differ"):
        driver.compare_refinement(coarse,fine)
    fine=reference(200);fine["d2"]={"real":0,"imag":0}
    with pytest.raises(ValueError,match="absolute-error"):
        driver.compare_refinement(coarse,fine)


@pytest.mark.parametrize("value", [float("nan"),float("inf"),"1",True])
def test_nonfinite_or_non_numeric_results_are_rejected(value):
    result=reference();result["d2"]["real"]=value
    with pytest.raises(ValueError):
        driver.complex_field(result,"d2")


def test_execution_records_match_the_current_sources_and_actual_seed_bytes():
    # Read existing completed outputs only; no compile/solver rerun.
    root=SCRIPT.parents[1]
    out=root/"research/hh_phys68_20261019/rust_reference/run_20261019"
    record=json.loads((out/"EXECUTION_RECORD.json").read_text())
    assert record["rust_source_sha256"]==driver.digest(SCRIPT.with_suffix(".rs"))
    assert record["driver_sha256"]==driver.digest(SCRIPT)
    assert record["seed_sha256"]==driver.digest(out/"SEED_INPUT.txt")
    assert all(command["exit_code"]==0 and not command["timed_out"] for command in record["commands"])
    assert record["ncp_launches"]==0 and record["old_campaign_reruns"]==0
