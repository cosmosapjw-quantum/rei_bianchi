#!/usr/bin/env python3
"""Independent 100-digit arithmetic readback + complete source-locked PHYS50 receipt."""
from __future__ import annotations
import hashlib,json,sys
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys50_trace_dtn import C_TRACE,FROZEN_SHA
from wu088_hh.phys49_dirichlet_collar import barrier_floor,dirichlet_floor


def run():
    base=ROOT/"research/hh_phys50_20261015"
    results=base/"results"
    original=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    cert=json.loads((results/"HIGH_TRACE_EXACT.json").read_text())
    assert sha(original)==cert["source_sha256"]==FROZEN_SHA
    assert C_TRACE==F(4849,16800)
    assert "357 passed in 191.25s" in (results/"FULL_SUITE.stdout").read_text()
    assert "EXIT=0" in (results/"FULL_SUITE.resource").read_text()
    assert "PHYS50_LOCAL_WOLFRAM_PASS=True" in (results/"CAS_WOLFRAM.stdout").read_text()
    with localcontext() as ctx:
        ctx.prec=105
        delta=2*(1+1/(D(20)-D(".7")))*(-D("38.6")).exp()
        beta=D(1693)/D(24300)-delta
        gamma=(D(4849)/D(16800)/beta).sqrt()
        lam=D(301657)/D(1190700)
        alpha=delta/(lam-delta)
        assert D(cert["trace_to_high_homogeneous_L2_gain_upper"])>=gamma
        assert D(cert["original_PHYS49_zero_trace_force_gain_upper"])>=alpha
        assert D(cert["screened_high_to_low_feedback_from_unknown_traces_upper"])>=delta*gamma
        assert D(cert["screened_high_to_low_feedback_from_low_field_upper"])>=delta*alpha
        independent={
          "schema":"WU088_HH_PHYS50_INDEPENDENT_DECIMAL_105DIGIT_READBACK_V1",
          "source_sha256":sha(original),
          "C_trace_exact":"4849/16800",
          "triangle_per_ell_energy_upper_margin_exact":"7/2400",
          "true_screening_delta":str(delta),
          "true_beta":str(beta),
          "true_gamma":str(gamma),
          "true_alpha":str(alpha),
          "true_trace_feedback":str(delta*gamma),
          "all_public_scientific_ceil_enclose_independent_105digit":True,
          "whole_suite":"357_PASS_EXIT0_191.25s",
          "Wolfram_triangle_C_DtN":"PASS_EXIT0"
        }
    target=results/"INDEPENDENT_READBACK.json"
    target.write_text(json.dumps(independent,indent=2)+"\n")
    files=[results/x for x in
      ["TRACE_FD_R32_MU128.json","TRACE_FD_R64_MU128.json",
       "TRACE_FD_R128_MU192.json","TRACE_FD_R64_MU192_L32.json"]]
    num=[json.loads(f.read_text()) for f in files]
    for z in num:
        assert z["source_sha256"]==FROZEN_SHA
        assert 0<z["discrete_DtN_eigen_min"]
        assert z["discrete_DtN_eigen_max"]<float(C_TRACE)
        assert z["energy_boundary_identity_abs_residual"]<5e-14
        assert z["matched_lu_rhs_max_difference"]<1e-12
    # Strip only representational escape used by chat-side file writer.
    report=base/"REPORT_KO.md"
    content=report.read_text()
    report.write_text(content.replace("\\`","`"))
    code=[
      "src/wu088_hh/phys50_trace_dtn.py",
      "scripts/phys50_trace_dtn.py",
      "scripts/phys50_trace_preview.py",
      "scripts/phys50_receipt.py",
      "tests/test_phys50_trace_dtn.py",
      "research/hh_phys50_20261015/CHECK_WOLFRAM_TRACE.wl",
      "research/hh_phys50_20261015/REPORT_KO.md",
      "research/hh_phys50_20261015/NEXT_DAG.json"
    ]
    actual=sorted(p for p in results.iterdir() if p.is_file() and
                  p.name!="EXECUTION_RECEIPT.json")
    receipt={
      "schema":"WU088_HH_PHYS50_EXECUTION_RECEIPT_V1",
      "date_KST":"2026-10-15",
      "parent_commit":"ce519958d930aa778cfce94134dba608ce552cd7",
      "original_frozen_sha256":sha(original),
      "rigorous_scope":"infinite ell>=21 all-m screened H-H Dirichlet two-boundary positive energy DtN r20..27 with nonzero X trace",
      "DtN_X_to_Xstar_exact_operator_upper":"4849/16800",
      "trace_to_L2_gain_upper":cert["trace_to_high_homogeneous_L2_gain_upper"],
      "source_to_high_L2_gain_upper":cert["original_PHYS49_zero_trace_force_gain_upper"],
      "high_to_low_screened_trace_gain_upper":
       cert["screened_high_to_low_feedback_from_unknown_traces_upper"],
      "physical_outgoing_high_boundary_trace":None,
      "targeted_pytest_PASS":24,
      "whole_project_pytest_PASS":357,
      "whole_project_test_seconds":191.25,
      "Wolfram_exact_and_numeric_PASS":True,
      "noncert_original_screened_finite_difference":[
       {k:v[k] for k in (
        "radial_grid_interiors","angular_Gauss_nodes","ell_high_modes",
        "discrete_DtN_eigen_max","measured_DtN_form",
        "energy_boundary_identity_abs_residual","measured_high_L2",
        "lu_batch_speedup")} for v in num],
      "original_src_doc_file_sha256":{name:sha(ROOT/name) for name in code},
      "result_sha256":{p.name:sha(p) for p in actual},
      "result_bytes":{p.name:p.stat().st_size for p in actual},
      "runtime":{"python":sys.version.split()[0],
                 "numpy_pin_declared":"2.3.5","local_numpy_actual":"2.4.2"},
      "local_codex":"NOT_USED","native_subagent":"NOT_RUN",
      "rei_bianchi_owner_mutations":0,"HH_R10_production":"OFF"
    }
    output=results/"EXECUTION_RECEIPT.json"
    output.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({
      "source_SHA256":sha(original),"report_bytes":report.stat().st_size,
      "independent_SHA256":sha(target),
      "receipt_SHA256":sha(output),"evidence_files":len(actual),
      "whole_project_pytest":357,"Wolfram_PASS":True}))
if __name__=="__main__":
    run()
