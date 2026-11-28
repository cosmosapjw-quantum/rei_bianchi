#!/usr/bin/env python3
"""Finite FTC transfer from fixed-family PHYS09 bounds; no source/root solve."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
from fractions import Fraction as Q

EXPECTED = "c6329fed8c411e1592bd1a0c63ebd9ca6151e81500ed1f46fb6b40f4b7758444"
CHECKS: list[dict] = []


def require(ok: bool, name: str) -> None:
    CHECKS.append({"id": name, "passed": bool(ok)})
    if not ok:
        raise ValueError(name)


def decode(v: dict, label: str) -> tuple[Q, Q]:
    lo, hi = (Q(int(v["exact"][s][0]), int(v["exact"][s][1])) for s in ("lo", "hi"))
    require(lo <= hi, label + ":ordered_exact")
    for side in ("lo", "hi"):
        f = v[side]
        require(math.isfinite(f), label + ":finite_" + side)
        require(struct.pack(">d", f).hex() == v[side + "_bits"], label + ":bits_" + side)
    require(Q.from_float(v["lo"]) <= lo <= hi <= Q.from_float(v["hi"]), label + ":outward_display")
    return lo, hi


def mul_positive(v: tuple[Q, Q], scale: Q) -> tuple[Q, Q]:
    if scale < 0:
        raise ValueError("FTC path length must be nonnegative")
    return v[0] * scale, v[1] * scale


def neg(v: tuple[Q, Q]) -> tuple[Q, Q]:
    return -v[1], -v[0]


def positive_ratio(a: tuple[Q, Q], b: tuple[Q, Q]) -> tuple[Q, Q]:
    if a[0] < 0 or b[0] <= 0:
        raise ValueError("positive_ratio requires nonnegative numerator and positive denominator")
    return a[0] / b[1], a[1] / b[0]


def decimal_outward(q: Q, side: str, significant: int = 9) -> str:
    if q == 0:
        return "0"
    # log10 only selects a candidate exponent; exact comparisons correct it.
    exp = int(math.floor(math.log10(abs(float(q)))))
    while abs(q) < Q(10) ** exp:
        exp -= 1
    while abs(q) >= Q(10) ** (exp + 1):
        exp += 1
    quantum = Q(10) ** (exp - significant + 1)
    scaled = q / quantum
    integer = scaled.numerator // scaled.denominator
    if side == "hi" and scaled.denominator != 1:
        integer += 1
    return f"{integer}e{exp-significant+1:+d}"


def encode(v: tuple[Q, Q], unit: str) -> dict:
    lo, hi = v
    sign = "STRICT_POSITIVE" if lo > 0 else "STRICT_NEGATIVE" if hi < 0 else "ZERO_CONTAINING"
    displays = [decimal_outward(lo, "lo"), decimal_outward(hi, "hi")]
    require(Q(displays[0]) <= lo <= hi <= Q(displays[1]), "output:outward_decimal")
    return {"unit": unit, "sign": sign,
            "exact": {"lo": [str(lo.numerator), str(lo.denominator)],
                      "hi": [str(hi.numerator), str(hi.denominator)]},
            "outward_decimal": displays,
            "plot_float_nearest": [float(lo), float(hi)]}


def semantic_cases() -> list[dict]:
    a, p, h, chi = Q(1, 3), Q(1, 5), Q(1, 7), Q(68, 5)
    base = 1 + a

    def x(lam: Q, birth: Q) -> Q:
        y = a + p * birth + h * lam
        return y / (1 + y)

    def delta(birth: Q) -> Q:
        return h / ((base + p * birth) * (base + p * birth + h))

    dx = x(Q(1), Q(1)) - x(Q(0), Q(1))
    require(dx == delta(Q(1)), "toy:closed_form_absolute_identity")
    ubox = (h / (base + p + h) ** 2, h / (base + p) ** 2)
    require(ubox[0] <= dx <= ubox[1], "toy:finite_response_inside_uniform_U")
    mixed = x(Q(1), Q(1)) - x(Q(0), Q(1)) - x(Q(1), Q(0)) + x(Q(0), Q(0))
    closed_mixed = -p * h * (2 * base + p + h) / (base * (base+p) * (base+h) * (base+p+h))
    require(mixed == delta(Q(1)) - delta(Q(0)) == closed_mixed < 0 < dx,
            "toy:positive_absolute_negative_mixed")
    require((-chi * dx) + chi * dx == 0 and -chi * mixed > 0,
            "toy:thermal_ionization_cancellation_and_mixed_sign")

    l0, l1, birth = Q(1, 4), Q(3, 4), Q(1)
    exact_subpath = h * (l1-l0) / ((base+p*birth+h*l0) * (base+p*birth+h*l1))
    sub_u = (h / (base+p*birth+h*l1)**2, h / (base+p*birth+h*l0)**2)
    sub_box = mul_positive(sub_u, l1-l0)
    require(exact_subpath == x(l1,birth)-x(l0,birth) and sub_box[0] <= exact_subpath <= sub_box[1],
            "toy:nonunit_path_length")
    require(mul_positive(sub_u,Q(0)) == (Q(0),Q(0)), "toy:zero_path")

    # g(lambda;alpha)=alpha+lambda/10. Changing alpha can reverse the finite sign.
    require(Q(1,10)>0 and (-1+Q(1,10))<0, "toy:changed_alpha_counterexample")
    require(encode((Q(-1),Q(1)),"toy")["sign"]=="ZERO_CONTAINING", "toy:zero_containing_preserved")
    rejected = False
    try:
        positive_ratio((Q(1),Q(2)),(Q(0),Q(1)))
    except ValueError:
        rejected = True
    require(rejected, "toy:zero_denominator_rejected")
    return [
        {"id":"competing_channels", "x":"(a+p*b+h*lambda)/(1+a+p*b+h*lambda)",
         "a":"1/3","p":"1/5","h":"1/7", "absolute":str(dx),"mixed":str(mixed)},
        {"id":"nonunit_FTC", "lambda":[str(l0),str(l1)],"absolute":str(exact_subpath)},
        {"id":"changed_alpha", "same_alpha_D":"1/10","mismatched_alpha_D":"-9/10"},
        {"id":"zero_semantics","zero_containing_preserved":True,"zero_denominator_rejected":True}]


def run(root: Path, output: Path) -> None:
    CHECKS.clear()
    output.mkdir(parents=True, exist_ok=False)
    source = root / "inputs/phys09/PROJECTED_RESULTS.json"
    blob = source.read_bytes()
    require(hashlib.sha256(blob).hexdigest() == EXPECTED, "input:pinned_sha256")
    data = json.loads(blob)
    plan = json.loads((root / "inputs/PLAN_OBSERVABLE_CONTRACTS.json").read_text())
    contract = plan["next_local_observables"]
    require(contract["fixed_b_amp"] == 1 and contract["theta_domain"] == {"lambda":[0,1],"b_amp":[0,1]},
            "input:fixed_birth_and_theta")
    require([s["stage"] for s in data["stages"]] == ["full","first_half"], "input:stage_identity")
    fixtures = semantic_cases()
    rows, csv_rows = [], []
    for i, stage in enumerate(data["stages"]):
        name = stage["stage"]
        detail = data["details"][i]
        require(detail["stage"] == name and detail["same_COMMON_first_stage"] is True,
                name + ":same_COMMON_first_stage")
        require(detail["native_authority"] is False and all(v is None for v in detail["actual_native"].values()),
                name + ":native_ceiling_preserved")
        gamma = decode(stage["gamma"], name+":inherited_gamma")
        margins = [decode(v,name+":inherited_margin"+str(j)) for j,v in enumerate(stage["margins"])]
        require(gamma[1] < 1 and all(v[0] > 0 for v in margins), name+":inherited_strict_family_margins")
        # Read all 4 components without dropping the small signed helium intervals.
        u = [decode(v,name+":U"+str(j)) for j,v in enumerate(stage["U"])]
        w = [decode(v,name+":W"+str(j)) for j,v in enumerate(stage["W"])]
        absolute = {"x_HII":mul_positive(u[0],Q(1)), "w":mul_positive(u[3],Q(1))}
        require(absolute["x_HII"] == u[0] and absolute["w"] == u[3], name+":exact_unit_FTC_transfer")
        mixed = {"x_HII":w[0], "w":w[3]}
        result = {"stage":name,"dt_s":contract["stages_seconds"][name],"b_amp":1,
                  "lambda_path":[0,1],"chronology":"separate first stage from COMMON",
                  "claim_status":["derived","numerically checked","implementation-verified"],
                  "premise":"inherited fixed-alpha source-inclusion and C2 family",
                  "absolute":{},"mixed_reused":{},"modulation_over_absolute_at_b1":{}}
        for obs,unit in (("x_HII","dimensionless HII fraction"),("w","eV per H nucleus")):
            result["absolute"][obs] = encode(absolute[obs],unit)
            result["mixed_reused"][obs] = encode(mixed[obs],unit)
            for kind in ("absolute","mixed_reused"):
                v=result[kind][obs]
                csv_rows.append([name,result["dt_s"],1,kind,obs,unit,*v["outward_decimal"],v["sign"]])
        if u[0][0]>0 and u[3][1]<0 and w[0][1]<0 and w[3][0]>0:
            result["modulation_over_absolute_at_b1"] = {
                "ionization_suppression":encode(positive_ratio(neg(w[0]),u[0]),"dimensionless"),
                "thermal_loss_reduction":encode(positive_ratio(w[3],neg(u[3])),"dimensionless"),
                "denominator":"absolute HH response at b_amp=1; not total ionization/heating",
                "cosmological_negligibility_claim":False}
        rows.append(result)
    final = {"schema":"WU088_HH_PHYS12_ABSOLUTE_RESPONSE_V1", "rows":rows,
             "source_sha256":EXPECTED,"source_science":"REUSED_PHYS09_WITHIN_PHYS11",
             "arithmetic":"exact rational finite FTC transfer; no source/root evaluation",
             "consumer_absolute_threshold":None,"native_authority":False,
             "actual_native_root_U_V_W_I":None,"carried_second_half":"OPEN",
             "time_remainder":"OPEN","continuum_remainder":"OPEN","global_conservation":"OPEN",
             "full49":"OPEN","production":"OPEN","heavy_queue":[],"launch":False,
             "semantic_cases":fixtures,"checks":CHECKS,
             "checked_assertions":len(CHECKS),"assertions_are_unique_tests":False}
    (output/"ABSOLUTE_RESULTS.json").write_text(json.dumps(final,indent=2)+"\n")
    with (output/"OBSERVABLES.csv").open("w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["stage","dt_s","b_amp","quantity_kind","observable","unit","lower_outward","upper_outward","sign"])
        writer.writerows(csv_rows)
    def thin(x):
        if isinstance(x,dict):return {k:thin(v) for k,v in x.items() if k not in ("exact","checks","plot_float_nearest")}
        if isinstance(x,list):return [thin(v) for v in x]
        return x
    (output/"SUMMARY.json").write_text(json.dumps(thin(final),indent=2)+"\n")
    print(json.dumps({"status":"COMPLETED_PENDING_INDEPENDENT_REVIEW","rows":thin(rows),
                      "checked_assertions":len(CHECKS)},indent=2))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    run(args.root.resolve(),args.out.resolve())
