"""Separate proper-time endpoint effect from same-mean-scale optical-depth contrast.

No claim of a pure shear response: cases may differ in q magnitude, gas physics,
and proper-time clock. Source histories have independent source-identities.
"""
from pathlib import Path
import argparse, json
import numpy as np
from cold_history_tau import read_history, OPACITY_FACTOR


def prefix_tau(t, ne):
    dt = np.diff(t)
    return np.r_[0., np.cumsum((OPACITY_FACTOR/2)*dt*(ne[:-1]+ne[1:]))]


def tau_at(t, ne, tau, requested_t):
    """Exact integral of piecewise linear ne over stored nodes in binary64 arithmetic."""
    if not t[0] <= requested_t <= t[-1]:
        raise ValueError("Requested proper time out of domain")
    j = int(np.searchsorted(t, requested_t, side="right")-1)
    if j == len(t)-1:
        return float(tau[-1])
    h = requested_t-t[j]
    interval = t[j+1]-t[j]
    if interval <= 0:
        raise ValueError("Time not monotonic")
    ne_star = ne[j]+(ne[j+1]-ne[j])*(h/interval)
    return float(tau[j] + OPACITY_FACTOR*h*0.5*(ne[j]+ne_star))


def compute_case(path):
    case, v, sha, metadata = read_history(path)
    t = v["time_s"]
    ne = v["ne_proper_cm3"]
    return {"case":case,"t":t,"ne":ne,"tau":prefix_tau(t,ne),
            "sha":sha,"a_end":float(v["a"][-1]),"zbar_end":float(v["zbar"][-1])}


def compare(ca, cb):
    if abs(float(ca["t"][0]-cb["t"][0])) > 0:
        raise ValueError("Different time origins")
    if abs(ca["a_end"]-cb["a_end"]) > 1e-12 or abs(ca["zbar_end"]-cb["zbar_end"]) > 1e-12:
        raise ValueError("Not same terminal mean scale/redshift")
    tc = min(float(ca["t"][-1]),float(cb["t"][-1]))
    ta_c=tau_at(ca["t"],ca["ne"],ca["tau"],tc)
    tb_c=tau_at(cb["t"],cb["ne"],cb["tau"],tc)
    change_at_scale=float(cb["tau"][-1]-ca["tau"][-1])
    change_at_common_time=float(tb_c-ta_c)
    endpoint_time_contrib=float((cb["tau"][-1]-tb_c)-(ca["tau"][-1]-ta_c))
    decomposition_residual=(change_at_common_time+endpoint_time_contrib)-change_at_scale
    assert abs(decomposition_residual) <= 1e-12 * max(1.,abs(change_at_scale))
    return {
        "case_a":ca["case"],"case_b":cb["case"],
        "sha256_a":ca["sha"],"sha256_b":cb["sha"],
        "common_endpoint_proper_s":tc,
        "terminal_time_a_s":float(ca["t"][-1]),
        "terminal_time_b_s":float(cb["t"][-1]),
        "terminal_time_B_minus_A_s":float(cb["t"][-1]-ca["t"][-1]),
        "tau_a_at_common_time":ta_c,"tau_b_at_common_time":tb_c,
        "delta_tau_at_common_proper_time":change_at_common_time,
        "delta_tau_at_common_zbar":change_at_scale,
        "terminal_clock_contribution":endpoint_time_contrib,
        "decomposition_residual":decomposition_residual,
        "interp_scheme":"piecewise linear ne, integrated exactly within selected cell",
        "interpretation":"algebraic clock decomposition, NOT isolated shear coefficient",
        "status":"NUMERICAL_DIAGNOSTIC_NOT_CERTIFIED"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--a",type=Path,required=True)
    p.add_argument("--b",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report=compare(compute_case(args.a),compute_case(args.b))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
