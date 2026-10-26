"""Only two affected native hydrogen tangent probes, at the frozen new h."""
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from pw19_rec_callback import EVENT_OWNER, ISOTOPE_POLICY, ROUTE, PW19HeIINetwork

HERE = Path(__file__).resolve().parent
CALLBACK = HERE / "run01/CALLBACK.json"
CHECKS = HERE / "run01/CHECKS.json"
CALLBACK_SHA256 = "df5d289dac63d01200cbbffb30fb8c52e6760fc06748c3588c7f26c5d1e12e7e"
CHECKS_SHA256 = "8b2a87870e7b7c8d37fcd75422bb056671e0ba17c377df1178de877d9d5905e9"
OLD_H = 1e-4
NEW_H = 1e-2
LIMIT = 2e-8
NAMES = ("full_native_hydrogen_electron_feedback_JVP",
         "native_hydrogen_electron_feedback_electron_tangent")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    if digest(CALLBACK) != CALLBACK_SHA256 or digest(CHECKS) != CHECKS_SHA256:
        raise ValueError("ORIGINAL_FAILED_RAW_IDENTITY_CHANGED")
    saved, prior = json.loads(CALLBACK.read_text()),json.loads(CHECKS.read_text())
    previous = {c["name"]:c for c in prior["checks"]}
    if (prior["check_count"] != 84 or sum(bool(c["pass"]) for c in prior["checks"]) != 82 or
        {c["name"] for c in prior["checks"] if not c["pass"]} != set(NAMES)):
        raise ValueError("ORIGINAL_TWO_FAILURE_SCOPE_MISMATCH")
    y = np.asarray(saved["snapshot"]["Y"],dtype=float)
    t = saved["snapshot"]["temperature_K"]
    nb = saved["snapshot"]["nb_m3"]
    if y.shape != (21,) or not np.all(np.isfinite(y)) or not np.all(y >= 0):
        raise ValueError("ORIGINAL_MATCHED_STATE_INVALID")
    native = PW19HeIINetwork(source_z=2.479,source_route=ROUTE,
                             isotope_policy=ISOTOPE_POLICY,
                             photo_owners=(EVENT_OWNER,))
    v = np.zeros(21);v[1]=-1e-5;v[2]=1e-5
    if np.count_nonzero(native._Gphoto@v):
        raise ValueError("HYDROGEN_DIRECTION_HAS_UNEXPECTED_PHOTO_ACTION")
    plus_state,minus_state = y+NEW_H*v,y-NEW_H*v
    if np.any(plus_state < 0) or np.any(minus_state < 0):
        raise ValueError("NEW_H_TRIAL_OUTSIDE_PHYSICAL_STATE")
    center = native.evaluate(y,t,1.0,nb)
    plus = native.evaluate(plus_state,t,1.0,nb)
    minus = native.evaluate(minus_state,t,1.0,nb)
    fd = ((plus["rr_rhs"]+plus["dr_rhs"]+plus["decay_rhs"])-
          (minus["rr_rhs"]+minus["dr_rhs"]+minus["decay_rhs"]))/(2*NEW_H)
    analytic = center["jac"]@v
    scale = float(np.max(np.abs(analytic)))
    ne_analytic = nb*float(native.q@v)
    ne_fd = (plus["ne"]-minus["ne"])/(2*NEW_H)
    residuals = (float(np.max(np.abs(fd-analytic))/scale),
                 abs(ne_fd-ne_analytic)/abs(ne_analytic))
    tests = [{"name":name,"old_residual":previous[name]["residual"],
              "new_residual":residual,"unchanged_limit":LIMIT,"pass":residual<=LIMIT}
             for name,residual in zip(NAMES,residuals)]
    eps = np.finfo(float).eps
    qy = float(native.q@y)
    qv = float(native.q@v)
    result = {"scope":"only_two_failed_hydrogen_finite_difference_checks",
              "original_run01":{"callback_sha256":CALLBACK_SHA256,
                                "checks_sha256":CHECKS_SHA256,
                                "reused_passing_checks":82,
                                "original_failed_checks":list(NAMES)},
              "old_h":OLD_H,"new_h":NEW_H,"direction":v.tolist(),
              "source_z":saved["snapshot"]["source_z"],
              "native_analytic_Jv":analytic.tolist(),
              "native_finite_difference_RR_DR_decay":fd.tolist(),
              "native_ne_center_m3":center["ne"],"native_ne_plus_m3":plus["ne"],
              "native_ne_minus_m3":minus["ne"],
              "ne_analytic_tangent_m3":ne_analytic,"ne_finite_difference_m3":ne_fd,
              "trial_H1I_margins":[float(plus_state[1]),float(minus_state[1])],
              "trial_H1II_margins":[float(plus_state[2]),float(minus_state[2])],
              "epsilon_machine":eps,
              "elementary_roundoff_relative_scale_old":eps*abs(qy)/(OLD_H*abs(qv)),
              "elementary_roundoff_relative_scale_new":eps*abs(qy)/(NEW_H*abs(qv)),
              "reference_JVP_scale":scale,
              "tests":tests,"pass":all(c["pass"] for c in tests),
              "combined_evidence_passing_count":82+sum(c["pass"] for c in tests),
              "combined_evidence_total_count":84,
              "original_run01_rewritten":False,
              "source_or_native_physics_changed":False}
    return result


if __name__ == "__main__":
    output = Path(os.environ["PW19_REC_REPAIR_OUTPUT_DIR"])
    result = run()
    (output/"HYDROGEN_REPAIR.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"passed":result["pass"],"tests":result["tests"],
                      "combined_evidence_passing_count":result["combined_evidence_passing_count"]},allow_nan=False))
    raise SystemExit(0 if result["pass"] else 1)
