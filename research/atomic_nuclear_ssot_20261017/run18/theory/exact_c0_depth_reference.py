#!/usr/bin/env python3
"""Exact reference/export for the RUN17 stored-polynomial C0 depth repair.

This is a new RUN18 read-only calculation on frozen RUN17 bytes. It performs
no native RHS call or IVP solve. IEEE binary64 data are interpreted exactly.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import numpy as np

def identity(path):
    path=Path(path); data=path.read_bytes()
    return {"path":str(path.resolve()),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}

def exact(v):
    return Q.from_float(float(v))

def bits(v):
    return struct.pack(">d",float(v)).hex()

def bit_array(a):
    a=np.asarray(a)
    if a.ndim==0: return bits(a)
    return [bit_array(v) for v in a]

def qstrs(rows):
    return [[str(v) for v in row] for row in rows]

def write_new(path,value):
    with Path(path).open("x",encoding="utf-8") as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write("\n")

def basis_value_derivative(y0,coeff,x,h):
    # Direct independent basis, not SciPy's nested evaluation recurrence.
    value=exact(y0); deriv=Q(0)
    for k,raw in enumerate(coeff):
        a=exact(raw); p=1+k//2; q=(k+1)//2
        value += a*x**p*(1-x)**q
        derivative=p*x**(p-1)*(1-x)**q
        if q: derivative-=q*x**p*(1-x)**(q-1)
        deriv += a*derivative
    return value,deriv/h

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-result",type=Path,required=True)
    parser.add_argument("--domain-certificate",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args(); start=time.perf_counter()
    record=json.loads(args.control_result.read_text())
    if record["failure"] is not None or record["active_pairs"]!=252 or record["dimension"]!=265:
        raise ValueError("frozen complete 265-state first-birth control required")
    npz=args.control_result.parent/Path(record["state"]["path"]).name
    if identity(npz)["sha256"]!=record["state"]["sha256"]:
        raise ValueError("state archive identity mismatch")
    with np.load(npz,allow_pickle=False) as a:
        data={k:a[k].copy() for k in a.files}
    z=data["accepted_z"]; h=data["dense_h"]; old=data["dense_y_old"][:,:257]
    F=data["dense_F"][:,:,:257]; accepted=data["accepted_y"][:,:257]
    oldt=data["dense_t_old"]; n=len(h); dim=257
    if F.shape!=(n,7,dim) or accepted.shape!=(n+1,dim) or n!=23:
        raise ValueError("expected 23 saved dense pieces")
    if not all(np.isfinite(v).all() for v in (z,h,old,F,accepted,oldt)):
        raise ValueError("nonfinite input")
    if not np.array_equal(z[:-1],oldt) or not np.array_equal(old,accepted[:-1]):
        raise ValueError("accepted/predecessor identity mismatch")
    if not (np.diff(z)>0).all() or not (h>0).all():
        raise ValueError("invalid clocks")
    clocks=[(exact(z[i+1])-exact(z[i]))/exact(h[i]) for i in range(n)]
    # The bit fixture admits independent Rust evaluation of full coefficients.
    fixture={"schema":"rei.run18.dense-f64-bits.v1",
      "bit_encoding":"16 lowercase hexadecimal IEEE754 binary64 bits; big-endian textual u64",
      "source_control":identity(args.control_result),"source_npz":identity(npz),
      "pieces":n,"components":dim,"gas_components":5,"depth_components":252,
      "original_state_dimension":265,
      "excluded_components":"eight passive local absorption/heat ledgers; no gas/depth feedback",
      "accepted_z_bits":bit_array(z),"dense_t_old_bits":bit_array(oldt),
      "dense_h_bits":bit_array(h),"accepted_y_bits":bit_array(accepted),
      "dense_y_old_bits":bit_array(old),"dense_F_bits":bit_array(F)}
    endpoint_difference=[]; derivative_jumps=[]
    for i,x in enumerate(clocks):
        mismatch=[]
        for j in range(dim):
            v,der=basis_value_derivative(old[i,j],F[i,:,j],x,exact(h[i]))
            mismatch.append(exact(accepted[i+1,j])-v)
        endpoint_difference.append(mismatch)
        if i<n-1:
            row=[]
            for j in range(dim):
                _,left_der=basis_value_derivative(old[i,j],F[i,:,j],x,exact(h[i]))
                _,right_der=basis_value_derivative(old[i+1,j],F[i+1,:,j],Q(0),exact(h[i+1]))
                row.append(right_der-left_der)
            derivative_jumps.append(row)
    internal=endpoint_difference[:-1]
    cumulative=[[Q(0)]*dim]
    for row in internal:
        cumulative.append([a+b for a,b in zip(cumulative[-1],row)])
    # Repair_i = polynomial_i - cumulative_i. Both endpoint traces now agree.
    continuity_checks=[]
    for i,row in enumerate(internal):
        continuity_checks.extend(b-a-jump==0
            for a,b,jump in zip(cumulative[i],cumulative[i+1],row))
    gas_offsets=max((abs(v) for row in cumulative for v in row[:5]),default=Q(0))
    gamma=max((abs(v) for row in cumulative for v in row[5:]),default=Q(0))
    gamma_terminal=max(map(abs,cumulative[-1][5:]),default=Q(0))
    beta=gamma/(1-gamma) if 0<=gamma<1 else None
    beta_terminal=gamma_terminal/(1-gamma_terminal) if 0<=gamma_terminal<1 else None
    certificate=json.loads(args.domain_certificate.read_text())
    if not certificate["all_certificates_pass"]:
        raise ValueError("prior exact polynomial domain certificate required")
    if not any(row["sha256"]==identity(npz)["sha256"] for row in certificate["inputs"]):
        raise ValueError("domain certificate does not bind this archive")
    certs=certificate["certificates"][1:]
    if len(certs)!=n: raise ValueError("domain piece count mismatch")
    positivity=[]
    for i,(row,offset) in enumerate(zip(certs,cumulative)):
        if row["interval_z"]!=[float(z[i]),float(z[i+1])]:
            raise ValueError("certificate interval mismatch")
        original_lower=Q(row["minimum_depth_lower_bound_rational"])
        offset_radius=max(map(abs,offset[5:]),default=Q(0))
        lower=original_lower-offset_radius
        positivity.append({"piece":i,"original_all_depth_lower":str(original_lower),
          "offset_infinity_norm":str(offset_radius),"repair_all_depth_lower":str(lower),
          "all_repaired_depths_nonnegative":lower>=0})
    def group(lo,hi):
        values=[v for row in internal for v in row[lo:hi]]
        maxjump=max(map(abs,values),default=Q(0))
        largest_der=max((abs(v) for row in derivative_jumps for v in row[lo:hi]),default=Q(0))
        return {"internal_components_checked":len(values),
          "nonzero_internal_value_jumps":sum(v!=0 for v in values),
          "max_abs_value_jump":str(maxjump),"max_abs_value_jump_float":float(maxjump),
          "sum_interface_infinity_norms":str(sum((max(map(abs,row[lo:hi]),default=Q(0)) for row in internal),Q(0))),
          "nonzero_jump_after_pieces":[i for i,row in enumerate(internal) if any(row[lo:hi])],
          "terminal_endpoint_minus_polynomial_nonzero":sum(v!=0 for v in endpoint_difference[-1][lo:hi]),
          "max_abs_derivative_jump":str(largest_der),"max_abs_derivative_jump_float":float(largest_der),
          "derivative_jump_interpretation":"one-sided derivative mismatch; not an atom of the first-order state residual"}
    result={"schema":"rei.run18.exact-c0-depth-reference.v1",
      "status":"EXACT_RATIONAL_DEFINED_RECONSTRUCTION",
      "original_DAG_node":"P4-S4C-SPECTRAL-EDGE-SUPPORT",
      "source_inputs":[identity(args.control_result),identity(npz),identity(args.domain_certificate)],
      "clock_scales":[str(v) for v in clocks],"all_clock_scales_exactly_one":all(v==1 for v in clocks),
      "state_jump_orientation":"next-piece right trace minus previous-piece left trace at shared time",
      "accepted_alignment_exact":True,"groups":{"gas_q5":group(0,5),"depth252":group(5,257)},
      "internal_value_jumps":qstrs(internal),
      "terminal_stored_endpoint_minus_polynomial":[str(v) for v in endpoint_difference[-1]],
      "internal_derivative_jumps":qstrs(derivative_jumps),
      "cumulative_offsets_at_piece_start":qstrs(cumulative),
      "repair_definition":"new polynomial on piece i equals original polynomial minus cumulative signed prior value jumps",
      "all_repaired_interfaces_exactly_continuous":all(continuity_checks),
      "gas_offset_infinity_norm":str(gas_offsets),
      "all_domain_pieces_repaired_depth_nonnegative":all(row["all_repaired_depths_nonnegative"] for row in positivity),
      "repair_positivity":positivity,
      "gamma_all_pieces":str(gamma),"gamma_all_pieces_float":float(gamma),
      "gamma_terminal":str(gamma_terminal),"gamma_terminal_float":float(gamma_terminal),
      "beta_all_pieces":str(beta),"beta_all_pieces_float":float(beta),
      "beta_terminal":str(beta_terminal),"beta_terminal_float":float(beta_terminal),
      "beta_claim":"For the same gas and prescribed geometry, any fixed nonnegative cohort sum changes by at most beta times its original value under the depth repair. This is not a true-IVP or source-continuum error bound.",
      "bound_proof":"abs(exp(c)-1)<=exp(abs(c))-1<=Gamma/(1-Gamma), 0<=Gamma<1",
      "native_rhs_calls":0,"new_IVP_solves":0,"historical_M2_reruns":0,
      "source_code":identity(__file__),"command_argv":sys.argv,
      "python":sys.version,"numpy":np.__version__,"wall_seconds":time.perf_counter()-start}
    if gas_offsets or not result["all_repaired_interfaces_exactly_continuous"] or not result["all_domain_pieces_repaired_depth_nonnegative"] or beta is None:
        raise ValueError("bounded repair assumptions failed")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    fixture_path=args.output_dir/"DENSE_B_F64_BITS.json"
    write_new(fixture_path,fixture)
    result["rust_fixture"]=identity(fixture_path)
    write_new(args.output_dir/"EXACT_C0_DEPTH_REFERENCE.json",result)
    print(json.dumps({"status":result["status"],"all_clock_scales_exactly_one":result["all_clock_scales_exactly_one"],
        "gas":result["groups"]["gas_q5"],"depth":result["groups"]["depth252"],
        "gamma":result["gamma_all_pieces"],"beta":result["beta_all_pieces"],
        "beta_float":result["beta_all_pieces_float"],
        "repair_positive":result["all_domain_pieces_repaired_depth_nonnegative"],
        "wall_seconds":result["wall_seconds"]}))

if __name__=="__main__":
    main()

