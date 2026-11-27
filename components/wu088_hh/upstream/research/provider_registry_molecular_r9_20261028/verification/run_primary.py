from __future__ import annotations
from pathlib import Path
from fractions import Fraction
from copy import deepcopy
import datetime, hashlib, importlib.util, json, sys, time, traceback

BASE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
INPUT = BASE / "verification/PRIMARY_INPUT.json"
CORE = BASE / "src/causal_resolvent.py"
FREEZE = BASE / "raw/PREEXECUTION_FREEZE.json"
OUT = BASE / "raw/PRIMARY_RESULTS.json"
R8_SHA = "520110d1cae1677491aecd7216621c25f1098470c939ee027d5df3bde183686b"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if OUT.exists():
        raise SystemExit("Refuse to overwrite a previous primary result")
    started = time.process_time()
    wall = time.monotonic()
    result = {"schema":"WU_R9_PRIMARY_RESULTS_V1", "started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "checks":[], "hd_cases":[], "controls":[], "core_sha256":digest(CORE), "input_sha256":digest(INPUT),
              "runner_sha256":digest(Path(__file__)), "scope":{"old_science_replay":0,"new_ODE_runs":0,"new_source_certificate_runs":0,"physical_consumer_admitted":False},
              "budget":{"primary_runs":1,"CPU_limit_s":60,"wall_limit_s":90,"bits":128}}
    def check(name, ok, evidence=None):
        result["checks"].append({"name":name,"status":"PASS" if bool(ok) else "FAIL","evidence":evidence})
    module = None
    try:
        freeze = json.loads(FREEZE.read_text())
        if freeze.get("status") != "PASS" or not isinstance(freeze.get("files"), list):
            raise ValueError("Missing successful S05 exact source freeze")
        frozen = {}
        for item in freeze["files"]:
            rel = item["path"]
            p = (REPO / rel).resolve()
            if not p.is_relative_to(REPO.resolve()):
                raise ValueError("Freeze path escapes repository")
            raw = p.read_bytes()
            if hashlib.sha256(raw).hexdigest() != item["sha256"] or len(raw) != item["bytes"]:
                raise ValueError("Frozen input bytes differ: " + rel)
            frozen[rel] = item["sha256"]
        required = [CORE.relative_to(REPO).as_posix(), INPUT.relative_to(REPO).as_posix(), Path(__file__).resolve().relative_to(REPO).as_posix()]
        if not all(p in frozen for p in required):
            raise ValueError("Source freeze omits core, input, or this primary runner")
        check("frozen_source_bytes", True, {"files":len(frozen),"required":required})
        spec = json.loads(INPUT.read_text())
        if spec["R8_primary_sha256"] != R8_SHA or spec["bits"] != 128 or spec["modes"] != ["raw","capped"]:
            raise ValueError("Fixed primary contract differs")
        old_path = (REPO / spec["R8_primary_path"]).resolve()
        if not old_path.is_relative_to(REPO.resolve()) or digest(old_path) != R8_SHA:
            raise ValueError("Frozen R8 primary SHA256 differs")
        old = json.loads(old_path.read_text())
        result["source_sha256"] = {"R8_primary":R8_SHA,"core":result["core_sha256"],"input":result["input_sha256"]}
        check("saved_R8_source_identity", True, R8_SHA)
        loader = importlib.util.spec_from_file_location("wu_r9_frozen_core", CORE)
        module = importlib.util.module_from_spec(loader)
        sys.modules[loader.name] = module
        loader.loader.exec_module(module)
        Q, up = module.Q, module.up
        eps = Fraction(1,1<<128)
        def cap(cert, namespace, i, kind):
            return {"source_kind":"saved_R8_"+kind,"source_sha256":R8_SHA,
                    "source_pointer":f"/{namespace}/{i}/certificate/{kind}",
                    "delta":cert["delta"],"cells":cert["cells"],"binding":cert["kernel"]["binding"],"upper":cert[kind]}
        def kwargs(cert, namespace, i, mode):
            x = {k:cert[k] for k in ("B","g","delta","initial","kernel","coarse_factors")}
            x["binding"] = cert["kernel"]["binding"]
            if mode == "capped":
                x["whole_caps"] = cap(cert,namespace,i,"whole_cells")
                x["point_caps"] = cap(cert,namespace,i,"endpoints")
            return x
        for namespace in ("hd_cases","controls"):
            expected_ids = spec[namespace]
            if [row["id"] for row in old[namespace]] != expected_ids:
                raise ValueError("Saved case ordering differs: "+namespace)
            for i, item in enumerate(old[namespace]):
                cert = item["certificate"]
                expected_cells = spec["hd_cells" if namespace == "hd_cases" else "control_cells"]
                if cert["cells"] != expected_cells:
                    raise ValueError("Saved cell count differs")
                saved_before = json.dumps(cert,sort_keys=True)
                record = {"id":item["id"],"source_pointer":f"/{namespace}/{i}/certificate"}
                for mode in ("raw","capped"):
                    s = module.sweep(**kwargs(cert,namespace,i,mode))
                    record[mode] = s
                    tag = item["id"]+":"+mode
                    check(tag+":positive_exact_D", s["D"]>0, str(s["D"]))
                    check(tag+":geometry", len(s["whole_cells"])==expected_cells and len(s["endpoints"])==expected_cells+1)
                    check(tag+":nonnegative", all(v>=0 for key in ("raw_whole_cells","whole_cells","raw_endpoints","endpoints") for pair in s[key] for v in pair))
                    check(tag+":endpoint_covered_by_closed_cell", all(s["endpoints"][n+1][k]<=s["whole_cells"][n][k] for n in range(expected_cells) for k in (0,1)))
                    check(tag+":initial_endpoint", tuple(s["endpoints"][0])==tuple(map(Q,cert["initial"])))
                    if mode == "capped":
                        check(tag+":source_whole_no_worse", all(s["whole_cells"][n][k]<=Q(cert["whole_cells"][n][k]) for n in range(expected_cells) for k in (0,1)))
                        check(tag+":source_point_no_worse", all(s["endpoints"][n][k]<=Q(cert["endpoints"][n][k]) for n in range(expected_cells+1) for k in (0,1)))
                check(item["id"]+":source_object_unchanged", saved_before==json.dumps(cert,sort_keys=True))
                record["comparison"] = {"R8_final":cert["endpoints"][-1],"raw_final":record["raw"]["endpoints"][-1],"capped_final":record["capped"]["endpoints"][-1],
                    "strict_capped_whole_components":sum(record["capped"]["whole_cells"][n][k]<Q(cert["whole_cells"][n][k]) for n in range(expected_cells) for k in (0,1)),
                    "strict_raw_whole_components":sum(record["raw"]["whole_cells"][n][k]<Q(cert["whole_cells"][n][k]) for n in range(expected_cells) for k in (0,1))}
                result[namespace].append(record)
        controls = {row["id"]:row for row in result["controls"]}
        no = controls["noforcing"]["raw"]
        check("analytic_noforcing_block_geometric", all(no["endpoints"][n]==(Fraction(2,2**(n//2)),Fraction(3)) for n in range(9)))
        nil = controls["nilpotent"]["raw"]
        check("analytic_nilpotent_R_1_plus_2t_E_2", all(nil["endpoints"][n]==(1+Fraction(n,4),Fraction(2)) for n in range(9)))
        check("analytic_nilpotent_closed_cell", all(nil["whole_cells"][n]==(1+Fraction(n+1,4),Fraction(2)) for n in range(8)))
        cf = controls["constantforcing"]["raw"]
        cf_expected = [(Fraction(1)+(Fraction(1,4*2**(n//2)) if n%2 else 0),1+Fraction(3*n,8)) for n in range(9)]
        check("analytic_constantforcing_geometric_sum", all(cf["endpoints"][n]==cf_expected[n] for n in range(9)))
        bind = old["controls"][0]["certificate"]["kernel"]["binding"]
        def one(B=((0,0),(0,0)),g=(0,0),initial=(1,0),delta=1,e=1,phi=1,h1=1):
            return {"B":B,"g":g,"initial":initial,"delta":delta,"binding":bind,
                    "kernel":{"h":[1,h1],"delta":delta,"cells":1,"bits":128,"binding":bind},
                    "coarse_factors":{"d":B[1][1],"delta":delta,"e_upper":e,"phi_upper":phi,"bits":128}}
        near = module.sweep(**one(B=((Fraction(999,1000),0),(0,0))))
        check("near_singular_D_not_upward_rounded", near["D"]==Fraction(1,1000) and near["raw_whole_cells"][0][0]==1000)
        cp = module.sweep(**one(B=((0,Fraction(1,2)),(Fraction(1,4),0))))
        check("analytic_coupled_cell_inverse", Fraction(8,7)<=cp["raw_whole_cells"][0][0]<Fraction(8,7)+eps and Fraction(2,7)<=cp["raw_whole_cells"][0][1]<Fraction(2,7)+Fraction(5,4)*eps)
        fresh = module.sweep(**one(g=(1,0),initial=(0,0),h1=Fraction(1,2)))
        check("fresh_forcing_uses_h0", fresh["raw_endpoints"][1][0]==1 and fresh["endpoints"][1][0]==1)
        neg = module.sweep(**one(B=((0,0),(0,-1)),initial=(0,1),delta=Fraction(1,2),e=Fraction(2,3),phi=Fraction(1,2)))
        pos = module.sweep(**one(B=((0,0),(0,1)),initial=(0,1),delta=Fraction(1,2),e=2,phi=1))
        check("signed_d_whole_cell_initial_max", neg["raw_whole_cells"][0][1]==1 and pos["raw_whole_cells"][0][1]==2)
        check("directed_one_third", Fraction(1,3)<=up(Fraction(1,3))<Fraction(1,3)+eps)
        big = Fraction((1<<8191)+1,(1<<8191)-1)
        check("8192bit_rational_serialization_roundtrip", Q(json.loads(json.dumps(module.export(big))))==big)
        def reject(name, args):
            try:
                module.sweep(**args)
            except module.DomainError as exc:
                check(name,True,type(exc).__name__)
            else:
                check(name,False,"accepted invalid input")
        bad = one();bad["delta"]=0;reject("guard_zero_delta",bad)
        bad = one();bad["delta"]=1.0;reject("guard_binary_float",bad)
        bad = one();bad["bits"]=True;reject("guard_bool_precision",bad)
        for a,b,c,tag in ((-1,0,0,"a"),(0,-1,0,"b"),(0,0,-1,"c")):
            reject("guard_negative_"+tag,one(B=((a,b),(c,0))))
        reject("guard_zero_D",one(B=((1,0),(0,0))))
        reject("guard_negative_D",one(B=((2,0),(0,0))))
        reject("guard_coupled_zero_D",one(B=((0,1),(1,0))))
        bad=one();bad["kernel"]["h"][0]=Fraction(1,2);reject("guard_h0",bad)
        bad=one();bad["kernel"]["cells"]=193;reject("guard_cell_limit",bad)
        bad=one();bad["kernel"]["h"][1]=2;reject("guard_kernel_growth",bad)
        bad=one();bad["coarse_factors"]["delta"]=2;reject("guard_factor_clock",bad)
        bad=one();bad["coarse_factors"]["d"]=-1;reject("guard_factor_d",bad)
        bad=one();bad["coarse_factors"]["phi_upper"]=-1;reject("guard_negative_phi",bad)
        bad=one();bad["initial"]=[1<<8192,0];reject("guard_scalar_bit_limit",bad)
        source = kwargs(old["controls"][0]["certificate"],"controls",0,"capped")
        bad=deepcopy(source);bad["whole_caps"]["source_sha256"]="0"*64;reject("guard_cap_source_identity",bad)
        bad=deepcopy(source);bad["whole_caps"]["delta"]="1/7";reject("guard_cap_grid",bad)
        bad=deepcopy(source);bad["point_caps"]["source_kind"]="reference_trajectory";reject("guard_reference_sample_not_cap",bad)
        bad=deepcopy(source);bad["kernel"]["binding"]=dict(bad["kernel"]["binding"]);bad["kernel"]["binding"]["clock"]="other clock";reject("guard_family_clock",bad)
        check("canonical_json_rational_roundtrip", module.export(result["hd_cases"][0]["raw"]["D"])==str(result["hd_cases"][0]["raw"]["D"]))
    except Exception as exc:
        check("unexpected_execution_error",False,{"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()})
    result["check_count"] = len(result["checks"])
    result["failure_count"] = sum(c["status"]=="FAIL" for c in result["checks"])
    result["status"] = "PASS" if result["failure_count"]==0 else "FAIL"
    result["first_failure"] = next((c for c in result["checks"] if c["status"]=="FAIL"),None)
    result["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["internal_CPU_before_serialization_s"] = time.process_time()-started
    result["internal_wall_before_serialization_s"] = time.monotonic()-wall
    result["complete_process_CPU_authority"] = "outer Actions process record includes imports and serialization"
    def encode(v):
        if isinstance(v,Fraction):return str(v)
        if isinstance(v,dict):return {str(k):encode(x) for k,x in v.items()}
        if isinstance(v,(tuple,list)):return [encode(x) for x in v]
        return v
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("x",encoding="utf-8") as f:
        json.dump(encode(result),f,ensure_ascii=False,separators=(",",":"));f.write("\n")
    print(json.dumps({"status":result["status"],"checks":result["check_count"],"failures":result["failure_count"],"output":OUT.relative_to(REPO).as_posix()}))
    return 0 if result["status"]=="PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
