#!/usr/bin/env python3
"""Exact comparison of saved HH results; no Rust/Arb integration is launched."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime,timezone
from decimal import Decimal,localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from flint import acb,arb,ctx,fmpq

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT/"src") not in sys.path:
    sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys67_coulomb_certificate import complex_ball_record,restore_complex_ball
from wu088_hh.phys68_profiles import load_profile_panel

SOURCE_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
OLD_D1_SHA = "c3e8640db5296c3a522397780ce74f09e0e5db334a11b671cecc7ada07758f95"
OUT = Path(__file__).resolve().parent
PROFILE = ROOT/"research/hh_phys68_20261019/profiles/run_l28_t65_completed"
RUST = ROOT/"research/hh_phys68_20261019/rust_reference/run_20261019"
PILOT = ROOT/"research/hh_phys66_20261018/c5c8/results"
OLD_D1 = ROOT/"research/hh_phys67_20261019/first_born/FIRST_BORN_CERTIFICATE.json"
SOURCE = ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path:Path)->dict:
    return json.loads(path.read_text())


def write(path:Path,data:dict)->None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite completed comparison {path}")
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")


def dyadic(record:dict)->Fraction:
    m,e=int(record["mantissa"]),int(record["exponent2"])
    return Fraction(m<<e) if e>=0 else Fraction(m,1<<(-e))


def rational(record:dict)->Fraction:
    n=int(record["numerator_hex"],16) if "numerator_hex" in record else int(record["numerator"])
    d=int(record["denominator_hex"],16) if "denominator_hex" in record else int(record["denominator"])
    if d<=0:raise ValueError("nonpositive rational denominator")
    return Fraction(n,d)


def fraction_record(value:Fraction)->dict:
    with localcontext() as context:
        context.prec=30
        display=str(Decimal(value.numerator)/Decimal(value.denominator))
    return {"numerator":str(value.numerator),"denominator":str(value.denominator),
            "display_approximate":display}


def exact_f64(value:float)->Fraction:
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("an actual finite binary64 value is required")
    return Fraction(*value.as_integer_ratio())


def endpoint(value:arb)->Fraction:
    if not value.is_exact() or not value.is_finite():
        raise ValueError("exact finite Arb endpoint required")
    m,e=value.man_exp();m,e=int(m),int(e)
    return Fraction(m<<e) if e>=0 else Fraction(m,1<<(-e))


def sqrt_bounds(value:Fraction)->tuple[Fraction,Fraction]:
    if value<0:raise ValueError("nonnegative squared distance required")
    with ctx.workprec(512):
        result=arb(fmpq(value.numerator,value.denominator)).sqrt()
        return endpoint(result.lower()),endpoint(result.upper())


@dataclass(frozen=True)
class Rectangle:
    real_mid:Fraction
    imag_mid:Fraction
    real_rad:Fraction
    imag_rad:Fraction

    @classmethod
    def from_record(cls,value:dict):
        def part(name):
            row=value[name]
            return dyadic(row["midpoint"] if "midpoint" in row else row["mid"]), \
                   dyadic(row["radius"] if "radius" in row else row["rad"])
        rm,rr=part("real");im,ir=part("imag")
        if rr<0 or ir<0:raise ValueError("negative ball radius")
        return cls(rm,im,rr,ir)

    def inflate(self,error:Fraction):
        if error<0:raise ValueError("negative tail bound")
        return Rectangle(self.real_mid,self.imag_mid,self.real_rad+error,self.imag_rad+error)

    def contains(self,other:Rectangle)->bool:
        return all(abs(m-n)+s<=r for m,r,n,s in [
            (self.real_mid,self.real_rad,other.real_mid,other.real_rad),
            (self.imag_mid,self.imag_rad,other.imag_mid,other.imag_rad)])

    def overlaps(self,other:Rectangle)->bool:
        return abs(self.real_mid-other.real_mid)<=self.real_rad+other.real_rad and \
               abs(self.imag_mid-other.imag_mid)<=self.imag_rad+other.imag_rad

    def distance_bounds(self,point:tuple[Fraction,Fraction])->tuple[Fraction,Fraction]:
        squared_lower=squared_upper=Fraction(0)
        for center,radius,p in [(self.real_mid,self.real_rad,point[0]),
                                (self.imag_mid,self.imag_rad,point[1])]:
            separation=abs(center-p)
            squared_lower+=max(Fraction(0),separation-radius)**2
            squared_upper+=(separation+radius)**2
        low,_=sqrt_bounds(squared_lower);_,high=sqrt_bounds(squared_upper)
        return low,high


def true_error_record(rectangle:Rectangle,tail:Fraction,point:tuple[Fraction,Fraction])->dict:
    """For z_T in rectangle and |z_infinity-z_T|<=tail, bound |p-z_infinity|."""
    low,high=rectangle.distance_bounds(point)
    low=max(Fraction(0),low-tail);high+=tail
    norm_low,norm_high=rectangle.distance_bounds((Fraction(0),Fraction(0)))
    norm_low=max(Fraction(0),norm_low-tail);norm_high+=tail
    if norm_low<=0:raise ValueError("true modulus lower bound is unresolved")
    relative_low,relative_high=low/norm_high,high/norm_low
    return {
        "absolute_error_lower":fraction_record(low),"absolute_error_upper":fraction_record(high),
        "relative_error_lower":fraction_record(relative_low),"relative_error_upper":fraction_record(relative_high),
        "true_modulus_lower":fraction_record(norm_low),"true_modulus_upper":fraction_record(norm_high),
        "comparison_value_exact":{"real":fraction_record(point[0]),"imag":fraction_record(point[1])},
        "radial_tail_applied":fraction_record(tail),
        "relative_goal":"1/1000000","relative_goal_certified":relative_high<Fraction(1,1000000),
        "status":"CERTIFIED_ERROR_OF_THIS_STORED_COMPLEX_VALUE_ONLY",
        "unit":"a0^-1","algorithm_uniform_error_bound":False,
    }


def main()->None:
    started=time.perf_counter()
    if sha(SOURCE)!=SOURCE_SHA or sha(OLD_D1)!=OLD_D1_SHA:
        raise ValueError("protected source or inherited PHYS67 certificate identity mismatch")
    cert=read(PROFILE/"CERTIFICATE.json")
    request=read(PROFILE/"REQUEST.json")
    old=read(OLD_D1)
    rust_execution=read(RUST/"EXECUTION_RECORD.json")
    pilot=read(PILOT/"PILOT_L28_T65.json")
    if cert["status"]!="CERTIFIED_GOALS_MET" or cert["scientific_execution"]!="COMPLETE":
        raise ValueError("profile certificate is not complete")
    if cert["full_intermediate_sum"]!=list(range(29)) or cert["m"]!=0:
        raise ValueError("finite L28 m0 full intermediate sum mismatch")
    for obj in (cert,old,rust_execution,pilot):
        if obj["source_sha256"]!=SOURCE_SHA:raise ValueError("scientific source binding mismatch")
    req=cert["request"]
    if (req["max_ell"],req["ell"],req["ellprime"],req["outer"])!=(28,21,20,"65"):
        raise ValueError("certificate target differs")
    if cert["fingerprint"]!=request["fingerprint"] or cert["request"]!=request["binding"]["request"]:
        raise ValueError("request fingerprint mismatch")
    engine={name:sha(ROOT/"src/wu088_hh"/name) for name in request["binding"]["engine"]["files_sha256"]}
    if engine!=request["binding"]["engine"]["files_sha256"]:
        raise ValueError("profile engine source has changed since execution")
    d2=Rectangle.from_record(cert["D2_B_cutoff"])
    beta2=rational(cert["D2_radial_cutoff_error"])
    if rational(cert["D2_numerical_absolute_error_l1"])!=d2.real_rad+d2.imag_rad:
        raise ValueError("numerical radius bookkeeping mismatch")
    if rational(cert["D2_full_radial_absolute_error_about_cutoff_midpoint"])!=d2.real_rad+d2.imag_rad+beta2:
        raise ValueError("numerical plus tail bookkeeping mismatch")
    if not Rectangle.from_record(cert["D2_B_full_radial_box"]).contains(d2.inflate(beta2)):
        raise ValueError("published full radial box failed exact outward inclusion")
    rows=[]
    for steps in (2432,4864):
        path=RUST/f"RK4_{steps}.json";result=read(path)
        if (result["steps"],result["L"],result["target"],result["T"])!=(steps,28,[21,20],65):
            raise ValueError("Rust target mismatch")
        point=(exact_f64(result["d2"]["real"]),exact_f64(result["d2"]["imag"]))
        comparison=true_error_record(d2,beta2,point)
        comparison.update({"name":f"Rust RK4 {steps}","path":str(path.relative_to(ROOT)),
                           "file_sha256":sha(path),"value_origin":"Exact binary64 result preserved by Rust JSON round-trip output"})
        rows.append(comparison)
    if pilot["ells"]!=list(range(29)) or pilot["m"]!=0 or pilot["outer"]!=65.0 or pilot["reported_indices"]!=[21,20]:
        raise ValueError("stored pilot scope mismatch")
    pilot_npz=PILOT/"PILOT_L28_T65.npz"
    with np.load(pilot_npz,allow_pickle=False) as archive:
        values=archive["contributions"]
        if values.shape!=(3,29,29) or values.dtype!=np.dtype("complex128"):
            raise ValueError("stored pilot contribution layout mismatch")
        value=values[1,21,20]
        point=(exact_f64(float(value.real)),exact_f64(float(value.imag)))
    json_value=pilot["terms"][1]["physical_entry"]
    if point!=(exact_f64(json_value[0]),exact_f64(json_value[1])):
        raise ValueError("pilot NPZ and JSON do not encode the same binary64 value")
    comparison=true_error_record(d2,beta2,point)
    comparison.update({"name":"Existing PHYS66 L28 T65 pilot D2(21,20)",
                       "path":str(pilot_npz.relative_to(ROOT)),"file_sha256":sha(pilot_npz),
                       "source_scope":"Earlier independently recovered PHYS66 C5-C8 pilot; no solver rerun or new final-9933 artifact claim."})
    rows.append(comparison)
    beta1=rational(cert["analytic_radial_cutoff"]["terms"][0]["radial_cutoff_bound"])
    d1=Rectangle.from_record(cert["D1_B_cutoff"]["20,21"])
    d1_full=d1.inflate(beta1)
    old_full=Rectangle.from_record(old["full_radial_enclosure"])
    d1check={
        "status":"CONSISTENT_NESTED_ENCLOSURES" if old_full.contains(d1_full) else "ENCLOSURE_NESTING_NOT_ESTABLISHED",
        "old_full_contains_new_full":old_full.contains(d1_full),"full_boxes_overlap":old_full.overlaps(d1_full),
        "new_full_absolute_error_l1":fraction_record(rational(cert["D1_B_full_radial_absolute_error_l1"]["20,21"])),
        "old_numerical_absolute_error_l1":fraction_record(rational(old["numerical_complex_error_upper"])),
        "new_radius_treatment":"Exact cutoff rectangle plus the L28 beta1 disk enclosed by a Cartesian square.",
        "scope":"Same original single first-Born entry, m0; no intermediate angular sum.",
        "old_certificate_sha256":sha(OLD_D1),"new_certificate_sha256":sha(PROFILE/"CERTIFICATE.json"),
        "old_integrator_reruns":0,
    }
    if not d1check["old_full_contains_new_full"] or not all(row["relative_goal_certified"] for row in rows):
        raise ArithmeticError("a stored-result comparison gate failed")
    identities={str(path.relative_to(ROOT)):sha(path) for path in [
        PROFILE/"CERTIFICATE.json",PROFILE/"REQUEST.json",OLD_D1,
        RUST/"EXECUTION_RECORD.json",RUST/"SEED_INPUT.txt",RUST/"RK4_2432.json",RUST/"RK4_4864.json",
        PILOT/"PILOT_L28_T65.json",pilot_npz,SOURCE,Path(__file__),
    ]}
    report={"schema":"PHYS68_SAVED_RESULTS_VALIDATION_V1","status":"PASS_SCOPED",
            "timestamp_utc":datetime.now(timezone.utc).isoformat(),"source_sha256":SOURCE_SHA,
            "source_file_identities":identities,"profile_engine_identities":engine,
            "D2_stored_value_error_certificates":rows,"D1_inherited_consistency":d1check,
            "new_solver_runs":0,"new_rust_runs":0,"new_integrator_runs":0,
            "arithmetic_precision_bits":512,"elapsed_seconds":time.perf_counter()-started,
            "HH_R10":"OFF"}
    write(OUT/"SAVED_RESULTS_COMPARISON.json",report)

    # New local evaluation from the recorded profile representation.  This
    # regenerates coefficient formulas; it invokes no Volterra/D2 integration.
    eval_started=time.perf_counter()
    panel=load_profile_panel(SOURCE,PROFILE,75)
    saved=read(PROFILE/"panel_0075.json")
    saved_rows={tuple(row["pair"]):row for row in saved["payload"]["pairs"]}
    evaluations=[]
    with ctx.workprec(384):
        for pair in ((20,21),(21,28)):
            value=panel.evaluate_first_born(*pair,Fraction(1,8))
            at_center=panel.evaluate_first_born(*pair,0)
            stored_center=restore_complex_ball(saved_rows[pair]["D1_center"])
            loaded_q0=Rectangle.from_record(complex_ball_record(panel.q_coefficients[pair][0]))
            stored_q0=Rectangle.from_record(saved_rows[pair]["q_center"])
            if not value.is_finite() or not at_center.overlaps(stored_center) or not loaded_q0.contains(stored_q0):
                raise ArithmeticError("profile loader witness failed")
            evaluations.append({"pair":list(pair),"radius":"219/8","offset":"1/8",
                                "cutoff_profile_enclosure":complex_ball_record(value),
                                "center_roundtrip_overlaps_saved":True,
                                "decoded_q0_contains_exact_saved_q0":True,
                                "radial_tail_applied":False,"unit":"a0^-1"})
    witness={"schema":"PHYS68_PROFILE_REUSE_WITNESS_V1","status":"PASS_SCOPED",
             "profile_certificate_sha256":sha(PROFILE/"CERTIFICATE.json"),"panel_index":75,
             "panel_payload_sha256":saved["payload_sha256"],"panel_center":str(panel.center),
             "input_source_sha256":SOURCE_SHA,"engine_identity_guard":"PASSED_BY_LOADER",
             "evaluations":evaluations,"elapsed_seconds":time.perf_counter()-eval_started,
             "coefficient_regeneration":True,"Volterra_or_D2_integration_invocations":0,
             "global_uniform_profile_error_claim":False,"HH_R10":"OFF"}
    write(OUT/"PROFILE_EVALUATION_WITNESS.json",witness)
    print(json.dumps({"status":report["status"],"D2_error_displays":[
        {"name":row["name"],"absolute_lower":row["absolute_error_lower"]["display_approximate"],
         "absolute_upper":row["absolute_error_upper"]["display_approximate"],
         "relative_upper":row["relative_error_upper"]["display_approximate"]} for row in rows],
        "D1_status":d1check["status"],"profile_witness":witness["status"]},indent=2))


if __name__=="__main__":main()
