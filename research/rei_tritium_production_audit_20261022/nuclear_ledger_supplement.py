"""Derive rate and energy/electron views from the saved nuclear sweep.

No trajectories or network ODEs are recomputed. This keeps the bounded
nominal/refinement result immutable while adding the requested ledgers.
"""
import json
import math

import numpy as np

import nuclear_network as net


def signed_sum(terms):
    positive = np.logaddexp.reduce([v for sign, v in terms if sign > 0]) if any(
        sign > 0 for sign, _ in terms) else -math.inf
    negative = np.logaddexp.reduce([v for sign, v in terms if sign < 0]) if any(
        sign < 0 for sign, _ in terms) else -math.inf
    sign, magnitude = net.signed_log_difference(float(positive), float(negative))
    return {"sign": sign, "absolute": net.report_log_value(magnitude)}


def main():
    contract = json.loads(net.CONTRACT.read_text())
    report = json.loads((net.HERE/"NUCLEAR_NETWORK_REPORT.json").read_text())
    with np.load(net.HERE/"NUCLEAR_NETWORK_HISTORIES.npz", allow_pickle=False) as data:
        temp = data["T_K"].copy()
        names = data["case_names"].tolist()
    kf, kr, _ = net.rate_table(contract, temp)
    np.savez_compressed(net.HERE/"NUCLEAR_NETWORK_LOG_RATE_TABLE.npz",
                        T_K=temp, family_ids=np.array([f["id"] for f in contract["families"]]),
                        log_forward_rate_m3_s_or_s_inv=kf,
                        log_reverse_rate_m3_s=kr)
    entries = {}
    for name in names:
        ledger = report["case_ledgers"][name]
        energy = []
        gamma = []
        beta = []
        electron = []
        for f, result in zip(contract["families"], ledger["families"]):
            q = result["Q_J_per_event"]
            for direction, key in ((1, "forward"), (-1, "reverse")):
                item = result[key]
                count_log = item["log10"]
                if count_log is None:
                    continue
                count_log *= math.log(10)
                if q:
                    signed = (direction*(1 if q > 0 else -1),
                              count_log+math.log(abs(q)))
                    energy.append(signed)
                    if f["kind"] == "radiative_capture":
                        gamma.append(signed)
                    if f["kind"] == "beta_minus":
                        beta.append(signed)
                if f.get("electrons_created") and direction == 1:
                    electron.append((1, count_log+math.log(f["electrons_created"])))
        entries[name] = {"total_signed_Q_J_per_baryon": signed_sum(energy),
                         "capture_gamma_escape_Q_J_per_baryon": signed_sum(gamma),
                         "beta_total_Q_J_per_baryon_unpartitioned": signed_sum(beta),
                         "beta_electrons_per_baryon": signed_sum(electron),
                         "beta_antineutrinos_per_baryon": signed_sum(electron)}
    payload = {"scope": contract["mode"], "origin": "saved NUCLEAR_NETWORK_REPORT.json",
               "rate_table": "NUCLEAR_NETWORK_LOG_RATE_TABLE.npz",
               "Q_meaning": "rest-mass deficit event integral; no thermal feedback",
               "capture_gamma": "escaping nuclear gamma Q approximation, recoil not partitioned",
               "beta_partition": "total Q only; electron kinetic versus neutrino unspecified",
               "case_ledgers": entries}
    (net.HERE/"NUCLEAR_NETWORK_ENERGY_LEDGER.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
