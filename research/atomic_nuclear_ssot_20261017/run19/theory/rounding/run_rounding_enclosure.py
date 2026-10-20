"""Run one saved-node interval-arithmetic unit, reusing frozen source bytes.

No new node/source/RHS evaluation or old trajectory is requested. Python Fraction
checks every output against the exact rational polynomial defined by input f64 bits.
"""
import argparse, csv, hashlib, json, os, platform, shutil, struct, subprocess, time
from fractions import Fraction as F
from pathlib import Path

EXPECTED_CUBIC = "7c45be5d93778d33d6c300b063b08efc4649c0106f26ac22720220328be4988f"
EXPECTED_DIRECTED = "2adadb6a5d77073e0a7d3d60aedfbf37e124d15a586a880d7d5a8c8d5307a814"
EXPECTED_CACHE = "dcfa521f60165632e6fa1c0d10473b194c8aab73844ee0a44ed2454e18f7a23b"
def sha(b): return hashlib.sha256(b).hexdigest()
def fbits(v): return f"{struct.unpack('<Q',struct.pack('<d',v))[0]:016x}"
def frombits(s): return struct.unpack("<d",struct.pack("<Q",int(s,16)))[0]
def record(path): return {"path":str(path),"bytes":path.stat().st_size,"sha256":sha(path.read_bytes())}
def dump_new(path,obj):
    with path.open("x") as f: json.dump(obj,f,indent=2);f.write("\n")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run19-root",type=Path,required=True)
    ap.add_argument("--run18-root",type=Path,required=True)
    ap.add_argument("--rustc",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    out=args.output
    out.mkdir(parents=True,exist_ok=False)
    source=out/"source"; source.mkdir()
    own=Path(__file__).resolve().parent
    cache=args.run19_root/"execution/unit_b/cache_probe01/cubic_default.bin"
    cubic=args.run19_root/"rate_cubic/src/lib.rs"
    directed=args.run18_root/"inventory/reuse_origin/crates/rodas5p-core/src/directed.rs"
    license_path=args.run18_root/"inventory/reuse_origin/LICENSE"
    raw=cache.read_bytes();cb=cubic.read_bytes();db=directed.read_bytes()
    assert sha(raw)==EXPECTED_CACHE
    assert sha(cb)==EXPECTED_CUBIC
    assert sha(db)==EXPECTED_DIRECTED
    assert raw[:16]==b"REI_TCUBIC_00001" and sha(raw[:-32])==raw[-32:].hex()
    nchan,nodes=struct.unpack_from("<II",raw,16)
    assert (nchan,nodes)==(16,32769)
    assert len(raw)==120+nodes*(nchan*8+1)+(nodes-1)*4
    lower,upper,log_lower,inv_step=struct.unpack_from("<4d",raw,56)
    assert (lower,upper)==(1.0,1e6)
    tags_start=88+nodes*nchan*8
    flag_start=tags_start+nodes
    flags=struct.unpack_from(f"<{nodes-1}I",raw,flag_start)
    eligible=[i for i in range(1,nodes-2) if flags[i]&(1<<31)==0]
    cells=[eligible[round(k*(len(eligible)-1)/31)] for k in range(32)]
    assert len(set(cells))==32
    theta=[0.0,0.25,0.371,0.5,0.75,1.0]
    fixture=out/"INPUT_STORED_NODES.csv"
    started=time.perf_counter()
    with fixture.open("x",newline="") as f:
        w=csv.writer(f)
        w.writerow(["case","cell","channel","theta_bits","a_bits","b_bits","c_bits","d_bits","tag","structural_zero"])
        case=0
        for i in cells:
            for th in theta:
                for j in range(nchan):
                    vals=[struct.unpack_from("<d",raw,88+((i+k)*nchan+j)*8)[0] for k in (-1,0,1,2)]
                    w.writerow([case,i,j,fbits(th),*[fbits(v) for v in vals],raw[tags_start+i],int(bool(flags[i]&(1<<j)))])
                    case+=1
    export_wall=time.perf_counter()-started
    # Extract the complete, unchanged scalar functions only. The source crate's
    # SHA cache implementation is not needed to evaluate its arithmetic kernel.
    begin=cb.index(b"#[inline]\npub fn centered_weights")
    end=cb.index(b"\npub fn source_digest",begin)
    fragment=cb[begin:end]
    (source/"kernel_fragment.rs").write_bytes(fragment)
    (source/"directed.rs").write_bytes(db)
    (source/"VIGILODE_LICENSE").write_bytes(license_path.read_bytes())
    (source/"main.rs").write_bytes((own/"main.rs").read_bytes())
    env=os.environ.copy()
    prefix=args.rustc.parent.parent
    env["LD_LIBRARY_PATH"]=str(prefix/"lib")
    compile_argv=[str(args.rustc),"--edition=2021","-O","-A","dead_code",str(source/"main.rs"),"-o",str(out/"stored_node_enclosure")]
    cstart=time.perf_counter()
    completed=subprocess.run(compile_argv,env=env,text=True,capture_output=True,timeout=30)
    compile_wall=time.perf_counter()-cstart
    (out/"compile.stdout.txt").write_text(completed.stdout)
    (out/"compile.stderr.txt").write_text(completed.stderr)
    dump_new(out/"COMPILE_COMMAND.json",{"argv":compile_argv,"exit_code":completed.returncode,"wall_seconds":compile_wall,"RUSTFLAGS":"","environment_overrides":{"LD_LIBRARY_PATH":env["LD_LIBRARY_PATH"]}})
    if completed.returncode: raise RuntimeError("compile failed; logs preserved")
    result_csv=out/"STORED_NODE_ENCLOSURES.csv"
    run_argv=[str(out/"stored_node_enclosure"),str(fixture),str(result_csv)]
    rstart=time.perf_counter()
    completed=subprocess.run(run_argv,env=env,text=True,capture_output=True,timeout=2)
    run_wall=time.perf_counter()-rstart
    (out/"run.stdout.txt").write_text(completed.stdout)
    (out/"run.stderr.txt").write_text(completed.stderr)
    dump_new(out/"RUN_COMMAND.json",{"argv":run_argv,"exit_code":completed.returncode,"wall_seconds":run_wall,"timeout_seconds":2})
    if completed.returncode: raise RuntimeError("new interval unit failed; logs preserved")
    rust_result=json.loads(completed.stdout)
    vstart=time.perf_counter()
    checked=0;zero=0;max_exact=F(0);max_case=None;max_bound=0.0
    for row in csv.DictReader(result_csv.open()):
        th=frombits(row["theta_bits"]);t=F.from_float(th)
        vals=[frombits(row[k+"_bits"]) for k in ("a","b","c","d")]
        a,b,c,d=map(F.from_float,vals)
        w=(-t*(t-1)*(t-2)/6,(t+1)*(t-1)*(t-2)/2,-(t+1)*t*(t-2)/2,(t+1)*t*(t-1)/6)
        ideal=sum(x*y for x,y in zip(w,(a,b,c,d)))
        lo,hi,actual,absbound=[frombits(row[k]) for k in ("ideal_lower_bits","ideal_upper_bits","value_bits","error_upper_bits")]
        assert F.from_float(lo)<=ideal<=F.from_float(hi)
        err=abs(F.from_float(actual)-ideal)
        assert err<=F.from_float(absbound)
        # Independent nearest arithmetic uses the same declared operation order.
        wf=(-th*(th-1.0)*(th-2.0)/6.0,(th+1.0)*(th-1.0)*(th-2.0)/2.0,
            -(th+1.0)*th*(th-2.0)/2.0,(th+1.0)*th*(th-1.0)/6.0)
        ordinary=((wf[0]*vals[0]+wf[1]*vals[1])+wf[2]*vals[2])+wf[3]*vals[3]
        assert fbits(ordinary)==row["value_bits"]
        if ideal>0:
            rel=err/ideal
            upper=frombits(row["relative_upper_bits"])
            assert rel<=F.from_float(upper)
            max_bound=max(max_bound,upper)
            if rel>max_exact: max_exact=rel;max_case={**row,"exact_ideal_numerator":str(ideal.numerator),"exact_ideal_denominator":str(ideal.denominator)}
        else:
            assert ideal==0 and actual==0 and row["relative_upper_bits"]=="-"
            zero+=1
        checked+=1
    verify_wall=time.perf_counter()-vstart
    result={
        "unit":"RUN19_C7_EXACT_STORED_NODE_CUBIC_ROUNDING",
        "status":"NUMERICALLY_CHECKED_WITH_EXACT_RATIONAL_CASE_VERIFICATION",
        "interpretation":"For each saved binary64 theta and four saved binary64 source-node values treated as exact reals, outward intervals enclose the ideal degree-three Lagrange polynomial. Its distance from the frozen rounded kernel is bounded per case. This is not a source-function or all-query enclosure.",
        "source_identity":{"cubic":record(cubic),"directed":record(directed),"kernel_fragment":record(source/"kernel_fragment.rs"),"adapter":record(source/"main.rs"),"runner":record(Path(__file__))},
        "input_identity":{"cache":record(cache),"cache_source_id_hex":raw[24:56].hex(),"fixture":record(fixture),"domain":[lower,upper],"nodes":nodes,"eligible_cells":len(eligible),"selected_cells":cells,"theta_binary64_hex":[fbits(t) for t in theta],"physical_channels":15,"zero_padding_channels":1},
        "results":{"checked_cases":checked,"positive_cases":checked-zero,"exact_zero_cases":zero,"all_exact_rational_values_enclosed":True,"all_exact_rational_errors_bounded":True,"all_independent_nearest_kernel_bits_equal":True,"maximum_exact_rational_relative_error_as_f64":float(max_exact),"maximum_exact_rational_relative_error":{"numerator":str(max_exact.numerator),"denominator":str(max_exact.denominator)},"maximum_directed_relative_error_upper":max_bound,"worst_exact_case":max_case,"rust_result":rust_result},
        "execution":{"compile_seconds":compile_wall,"fixture_export_seconds":export_wall,"rust_process_seconds":run_wall,"exact_fraction_verification_seconds":verify_wall,"bounded_calculation_seconds_excluding_compile":export_wall+run_wall+verify_wall,"rustc":subprocess.check_output([str(args.rustc),"--version"],env=env,text=True).strip(),"python":platform.python_version(),"compile_exit_code":0,"run_exit_code":0},
        "scope_exclusions":["No exact-real source formula rounding or table-node ln/exp construction error is included.","Theta is a specified stored binary64 value; this unit does not enclose ln(T), cell selection or coordinate rounding.","The native CI floor/structural-zero postprocessing is outside the raw-kernel comparison; all zero cases remain exactly zero.","Finite selected cases are not a supremum over every table cell or theta.","Source fit, Jacobian, gas/radiation feedback and trajectory error remain separate."],
        "native_rhs_calls":0,"source_function_calls":0,"new_ivp_runs":0,"historical_runs_repeated":0,"original_source_modifications":0,
        "output":record(result_csv),
    }
    dump_new(out/"STORED_NODE_ROUNDING_RESULT.json",result)
    print(json.dumps({"result":str(out/"STORED_NODE_ROUNDING_RESULT.json"),"sha256":sha((out/"STORED_NODE_ROUNDING_RESULT.json").read_bytes()),"cases":checked,"max_exact_relative":float(max_exact),"max_directed_relative_upper":max_bound,"execution":result["execution"]}))
if __name__=="__main__":main()
