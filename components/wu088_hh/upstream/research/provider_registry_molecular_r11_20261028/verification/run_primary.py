"""One frozen R11 primary pass. No predecessor execution, source call, or ODE."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import sys
import time
import traceback

BASE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
CORE = BASE / "src/full_generator_blocks.py"
INPUT = BASE / "verification/PRIMARY_INPUT.json"
FREEZE = BASE / "raw/PREEXECUTION_FREEZE.json"
OUT = BASE / "raw/PRIMARY_RESULTS.json"
SOURCE_HASHES = {
    "R7_input": "3ff9c2535e5c0ce6ffa5e9671de15aad6649e0996cd9b9e275cc290facd8d330",
    "R7_primary": "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15",
    "R10_primary": "1713df54bc3653003614f3deba93212735a345e8d7220f053ab9af2d84677fb1",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(relative):
    p = (REPO / relative).resolve()
    if not p.is_relative_to(REPO.resolve()):
        raise ValueError("Source path escapes repository")
    return p


def main():
    if OUT.exists():
        raise SystemExit("Refuse to overwrite the first R11 primary result")
    cpu0, wall0 = time.process_time(), time.monotonic()
    result = {
        "schema": "WU_R11_PRIMARY_RESULTS_V1", "unit": "WU_FULL_GENERATOR_BLOCK_R11",
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_sha256": digest(INPUT), "core_sha256": digest(CORE),
        "runner_sha256": digest(Path(__file__)), "checks": [], "hd_cases": [], "controls": [],
        "generator_controls": [],
        "scope": {"old_science_replay": 0, "new_ODE_runs": 0, "predecessor_module_imports": 0,
                  "physical_consumer_admitted": False,
                  "lower_arrays": "chosen rational-q ideal comparison only"},
        "budget": {"primary_runs":1,"CPU_limit_s":60,"wall_limit_s":90,"bits":128,"degree":96},
    }
    module = None

    def check(name, ok, evidence=None):
        result["checks"].append({"name":name,"status":"PASS" if bool(ok) else "FAIL","evidence":evidence})

    def require(name, ok, evidence=None):
        check(name, ok, evidence)
        if not ok:
            raise ValueError("Required source/contract assertion failed: " + name)

    def guard():
        if time.process_time()-cpu0 > 58 or time.monotonic()-wall0 > 88:
            raise RuntimeError("R11 primary bounded pre-finalization stop")

    try:
        freeze = json.loads(FREEZE.read_text())
        if freeze.get("status") != "PASS" or not isinstance(freeze.get("files"), list):
            raise ValueError("Successful preexecution freeze required")
        frozen = {}
        for row in freeze["files"]:
            p = inside(row["path"])
            raw = p.read_bytes()
            if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ValueError("Frozen bytes differ: " + row["path"])
            frozen[row["path"]] = row["sha256"]
        required = [CORE.relative_to(REPO).as_posix(), INPUT.relative_to(REPO).as_posix(),
                    Path(__file__).resolve().relative_to(REPO).as_posix()]
        require("freeze_membership", all(p in frozen for p in required), required)
        result["freeze_sha256"] = digest(FREEZE)
        spec = json.loads(INPUT.read_text())
        require("fixed_primary_contract", spec.get("schema")=="WU_R11_FIXED_PRIMARY_INPUT_V1" and
                spec.get("unit")==result["unit"] and spec.get("bits")==128 and
                spec.get("degree")==96 and spec.get("hd_cells")==192 and spec.get("block_steps")==64)
        source = {}
        for name, sha in SOURCE_HASHES.items():
            row = spec["sources"][name]
            path = inside(row["path"])
            require("source_"+name+"_identity", row["sha256"]==sha and digest(path)==sha and
                    frozen.get(row["path"])==sha, row)
            source[name] = json.loads(path.read_text())
        result["source_sha256"] = SOURCE_HASHES
        require("saved_source_results_pass", all(source[n]["status"]=="PASS" for n in ("R7_primary","R10_primary")))
        require("saved_case_order", all([x["id"] for x in source[n]["hd_cases"]]==spec["hd_case_ids"]
                                      for n in SOURCE_HASHES))
        loader = importlib.util.spec_from_file_location("wu_r11_frozen_core", CORE)
        module = importlib.util.module_from_spec(loader)
        sys.modules[loader.name] = module
        loader.loader.exec_module(module)
        Q = module.Q

        def nominal(K, tau, rho, bind, ident, pointer, sha):
            return {"certificate_id":ident,"source_pointer":pointer,"source_sha256":sha,
                    "fixed_homogeneous_K":True,"uniform_all_starts":True,
                    "scientific_status":"CERTIFIED_K_BLOCK","K_sha256":module.matrix_identity(K),
                    "tau":tau,"rho_K":rho,"binding":deepcopy(bind)}

        def invariants(y):
            u,v,w,X = y
            return 2*u+w+X,v+X,v+w

        fields = ("id","K","pi","alpha","kf","destruction","coarse_kf_offset","H","rho",
                  "initial_fine","initial_coarse","density_box","q_norm_upper","branch_distance_upper",
                  "coarse_scalar_defect_upper","source_map_identity","source_scope","certificate_id")
        for i, fixture in enumerate(source["R7_input"]["hd_cases"]):
            guard()
            old = source["R7_primary"]["hd_cases"][i]
            saved = source["R10_primary"]["hd_cases"][i]["capped"]
            ident = fixture["id"]
            require(ident+":saved_fields", all(fixture[k]==old[k] for k in fields))
            K = tuple(tuple(map(Q,row)) for row in fixture["K"])
            p,ds,alpha = (tuple(map(Q,fixture[k])) for k in ("pi","destruction","alpha"))
            fine,coarse = (tuple(map(Q,fixture[k])) for k in ("initial_fine","initial_coarse"))
            aggregate = fine[:3]+(sum(fine[3:]),)
            eta = aggregate[3]-coarse[3]
            R0 = sum(abs(fine[j+3]-p[j]*aggregate[3]) for j in range(len(p)))
            require(ident+":same_invariant_class", invariants(aggregate)==invariants(coarse) and
                    tuple(a-b for a,b in zip(aggregate,coarse))==(-eta,-eta,eta,eta) and
                    R0==Q(old["initial_error"]["R"]) and abs(eta)==Q(old["initial_error"]["E"]) and
                    sum(fine[j+3]-p[j]*aggregate[3] for j in range(len(p)))==0)
            require(ident+":simplex_positive_state", sum(p)==sum(alpha)==1 and min(p+alpha+fine+coarse)>=0)
            box = {k:tuple(map(Q,fixture["density_box"][k])) for k in ("u","v","w","X")}
            require(ident+":whole_invariant_box", invariants(aggregate)==(Fraction(7,2),Fraction(3,2),2) and
                    box=={"u":(0,Fraction(3,2)),"v":(0,Fraction(3,2)),"w":(Fraction(1,2),2),"X":(0,Fraction(3,2))})
            qstar,theta = Q(fixture["q_norm_upper"]),Q(fixture["branch_distance_upper"])
            actualq = sum(abs(sum(K[j][k]*p[k] for k in range(len(p)))) for j in range(len(p)))
            require(ident+":q_theta", actualq<=qstar and sum(abs(a-b) for a,b in zip(alpha,p))<=theta<=2)
            mu,mv,mw,mx = (box[k][0] for k in ("u","v","w","X"))
            Mu,Mv,Mw,MX = (box[k][1] for k in ("u","v","w","X"))
            rate,spread = Q(fixture["kf"]),max(ds)-min(ds)
            coeff = {"c":Mw*spread/2,"d":-(rate*(mu+mv)+min(ds)*(mw+mx)),
                     "g_r":qstar*MX+rate*Mu*Mv*theta+Mw*MX*spread/2,
                     "g_e":Q(fixture["coarse_scalar_defect_upper"])}
            require(ident+":whole_domain_coefficients_unchanged", all(coeff[k]==Q(old["coefficients"][k])==Q(saved["coefficients"][k]) for k in coeff))
            require(ident+":same_exact_grid_initial", saved["cells"]==192 and Q(saved["delta"])==Q(fixture["H"])/64 and
                    tuple(map(Q,saved["initial"]))==(R0,abs(eta)))
            bind = deepcopy(saved["binding"])
            require(ident+":nominal_K_binding_reused", old["binding"]["H"]==fixture["H"] and
                    old["binding"]["rho"]==fixture["rho"] and old["binding"]["certificate_id"]==fixture["certificate_id"] and
                    old["binding"]["clock"]==bind["clock"] and bind["uniform_all_starts"] is True and
                    bind["same_family_composition"] is True)
            nc = nominal(K,fixture["H"],fixture["rho"],bind,fixture["certificate_id"],
                         f"/hd_cases/{i}/binding",SOURCE_HASHES["R7_primary"])
            args = {"K":fixture["K"],"pi":fixture["pi"],"destruction":fixture["destruction"],
                    "w_box":fixture["density_box"]["w"],"tau":fixture["H"],"rho_K":fixture["rho"],
                    **coeff,"delta":saved["delta"],"initial":saved["initial"],"cells":192,
                    "binding":bind,"nominal_certificate":nc}
            record = {"id":ident,"source_scope":fixture["source_scope"],
                      "source_pointers":{"R7_input":f"/hd_cases/{i}","R7_primary":f"/hd_cases/{i}",
                                         "R10_primary":f"/hd_cases/{i}/capped"}}
            before = json.dumps(args,sort_keys=True,default=str)
            for mode in ("raw","capped"):
                call = deepcopy(args)
                if mode=="capped":
                    for arg,key in (("point_caps","endpoints_upper"),("whole_caps","whole_cells_upper")):
                        call[arg] = {"source_kind":"saved_R10_"+key,"source_sha256":SOURCE_HASHES["R10_primary"],
                                     "source_pointer":f"/hd_cases/{i}/capped/{key}","cells":192,"delta":saved["delta"],
                                     "binding":deepcopy(bind),"upper":saved[key]}
                out = module.sweep(**call)
                record[mode] = out
                tag = ident+":"+mode
                check(tag+":geometry",len(out["endpoints_upper"])==193 and len(out["whole_cells_upper"])==192)
                check(tag+":nonnegative",all(x>=0 for key in ("endpoints_upper","whole_cells_upper") for row in out[key] for x in row))
                check(tag+":initial",tuple(out["endpoints_upper"][0])==(R0,abs(eta)))
                check(tag+":closed_cells_cover_endpoints",all(out["endpoints_upper"][n+j][k]<=out["whole_cells_upper"][n][k]
                                                            for n in range(192) for j in (0,1) for k in (0,1)))
                check(tag+":fresh_forcing_age_zero",out["h0"]==1 and out["kernel_lower"][0]==out["kernel_upper"][0]==1 and
                      out["forcing_lower"][1]<=Q(saved["delta"])*coeff["g_r"]<=out["forcing_upper"][1])
                gen=out["generator"]
                check(tag+":full_A_certificate",gen["uniform_all_starts"] and not gen["nominal_K_rho_directly_transferred"] and
                      0<=gen["q"]<=1 and gen["H_l1_norm"]==2*gen["b_H"])
                check(tag+":no_R_restart",out["R_memory_reset"] is False and out["block_steps"]==64)
                if mode=="raw":
                    check(tag+":comparison_interval_order",all(lo<=hi for a,b in zip(out["endpoints_lower"],out["endpoints_upper"]) for lo,hi in zip(a,b)))
                    check(tag+":block_left_limit_retained",all(out["whole_cells_upper"][n][0]>=out["R_affine_cells"][n]["right_left_limit_interval"][1] for n in (63,127,191)))
                else:
                    check(tag+":lower_absent",out["endpoints_lower"] is None)
                    for key in ("endpoints_upper","whole_cells_upper"):
                        check(tag+":"+key+"_no_worse_R10",all(a<=Q(b) for aa,bb in zip(out[key],saved[key]) for a,b in zip(aa,bb)))
            check(ident+":arguments_unchanged",before==json.dumps(args,sort_keys=True,default=str))
            record["comparison"]={"R10_final":saved["endpoints_upper"][-1],
                                  "raw_final":record["raw"]["endpoints_upper"][-1],
                                  "capped_final":record["capped"]["endpoints_upper"][-1]}
            for mode in ("raw","capped"):
                for key in ("endpoints_upper","whole_cells_upper"):
                    pairs=[(a,Q(b)) for aa,bb in zip(record[mode][key],saved[key]) for a,b in zip(aa,bb)]
                    record["comparison"][mode+"_"+key+"_counts"]={"less":sum(a<b for a,b in pairs),
                           "equal":sum(a==b for a,b in pairs),"greater":sum(a>b for a,b in pairs)}
            result["hd_cases"].append(record)

        control_bind={"family_id":"R11_exact_arithmetic_controls","state_ids":["s0","s1"],
                      "source_sha256":result["input_sha256"],"clock":"dimensionless exact R11 control clock","norm":"l1_on_kerP"}
        for control in spec["controls"]:
            guard()
            pars={k:v for k,v in control.items() if k!="id"}
            out=module.convolution_sweep(**pars,binding=control_bind)
            result["controls"].append({"id":control["id"],"parameters":pars,"raw":out})
            tag="control:"+control["id"]
            check(tag+":interval_order",all(0<=lo<=hi for a,b in zip(out["endpoints_lower"],out["endpoints_upper"]) for lo,hi in zip(a,b)))
            check(tag+":closed_cell_endpoints",all(out["endpoints_upper"][n+j][k]<=out["whole_cells_upper"][n][k]
                                                 for n in range(pars["cells"]) for j in (0,1) for k in (0,1)))
            check(tag+":h0_and_dimensions",out["h0"]==1 and len(out["kernel_lower"])==pars["cells"]+1)
            if control["id"] in ("zero","polynomial_q1"):
                r0,e0=map(Q,pars["initial"]);c,d,gr,ge,dt=(Q(pars[k]) for k in ("c","d","g_r","g_e","delta"))
                truth=[(r0+gr*n*dt,e0+(c*r0+ge)*n*dt+c*gr*(n*dt)**2/2) for n in range(pars["cells"]+1)]
                check(tag+":independent_exact_polynomial",all(out["endpoints_lower"][n][k]<=truth[n][k]<=out["endpoints_upper"][n][k]
                                                           for n in range(pars["cells"]+1) for k in (0,1)))
            if control["id"]=="late_forcing_q0":
                check(tag+":current_cell_not_contracted",out["endpoints_lower"][-1][0]==out["endpoints_upper"][-1][0]==Fraction(1,8))
                check(tag+":exact_E_ramp",out["endpoints_lower"][-1][1]==out["endpoints_upper"][-1][1]==Fraction(1,128))
            if control["id"]=="block_jump_left_limit":
                check(tag+":whole_exceeds_jumped_endpoint",out["whole_cells_upper"][1][0]==1 and out["endpoints_upper"][2][0]==Fraction(1,2))

        baseK=((-1,1),(1,-1)); tau=Fraction(1,4);rho=Fraction(5,8)
        base_nc=nominal(baseK,tau,rho,control_bind,"analytic exp(-1/2)<=5/8","/controls",result["input_sha256"])
        base={"K":baseK,"pi":("1/2","1/2"),"destruction":(0,0),"w_box":(0,2),"tau":tau,"rho_K":rho,
              "c":0,"d":0,"g_r":0,"g_e":0,"delta":"1/8","initial":(1,0),"cells":4,
              "binding":control_bind,"nominal_certificate":base_nc}
        for name,ds,p,Mw in (("zero_H",(0,0),("1/2","1/2"),2),("zero_Mw",(2,4),("1/2","1/2"),0),
                             ("additive_saturation",(2,4),("1/2","1/2"),2),("boundary_simplex",(2,4),(1,0),2)):
            args={k:base[k] for k in ("K","tau","rho_K","binding","nominal_certificate")}
            out=module.generator_certificate(**args,pi=p,destruction=ds,w_box=(0,Mw))
            result["generator_controls"].append({"id":name,"parameters":{"K":baseK,"pi":p,"destruction":ds,"w_box":(0,Mw),"tau":tau,"rho_K":rho},"certificate":out})
            check("generator:"+name+":conservative_H",all(sum(row[j] for row in out["H"])==0 for j in range(2)))
            if name in ("zero_H","zero_Mw"):
                check("generator:"+name+":unchanged_q",out["q"]==rho)
            if name=="additive_saturation":
                check("generator:additive_saturates_minorization_strict",out["q_additive"]==1 and out["q"]<1)
            if name=="boundary_simplex":
                check("generator:boundary_norm",out["b_H"]==4 and out["H_l1_norm"]==8)
        zK=((0,0),(0,0))
        zn=nominal(zK,tau,1,control_bind,"K=0 gives rho=1","/controls",result["input_sha256"])
        zc=module.generator_certificate(zK,("1/2","1/2"),(2,4),(0,2),tau,1,binding=control_bind,nominal_certificate=zn)
        check("generator:reducible_q1",zc["q"]==1)
        result["generator_controls"].append({"id":"reducible_q1","certificate":zc})
        b1=dict(control_bind,state_ids=["only"])
        n1=nominal(((0,),),tau,1,b1,"singleton trivial zero-mass subspace","/controls",result["input_sha256"])
        one=module.sweep(((0,),),(1,),(7,),(0,2),tau,1,0,-1,0,0,"1/8",(0,1),2,binding=b1,nominal_certificate=n1)
        check("singleton_zero_residual",one["generator"]["b_H"]==0 and all(row[0]==0 for row in one["endpoints_upper"]))
        n=13;bn=dict(control_bind,state_ids=["s"+str(i) for i in range(n)]);Kn=[[0]*n for _ in range(n)]
        nn=nominal(Kn,tau,1,bn,"zero generator rho=1","/controls",result["input_sha256"])
        dim=module.generator_certificate(Kn,[Fraction(1,n)]*n,[1]*n,(0,2),tau,1,binding=bn,nominal_certificate=nn)
        check("dimension13_exact_norm",dim["b_H"]==Fraction(12,13) and dim["H_l1_norm"]==Fraction(24,13))
        check("directed_one_third",module.down(Fraction(1,3))<=Fraction(1,3)<=module.up(Fraction(1,3)))

        def reject(name, args):
            try:
                module.sweep(**args)
            except module.DomainError as exc:
                check("guard:"+name,True,str(exc))
            else:
                check("guard:"+name,False,"Invalid input accepted")

        for key,value,name in (("delta",0,"zero_delta"),("delta",1.0,"float"),("g_r",True,"bool"),
                               ("c",-1,"negative_c"),("g_r",-1,"negative_gr"),("g_e",-1,"negative_ge"),
                               ("initial",(-1,0),"negative_initial"),("cells",193,"cell_limit"),
                               ("cells",True,"bool_cells"),("bits",127,"bits"),("degree",95,"degree"),
                               ("g_r",1<<8192,"scalar_limit"),("w_box",(-1,2),"negative_w"),
                               ("w_box",(2,1),"reversed_w"),("pi",("1/2","1/3"),"simplex"),
                               ("destruction",(-1,2),"negative_destruction"),("destruction",(1,),"destruction_dimension"),
                               ("destruction",(1000,1000),"certificate_exp_limit"),
                               ("K",((0,1),(1,-1)),"nonconservative_K"),("K",((1,-1),(-1,1)),"nonmetzler_K"),
                               ("rho_K",2,"rho_over_one"),("rho_K",-1,"negative_rho"),
                               ("delta","1/7","noncommensurate_grid"),("tau",100,"block_steps_limit"),
                               ("g_r",[1,2],"forcing_length"),("g_e",[0,0,-1,0],"negative_forcing_array"),
                               ("d",129,"scaled_exp_limit")):
            reject(name,dict(base,**{key:value}))
        for key,value,name in (("uniform_all_starts",False,"all_starts"),("fixed_homogeneous_K",False,"fixed_K"),
                               ("scientific_status","PROPOSED","uncertified_rho"),("K_sha256","0"*64,"K_identity"),
                               ("tau","1/3","nominal_tau"),("rho_K","1/2","nominal_rho"),
                               ("source_sha256","bad","nominal_source_sha"),("source_pointer","not_pointer","nominal_pointer")):
            nc=deepcopy(base_nc);nc[key]=value;reject(name,dict(base,nominal_certificate=nc))
        for key,value,name in (("clock","other clock","clock"),("state_ids",["s1","s0"],"state_order"),
                               ("family_id","other family","family"),("norm","total_variation","norm"),
                               ("source_sha256","bad","source_sha")):
            bind=deepcopy(control_bind);bind[key]=value;reject(name,dict(base,binding=bind))
        hd=source["R10_primary"]["hd_cases"][0]["capped"]
        validcap={"source_kind":"saved_R10_endpoints_upper","source_sha256":SOURCE_HASHES["R10_primary"],
                  "source_pointer":"/hd_cases/0/capped/endpoints_upper","cells":4,"delta":"1/8",
                  "binding":deepcopy(control_bind),"upper":[[1,1]]*5}
        for key,value,name in (("source_kind","trajectory_points","sample_caps"),("source_sha256","0"*64,"cap_source"),
                               ("source_pointer","/hd_cases/0/capped/whole_cells_upper","point_as_whole"),
                               ("delta","1/9","cap_clock_grid"),("cells",3,"cap_cells"),("cells",4.0,"cap_float_cells"),
                               ("upper",[[1,1]]*4,"cap_length"),("upper",[[0,0]]*5,"cap_initial")):
            cap=deepcopy(validcap);cap[key]=value;reject(name,dict(base,point_caps=cap))
        cap=deepcopy(validcap);cap["binding"]["clock"]="another";reject("cap_binding",dict(base,point_caps=cap))
        cap=deepcopy(validcap);cap["upper"][2]=[-1,0];reject("negative_cap",dict(base,point_caps=cap))
        whole=deepcopy(validcap);whole.update(source_kind="saved_R10_whole_cells_upper",source_pointer="/hd_cases/1/capped/whole_cells_upper",upper=[[1,1]]*4)
        reject("different_cap_cases",dict(base,point_caps=validcap,whole_caps=whole))
        result["first_failure"] = None
    except Exception as exc:
        result["first_failure"]={"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()}
        check("uncaught_exception",False,str(exc))
    result["check_count"]=len(result["checks"])
    result["failure_count"]=sum(x["status"]!="PASS" for x in result["checks"])
    result["status"]="PASS" if result["failure_count"]==0 else "FAIL"
    result["finished_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["internal_CPU_before_serialization_s"]=time.process_time()-cpu0
    result["internal_wall_before_serialization_s"]=time.monotonic()-wall0
    result["complete_process_CPU_authority"]="external execute_once OS rusage, including imports and serialization"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    def export(x):
        if isinstance(x,Fraction):return str(x)
        if isinstance(x,dict):return {k:export(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)):return [export(v) for v in x]
        return x
    OUT.write_text(json.dumps(export(result),indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":result["status"],"checks":result["check_count"],"failures":result["failure_count"],
                      "CPU_before_serialization_s":result["internal_CPU_before_serialization_s"]}))
    return 0 if result["status"]=="PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
