#!/usr/bin/env python3
"""Independent Decimal80 R8 reference, integrated from independent author design.
No production import, no ODE solve, no adaptive parameter search or retry.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent
OUT = ROOT/"raw/REFERENCE_RESULTS.json"
R6SHA = "1a3b55f7c14a64a10a651de2df7b7f7d2df24d0b9e809b729f32d73377c90e84"
R7SHA = "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15"
REFSHA = "e403c7803c080fd4f26be71a93b782b02d874f80ef11c85a706bea71e2a743cd"
INPUTSHA = "3ff9c2535e5c0ce6ffa5e9671de15aad6649e0996cd9b9e275cc290facd8d330"
EXPSHA = "002a66a30961b21e566a940462468c9ea8e1bc868d98549d3ea79d164c239957"
PARENT = "c1badb7de44131715a4998d76515506da5573707"
HD = ["two_state_no_reaction","two_state_nonlinear","two_state_coarse_source_defect",
      "saved_native_nine_state_K_conditional_feedback"]
SOURCES = {
 "R6":("provider_registry_molecular_r6_20261027/raw/PRIMARY_RESULTS.json",R6SHA,"9989728decbae54e637bf30aaec961ed2b1931d4"),
 "R7":("provider_registry_molecular_r7_20261027/raw/PRIMARY_RESULTS.json",R7SHA,"479d5ef4e44ad5046dc25926fa96f4900042606e"),
 "saved":("provider_registry_molecular_r7_20261027/raw/REFERENCE_RESULTS.json",REFSHA,"81624667a28180d221c057922abf295f046e2365"),
 "input":("provider_registry_molecular_r7_20261027/verification/PRIMARY_INPUT.json",INPUTSHA,"7697c8e6980cd40872990a3cd0258d40b0154b5e"),
}
ZERO,ONE = Decimal(0),Decimal(1)
CHECKS = []
def utc(): return datetime.now(timezone.utc).isoformat()
def sha(raw): return hashlib.sha256(raw).hexdigest()
def Q(x):
    if isinstance(x,bool) or isinstance(x,float): raise ValueError("Non-exact input")
    return Fraction(x)
def D(x):
    if isinstance(x,Decimal):
        if not x.is_finite(): raise ValueError("Nonfinite")
        return x
    x=Q(x)
    return Decimal(x.numerator)/Decimal(x.denominator)
def pair(x):
    if not isinstance(x,(list,tuple)) or len(x)!=2: raise ValueError("Pair required")
    return [D(v) for v in x]
def flat(x):
    if isinstance(x,(list,tuple)):
        for y in x: yield from flat(y)
    else: yield x
def eq(a,b):
    if isinstance(a,(list,tuple)) or isinstance(b,(list,tuple)):
        return isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)) and len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
    return Q(a)==Q(b)
def record(name,ok,evidence=None,components=1,failed=None):
    CHECKS.append({"name":name,"status":"PASS" if ok else "FAIL","component_comparisons":components,
                   "failed_components":(0 if ok else components) if failed is None else failed,
                   "evidence":evidence or {}})
def require(ok,name,evidence=None):
    record(name,bool(ok),evidence)
    if not ok: raise ValueError(name)
def parse(raw):
    def bad(x): raise ValueError("Nonfinite JSON "+x)
    return json.loads(raw,parse_float=Decimal,parse_constant=bad)
def compare(name,produced,reference,kind="arithmetic"):
    pp,rr=list(flat(produced)),list(flat(reference))
    if len(pp)!=len(rr):
        record(name,False,{"lengths":[len(pp),len(rr)]}); return
    bad=[]; failures=0; maxabs=ZERO; mindiff=None; maxdiff=None
    for i,(p,r) in enumerate(zip(pp,rr)):
        p,r=D(p),D(r); diff=p-r; scale=max(ONE,abs(p),abs(r))
        low=Decimal("1e-60")*scale if kind=="arithmetic" else Decimal("5e-14")*scale
        high=Decimal("1e-30")*scale if kind=="arithmetic" else low
        mindiff=diff if mindiff is None else min(mindiff,diff)
        maxdiff=diff if maxdiff is None else max(maxdiff,diff)
        maxabs=max(maxabs,abs(diff))
        if not -low<=diff<=high:
            failures+=1
            if len(bad)<12: bad.append({"index":i,"production":p,"reference":r,"difference":diff})
    record(name,failures==0,{"policy":kind,"min_difference":mindiff,"max_difference":maxdiff,
                           "max_absolute_difference":maxabs,"first_failures":bad},len(pp),failures)
def containment(name,actual,upper):
    aa,uu=list(flat(actual)),list(flat(upper))
    if len(aa)!=len(uu):
        record(name,False,{"lengths":[len(aa),len(uu)]}); return
    bad=[]; failed=0; worst=None
    for i,(a,u) in enumerate(zip(aa,uu)):
        a,u=D(a),D(u); tol=Decimal("2e-12")+Decimal("2e-10")*max(abs(a),abs(u))
        excess=a-u-tol; worst=excess if worst is None else max(worst,excess)
        if excess>0:
            failed+=1
            if len(bad)<12: bad.append({"index":i,"actual":a,"upper":u,"tolerance":tol})
    record(name,failed==0,{"max_excess_after_tolerance":worst,"first_failures":bad,
                          "role":"Saved binary64 sample corroboration, not rigorous new ODE enclosure"},len(aa),failed)
def pointer(doc,p):
    for key in p.split("/")[1:]:
        key=key.replace("~1","/").replace("~0","~")
        doc=doc[int(key)] if isinstance(doc,list) else doc[key]
    return doc
def controls():
    z=[["0","0"],["0","0"]]
    return {
     "noforcing":(z,["0","0"],["2","3"],["2","3"],"1/2",2,"0"),
     "constantforcing":(z,["2","3"],["1","1"],["5","5"],"1/2",2,"2"),
     "nilpotent":([["0","1"],["0","0"]],["0","0"],["1","2"],["8","2"],"1",1,"2"),
     "negative_d":([["0","0"],["0","-1/2"]],["0","3"],["2","2"],["2","5"],"1/2",2,"0"),
     "positive_d":([["0","0"],["0","1/2"]],["0","3"],["2","1"],["2","8"],"1/2",2,"0"),
    }
def independent(B,g,delta,initial,baseline,blocks,caps):
    a,b=pair(B[0]); c,d=pair(B[1]); gr,ge=pair(g); R0,E0=pair(initial)
    dt=D(delta); N=len(baseline); h=[ONE]
    for n in range(1,N+1):
        h.append(min([h[n-1]]+[D(k["rho"])*h[n-k["steps"]] for k in blocks if k["steps"]<=n]))
    e=(d*dt).exp(); phi=dt if d==0 else (e-ONE)/d
    powers=[ONE]
    for _ in range(N): powers.append(powers[-1]*e)
    prev=[pair(x) for x in baseline]; passes=[]
    for p in (1,2):
        F=[a*x[0]+b*x[1]+gr for x in prev]; L=[c*x[0]+ge for x in prev]
        whole=[]; ends=[[R0,E0]]
        for n in range(N):
            rw=h[n]*R0+dt*(sum((h[n-j-1]*F[j] for j in range(n)),ZERO)+F[n])
            shift=1 if d<=0 else 0
            ew=powers[n if d<=0 else n+1]*E0+phi*(sum((powers[n-j-shift]*L[j] for j in range(n)),ZERO)+L[n])
            whole.append([min(prev[n][0],rw),min(prev[n][1],ew)])
            ends.append([h[n+1]*R0+dt*sum((h[n-j]*F[j] for j in range(n+1)),ZERO),
                         powers[n+1]*E0+phi*sum((powers[n-j]*L[j] for j in range(n+1)),ZERO)])
        capped=[row[:] for row in ends]
        for i,v in caps.items(): capped[i]=[min(capped[i][k],v[k]) for k in range(2)]
        passes.append({"pass":p,"F_upper":F,"L_upper":L,"whole_cells":whole,"raw_endpoints":ends,"endpoints":capped})
        prev=whole
    return {"h":h,"e":e,"phi":phi,"passes":passes,"whole_cells":prev,"endpoints":passes[-1]["endpoints"]}
def binding(name,cert,wanted,ids=None):
    bb=cert["kernel"]["binding"]
    for k,v in wanted.items(): require(bb.get(k)==v,name+": binding "+k)
    sid=bb["state_ids"]
    require(len(sid)==len(set(sid)) and all(isinstance(x,str) and x for x in sid),name+": state identities")
    if ids is not None: require(list(sid)==list(ids),name+": exact state order")
    require(re.fullmatch("[0-9a-f]{64}",bb["source_sha256"]) is not None,name+": source hash syntax")
def caps_for(name,cert,r7,ci,delta):
    case=r7["hd_cases"][ci]; wanted={}
    for bi,block in enumerate(case["blocks"]):
        prefix=f"/hd_cases/{ci}/blocks/{bi}"
        for qi,q in enumerate(block["queries"]):
            wanted[prefix+f"/queries/{qi}/bound"]=(Q(block["t0"])+Q(q["t"]),q["bound"],"saved_R7_query")
        wanted[prefix+"/certificate/w_next_upper"]=(Q(block["t0"])+Q(block["certificate"]["H"]),block["certificate"]["w_next_upper"],"saved_R7_endpoint")
    actual=cert["cap_provenance"]; ps=[x["source_pointer"] for x in actual]
    require(len(wanted)==18 and len(ps)==18 and len(set(ps))==18 and set(ps)==set(wanted),name+": eighteen exact cap sources")
    caps={}
    for item in actual:
        p=item["source_pointer"]; t,v,kind=wanted[p]; idx=t/delta
        require(idx.denominator==1 and item["index"]==int(idx) and Q(item["time"])==t and item["source_kind"]==kind and item["source_sha256"]==R7SHA and eq(item["upper"],v) and eq(pointer(r7,p),v),name+": original cap "+p)
        i=int(idx); vv=pair(v); caps[i]=[min(caps.get(i,vv)[k],vv[k]) for k in range(2)]
    return caps
def check_certificate(name,cert,B,g,delta,initial,baseline,blocks,caps):
    N=len(baseline); kernel=cert["kernel"]
    require(cert["cells"]==N and Q(cert["delta"])==delta,name+": fixed grid")
    for field,wanted in [("B",B),("g",g),("initial",initial),("baseline_cells",baseline)]:
        require(eq(cert[field],wanted),name+": exact "+field)
    require([p["pass"] for p in cert["passes"]]==[1,2],name+": two passes")
    require(kernel["cells"]==N and kernel["bits"]==128 and Q(kernel["delta"])==delta and len(kernel["h"])==N+1,name+": kernel dimensions")
    actual=kernel["certificates"]
    tuples=lambda rows:[(Q(x["H"]),Q(x["rho"]),x["steps"]) for x in rows]
    require(len(actual)==len(blocks) and len(set(tuples(actual)))==len(actual) and set(tuples(actual))==set(tuples(blocks)),name+": source H/rho")
    require(all(type(x["steps"]) is int and 0<x["steps"] and Q(x["H"])==x["steps"]*delta and 0<=Q(x["rho"])<=1 for x in actual),name+": exact integer steps")
    h=[Q(x) for x in kernel["h"]]; wit=kernel["witness"]; ids={x["id"]:x for x in actual}
    require(len(wit)==N+1 and len(ids)==len(actual),name+": witnesses")
    bad=[]
    for n,w in enumerate(wit):
        good=False
        if n==0: good=h[0]==1 and w=={"kind":"nonexpansive","index":0}
        elif w.get("kind")=="previous_lag": good=w["index"]==n-1 and h[n]==h[n-1]
        elif w.get("kind")=="block_composition" and w.get("id") in ids:
            k=ids[w["id"]]; j=n-k["steps"]
            good=j>=0 and w["index"]==j and 0<=h[n]-Q(k["rho"])*h[j]<=Fraction(1,2**128)
        if n: good=good and 0<=h[n]<=h[n-1]<=1
        if not good: bad.append(n)
    record(name+": outward source-backed kernel witnesses",not bad,{"failed_indices":bad[:12]},N+1,len(bad))
    require(min(Q(x) for x in [B[0][0],B[0][1],B[1][0],*g,*initial])>=0,name+": positive couplings")
    require(abs(D(B[1][1])*D(delta))<=Decimal("0.25"),name+": frozen small argument")
    ref=independent(B,g,delta,initial,baseline,blocks,caps)
    compare(name+": lag ladder",kernel["h"],ref["h"])
    fac=cert["coarse_factors"]
    require(Q(fac["d"])==Q(B[1][1]) and Q(fac["delta"])==delta and fac["bits"]==128,name+": factor inputs")
    if "degree" in fac: require(fac["degree"]==48 and fac["dependency_sha256"]==EXPSHA,name+": exp dependency")
    compare(name+": exp factor",fac["e_upper"],ref["e"]); compare(name+": phi factor",fac["phi_upper"],ref["phi"])
    prev=baseline; prevend=None
    for prod,rr in zip(cert["passes"],ref["passes"]):
        pre=name+f": pass{prod['pass']}"
        require(all(len(prod[f])==sz for f,sz in [("whole_cells",N),("raw_endpoints",N+1),("endpoints",N+1),("F_upper",N),("L_upper",N)]),pre+": dimensions")
        for f in ("F_upper","L_upper","whole_cells","raw_endpoints","endpoints"): compare(pre+": "+f,prod[f],rr[f])
        old,new=list(flat(prev)),list(flat(prod["whole_cells"]))
        strict=sum(Q(x)<Q(y) for x,y in zip(new,old))
        require(all(0<=Q(x)<=Q(y) for x,y in zip(new,old)),pre+": exact descent")
        require(strict==prod["strictly_tightened_cell_components"],pre+": strict count",{"count":strict})
        if prevend is not None: require(all(Q(x)<=Q(y) for x,y in zip(flat(prod["endpoints"]),flat(prevend))),pre+": endpoint descent")
        for cap in cert["cap_provenance"]:
            idx,v=cap["index"],cap["upper"]
            require(all(Q(prod["endpoints"][idx][k])<=Q(v[k]) for k in (0,1)),pre+": retained exact cap index"+str(idx))
        prev=prod["whole_cells"]; prevend=prod["endpoints"]
    require(eq(cert["whole_cells"],prev) and eq(cert["endpoints"],prevend),name+": final aliases")
    return ref
def saved_trajectory(name,saved,case,cert,delta):
    require(saved["id"]=="HD:"+name and saved["physical_consumer_admitted"] is False,name+": saved identity/scope")
    require(all(len(saved[k])==193 for k in ("times","fine_states","coarse_states","R_E")),name+": 193 saved rows")
    errors=[abs(D(t)-D(delta*i)) for i,t in enumerate(saved["times"])]
    bad=[i for i,e in enumerate(errors) if e>Decimal("5e-14")+Decimal("5e-15")*abs(D(delta*i))]
    record(name+": common clocks",not bad,{"maximum_error":max(errors),"failed_indices":bad[:12]},193,len(bad))
    pi=[D(x) for x in case["pi"]]; reconstructed=[]; shapes=True
    for fine,coarse in zip(saved["fine_states"],saved["coarse_states"]):
        shapes=shapes and len(fine)==len(pi)+3 and len(coarse)==4
        x=[D(v) for v in fine[3:]]; total=sum(x,ZERO)
        reconstructed.append([sum((abs(v-p*total) for v,p in zip(x,pi)),ZERO),abs(total-D(coarse[3]))])
    require(shapes,name+": saved state dimensions")
    compare(name+": reconstruct saved R/E",saved["R_E"],reconstructed,"saved")
    containment(name+": all saved endpoints",saved["R_E"],cert["endpoints"])
    actual=[]; upper=[]
    for n in range(192):
        actual.extend([saved["R_E"][n],saved["R_E"][n+1]])
        upper.extend([cert["whole_cells"][n],cert["whole_cells"][n]])
    containment(name+": both boundaries of closed cells",actual,upper)
    return {"saved_clocks":193,"new_ODE_runs":0,"max_clock_error":max(errors)}
def closed_control(spec):
    B,g,initial,base,rho,m,F=spec
    rho=D(rho); R0,E0=pair(initial); F=D(F); L=D(g[1]); d=D(B[1][1]); dt=Decimal(1)/8
    phi=dt if d==0 else ((d*dt).exp()-ONE)/d
    def hh(n): return rho**(n//m)
    def hs(n):
        if rho==1: return Decimal(n)
        q,r=divmod(n,m)
        return Decimal(m)*(ONE-rho**q)/(ONE-rho)+Decimal(r)*rho**q
    ends=[]; whole=[]
    for n in range(9):
        t=Decimal(n)*dt; z=(d*t).exp()
        E=E0+L*t if d==0 else z*E0+L*(z-ONE)/d
        ends.append([hh(n)*R0+dt*F*hs(n),E])
    for n in range(8):
        left=Decimal(n)*dt; right=Decimal(n+1)*dt
        if d==0: E=E0+L*right
        elif d<0:
            z=(d*left).exp(); E=z*E0+L*((z-ONE)/d+phi)
        else:
            z=(d*right).exp(); E=z*E0+L*(z-ONE)/d
        whole.append([min(D(base[0]),hh(n)*R0+dt*F*(hs(n)+ONE)),min(D(base[1]),E)])
    return ends,whole
def run(report):
    require(len(sys.argv)==1,"No adaptive arguments")
    src={}
    for label,(path,wanted,blob) in SOURCES.items():
        raw=(RESEARCH/path).read_bytes()
        b=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        require(sha(raw)==wanted and b==blob,label+": immutable source bytes")
        report["sources"][label]={"path":path,"sha256":sha(raw),"git_blob":b,"bytes":len(raw)}
        src[label]=parse(raw)
    r6,r7,saved=src["R6"],src["R7"],src["saved"]
    require(r6["status"]=="PASS_SCOPED_EXACT_CERTIFICATES" and r6["failure_count"]==0,"R6 saved admission")
    require(r7["status"]=="PASS" and r7["failure_count"]==0 and r7["input_sha256"]==INPUTSHA,"R7 saved admission/input")
    require(saved["status"]=="PASS" and saved["failure_count"]==0 and saved["primary_sha256"]==R7SHA,"Saved reference binding")
    raw=(ROOT/"raw/PRIMARY_RESULTS.json").read_bytes(); primary=parse(raw)
    report["R8_primary_sha256"]=sha(raw); report["R8_primary_bytes"]=len(raw)
    require(primary["status"].startswith("PASS") and primary["failure_count"]==0,"Primary actual PASS")
    core_sha=sha((ROOT/"src/volterra_feedback.py").read_bytes())
    require(primary["core_sha256"]==core_sha,"Primary matches actual frozen core")
    require([x["id"] for x in r7["hd_cases"]]==HD,"Fixed HD order")
    hd={x["id"]:x["certificate"] for x in primary["hd_cases"]}
    ctr={x["id"]:x["certificate"] for x in primary["controls"]}
    require(len(primary["hd_cases"])==len(hd)==4 and set(hd)==set(HD),"Four HD cases")
    require(len(primary["controls"])==len(ctr)==5 and set(ctr)==set(controls()),"Five controls")
    rb={x["id"]:x for x in r6["graph"]["blocks"]}
    common={"norm":"l1_on_kerP","generator_scope":"nominal_K","uniform_all_starts":True,"nonexpansive":True,"same_family_composition":True}
    for ci,name in enumerate(HD):
        try:
            case=r7["hd_cases"][ci]; cert=hd[name]; H=Q(case["H"]); dt=H/64
            require(len(case["blocks"])==3,name+": three macroblocks")
            B=case["coefficients"]["B"]; g=case["coefficients"]["g"]
            require(all(eq(b["certificate"]["B"],B) and eq(b["certificate"]["g"],g) and Q(b["certificate"]["H"])==H and Q(b["t0"])==i*H for i,b in enumerate(case["blocks"])),name+": constant global coefficients/clock")
            baseline=[case["blocks"][n//64]["certificate"]["whole_block_upper"] for n in range(192)]
            initial=[case["initial_error"]["R"],case["initial_error"]["E"]]
            bb={**common,"clock":case["coefficients"]["metadata"]["clock"]}
            if ci==3:
                bb.update(family_id="R6_native100K_paraH2_interval_family",source_sha256=R6SHA)
                blocks=[{"H":rb[k]["H"],"rho":rb[k]["rho_upper"],"steps":m} for k,m in [("native_mu_8",2),("native_mu_32",8),("native_mu_128",32),("native_mu_256",64)]]
                require(all(Q(b["lambda"])==Q(r6["graph"]["lambda"]) and eq(b["P_lower"],r6["graph"]["P_lower"]) for b in rb.values()),name+": retained common family data")
                require(H==Q(rb["native_mu_256"]["H"]) and Q(case["rho"])==Q(rb["native_mu_256"]["rho_upper"]),name+": native macro binding")
            else:
                bb.update(family_id="R7_symmetric_two_state_nominal_family",source_sha256=R7SHA)
                require(H==Fraction(1,4) and Q(case["rho"])==Fraction(5,8),name+": synthetic fixed pair")
                blocks=[{"H":"1/4","rho":"5/8","steps":64}]
            binding(name,cert,bb,case["coefficients"]["metadata"]["state_ids"])
            require(cert["baseline_expected_sha256"]==R7SHA,name+": baseline hash")
            caps=caps_for(name,cert,r7,ci,dt)
            ref=check_certificate(name,cert,B,g,dt,initial,baseline,blocks,caps)
            old=next(x for x in saved["hd_cases"] if x["id"]=="HD:"+name)
            samp=saved_trajectory(name,old,case,cert,dt)
            report["hd_cases"].append({"id":name,"independent_Decimal80":ref,"saved_reference":samp,"physical_consumer_admitted":False})
        except Exception as exc: record(name+": preserved exception",False,{"message":str(exc),"traceback":traceback.format_exc()})
    for name,spec in controls().items():
        try:
            B,g,ini,base,rho,m,F=spec; cert=ctr[name]; dt=Fraction(1,8)
            binding(name,cert,{**common,"family_id":"R8_declared_analytic_control_family","clock":"dimensionless analytic control"})
            require(len(cert["kernel"]["binding"]["state_ids"])==2 and cert["cap_provenance"]==[],name+": analytic control scope")
            ref=check_certificate(name,cert,B,g,dt,ini,[base]*8,[{"H":str(m*dt),"rho":rho,"steps":m}],{})
            ends,whole=closed_control(spec)
            for p in cert["passes"]:
                for field,wanted in [("raw_endpoints",ends),("endpoints",ends),("whole_cells",whole)]:
                    compare(name+f": pass{p['pass']} closed "+field,p[field],wanted)
            report["controls"].append({"id":name,"independent_Decimal80":ref,"closed_endpoints":ends,"closed_whole_cells":whole})
        except Exception as exc: record(name+": preserved exception",False,{"message":str(exc),"traceback":traceback.format_exc()})
    wanted={"gamma":"1","H":"1","epsilon":"1/4","J":"1"}
    require(all(Q(primary["late_forcing"][k])==Q(v) for k,v in wanted.items()),"Late forcing fixed input")
    gamma,H,eps,J=[D(wanted[k]) for k in ("gamma","H","epsilon","J")]
    actual=J*(ONE-(-gamma*eps).exp())/(gamma*eps); wrong=(-gamma*H).exp()*J
    record("Late forcing analytic counterexample",wrong<actual<=J,{"actual":actual,"wrong":wrong,"correct":J})
    dt=Decimal(1)/8
    record("Current-cell pulse coefficient one",dt*(J/dt)==J and J/2<J,{"current":J,"wrong_rho":J/2})
    report["late_forcing"]={"input":wanted,"actual_Decimal80":actual,"wrong_upper":wrong,"correct_upper":J}
    require(len(report["hd_cases"])==4 and len(report["controls"])==5,"Every frozen case completed")
def main():
    t0=time.monotonic()
    if OUT.exists():
        print('{"status":"FAIL","reason":"create-only output exists"}'); return 2
    report={"schema":"WU_R8_INDEPENDENT_REFERENCE_RESULT_V1","run_id":"WU_R8_REFERENCE_01","started_utc":utc(),
            "parent_commit":PARENT,"script_sha256":sha(Path(__file__).read_bytes()),
            "sources":{},"hd_cases":[],"controls":[],"checks":CHECKS,
            "execution":{"new_reference_runs":1,"CPU_limit_s":60,"external_wrapper_full_CPU_authoritative":True,
                         "arithmetic":"Independent Decimal80 direct convolutions and closed forms",
                         "production_imports":0,"new_ODE_runs":0,"old_science_replay":0,
                         "GITHUB_SHA":os.environ.get("GITHUB_SHA"),"GITHUB_RUN_ID":os.environ.get("GITHUB_RUN_ID"),
                         "observed_RLIMIT_CPU":list(resource.getrlimit(resource.RLIMIT_CPU))},
            "scope":{"physical_consumer_admitted":False,"physical_IVP":0,"global_remaining":None,
                     "trajectory_role":"Retained binary64 sample corroboration, no continuous ODE promotion"},
            "tolerances":{"arithmetic_lower_scaled":"1e-60","arithmetic_upper_scaled":"1e-30","saved_consistency_scaled":"5e-14",
                          "clock_atol":"5e-14","clock_rtol":"5e-15","trajectory_atol":"2e-12","trajectory_rtol":"2e-10"}}
    try: run(report)
    except Exception as exc: record("Run exception preserved",False,{"message":str(exc),"traceback":traceback.format_exc()})
    usage=resource.getrusage(resource.RUSAGE_SELF); cpu=usage.ru_utime+usage.ru_stime
    record("CPU before serialization",cpu<=60,{"seconds":cpu,"full_CPU":"external wrapper"})
    report.update(check_count=len(CHECKS),failure_count=sum(x["status"]=="FAIL" for x in CHECKS),
                  component_comparison_count=sum(x["component_comparisons"] for x in CHECKS),
                  failed_component_count=sum(x["failed_components"] for x in CHECKS),
                  process_CPU_before_serialization_s=cpu,wall_before_serialization_s=time.monotonic()-t0,
                  finished_utc_before_serialization=utc(),counts_are_not_distinct_physical_scenarios=True)
    report["status"]="PASS" if report["failure_count"]==0 else "FAIL"
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("x",encoding="utf-8") as f: f.write(json.dumps(report,indent=2,ensure_ascii=True,default=str,allow_nan=False)+"\n")
    print(json.dumps({k:report[k] for k in ("status","check_count","failure_count","component_comparison_count","failed_component_count")}))
    return 0 if report["status"]=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
