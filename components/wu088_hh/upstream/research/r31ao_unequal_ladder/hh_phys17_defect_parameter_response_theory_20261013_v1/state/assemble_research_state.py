#!/usr/bin/env python3
"""Assemble PHYS17 workflow metadata from immutable existing evidence."""
from __future__ import annotations
import datetime, hashlib, json, pathlib, platform, shutil, sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
P15=ROOT.parent/"HH_PHYS15_THEORY_20261012_v1"
P16=ROOT.parent/"HH_PHYS16_THEORY_20261013_v1"
STATE=ROOT/"state"
ACTIVE=pathlib.Path("/root/.codex/skills/remote-skills/skill-6aa0657100b08191b7d67482d1f97c1d")

def read(root,rel):
    return json.loads((root/rel).read_text())

def ident(root,rel):
    data=(root/rel).read_bytes()
    return {"root":root.name,"path":rel,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}

def main():
    before=STATE/"RESEARCH_STATE_BEFORE_COMPLETION_UPDATE.json"
    if not before.exists():
        shutil.copy2(STATE/"RESEARCH_STATE.json",before)
    state=json.loads(before.read_text())
    family=state["scope"] if isinstance(state["scope"],dict) else state["family_scope"]
    contract=read(ROOT,"contracts/INHERITED_PARAMETER_RESPONSE_CONTRACT.json")
    review=read(ROOT,"review/INDEPENDENT_REVIEW.json")
    decision=read(ROOT,"review/DECISION.json")
    theory=read(ROOT,"theory/PARAMETER_RESPONSE_CLAIMS.json")
    assert review["decision"]==decision["decision"]=="PROMOTE_SCOPED"
    assert len(theory["claims"])==8
    assert review["arithmetic_review"]["final_checks_passed"]==29
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    workflow_identity=[]
    for rel in ("scripts/run_record.py","references/WORKFLOW.json","references/THEORY_LOOP.md"):
        saved=ident(ROOT,"evidence/workflow_1_0_0/"+rel)
        active=ident(ACTIVE,rel)
        assert saved["sha256"]==active["sha256"],("workflow_copy_mismatch",rel)
        workflow_identity.append({"saved":saved,"active":active,"matches":True})
    (STATE/"WORKFLOW_IDENTITY.json").write_text(json.dumps({"workflow_version":"1.0.0","verified_utc":stamp,"files":workflow_identity},indent=2)+"\n")
    deps=[];evidence=[];dep_index={};ev_index={}
    def artifact(label,root,rel,kind,scope,extra_dependencies=()):
        d=ident(root,rel)
        did="D_"+label;eid="E_"+label
        assert did not in dep_index and eid not in ev_index
        row={"id":did,"identity":"sha256:"+d["sha256"]+";bytes:"+str(d["bytes"]),
             "description":scope,"artifact_identity":d}
        deps.append(row);dep_index[did]=row
        locator=rel if root==ROOT else "../"+root.name+"/"+rel
        ev={"id":eid,"kind":kind,"locator":locator,"scope":scope,
            "dependency_ids":[did,*extra_dependencies],"relation":"supports"}
        evidence.append(ev);ev_index[eid]=ev
        return eid
    contract_ids=[]
    for b in contract["input_bindings"]:
        root=P15 if b["root"]=="PHYS15" else P16
        actual=ident(root,b["path"])
        assert actual["bytes"]==b["bytes"] and actual["sha256"]==b["sha256"],b["id"]
        artifact("INPUT_"+b["id"],root,b["path"],"source",b["role"])
        contract_ids.append("D_INPUT_"+b["id"])
    assert len(contract_ids)==14
    artifact("CONTRACT",ROOT,"contracts/INHERITED_PARAMETER_RESPONSE_CONTRACT.json","resource",
             "Inherited PHYS16 parameter-response scope and P1-P4 acceptance contract",contract_ids)
    artifact("ENTRY",ROOT,"evidence/intake/ENTRY_INPUT_IDENTITIES.json","review",
             "Actual intake comparison of the 14 contract bindings and inherited source/root history",contract_ids)
    artifact("PARENT_DECISION",P16,"review/DECISION.json","decision","Inherited PHYS16 PROMOTE_SCOPED")
    artifact("PARENT_REMOTE",ROOT,"evidence/intake/PARENT_REMOTE_REFERENCE.json","storage",
             "Actually observed PHYS16 commit/PR and Drive/Dropbox metadata; not a PHYS17 backup receipt")
    specs=[
      ("THEOREM","theory/PARAMETER_RESPONSE_THEOREM_KO.md","derivation","Seven completed C2 theorems, exact source mapping and finite corollaries"),
      ("CLAIMS","theory/PARAMETER_RESPONSE_CLAIMS.json","derivation","Eight scientific claims with equation and scope mapping"),
      ("COROLLARIES","theory/PARAMETER_COROLLARIES.json","calculation","Five exact rational consequence intervals from run02"),
      ("NEXT_PROPOSAL","theory/NEXT_MIXED_RESPONSE_PROPOSAL_KO.md","derivation","Selected next mixed-response formulae; application not_run"),
      ("MAIN_CODE","src/parameter_response_application.py","implementation","Frozen run02 source; shared gas and dual photon derivative graph"),
      ("FORCING_CODE","src/forcing_feedback_decomposition.py","implementation","Frozen manual photon product rule and explicit/feedback implementation"),
      ("NEUMANN_CODE","src/derivative_neumann_readout.py","implementation","Frozen finite Neumann derivative error readout"),
      ("REVIEW_CODE_01","review/independent_arithmetic_review.py","implementation","Original exact Fraction reviewer with equality assumption, retained unchanged"),
      ("REVIEW_CODE_02","review/independent_arithmetic_review_v2.py","implementation","Corrected independent Fraction/Cramer reviewer; no candidate/helper import"),
      ("REVIEW","review/INDEPENDENT_REVIEW.json","review","Independent scoped scientific adoption and 29/29 final arithmetic checks"),
      ("REVIEW_HUMAN","review/INDEPENDENT_REVIEW_KO.md","review","Readable independent science review and actual failure correction"),
      ("SOURCE_REVIEW","review/SOURCE_AND_DERIVATION_REVIEW_KO.md","review","Direct original Rust source, He projector, density, sign and normalization review"),
      ("SOURCE_IDENTITIES","review/ORIGINAL_SOURCE_IDENTITIES.json","source","Four actually hashed original source/helper identities"),
      ("FORMULA_REVIEW","review/INITIAL_FORMULA_REVIEW_KO.md","derivation","Independent starting P1-P4 derivation"),
      ("DECISION","review/DECISION.json","decision","Root detached PROMOTE_SCOPED adoption; original candidate result status preserved"),
      ("LIT_REVIEW","literature/LITERATURE_REVIEW_KO.md","source","Four new primary references and two reused prior references, source-condition comparison"),
      ("LIT_BIB","literature/references.bib","source","Primary bibliography with DOI/URL"),
      ("LIT_SEARCH","literature/SEARCH_PROVENANCE.json","source","Actual SciSpace 1 search/10 records, Exa 4 searches/20 requested and 4 fetches"),
      ("WL_CODE","checks/wolfram/parameter_response_checks.wl","implementation","Actual Wolfram+xAct symbolic code"),
      ("WL_PRE","checks/wolfram/PRE_RUN.json","resource","Actual Wolfram evaluator pre-run command and 60-second constraint"),
      ("WL_RAW","checks/wolfram/WOLFRAM_XACT_EXECUTION.json","calculation","Completed actual Wolfram/xAct run: 6 tensor and 15 scalar values all exact zero"),
      ("WL_SUMMARY","checks/wolfram/SUMMARY.json","review","6 tensor checks, 9 scalar bundles and 15 scalar values, xPerm pure WL backend"),
      ("WORKFLOW","state/WORKFLOW_IDENTITY.json","resource","Captured validator/workflow/theory loop verified identical to the currently installed skill"),
    ]
    for label,rel,kind,scope in specs:artifact(label,ROOT,rel,kind,scope)
    for n,x in enumerate(read(ROOT,"review/ORIGINAL_SOURCE_IDENTITIES.json")["source_files"],1):
        root=P15 if x["root"]==P15.name else P16
        actual=ident(root,x["path"]);assert actual["sha256"]==x["sha256"]
        artifact("ORIGINAL_SOURCE_"+str(n),root,x["path"],"source","Original source used in the direct source/derivation review")
    executions=[];checks=[]
    runtime={"python":platform.python_version(),"location":"current shared executor",
             "arithmetic":"exact Fraction endpoints; application uses directed 256-significant-bit rounding"}
    def execution(label,directory,run_name,pre_name,code_eid,result_rel=None,failed_reason=""):
        run=read(ROOT,directory+"/"+run_name)
        artifact(label+"_PRE",ROOT,directory+"/"+pre_name,"resource","Actual recorded pre-run command and source identity")
        artifact(label+"_RUN",ROOT,directory+"/"+run_name,"calculation","Actual process completion, command, exit code and measured resources")
        refs=["E_"+label+"_PRE","E_"+label+"_RUN",code_eid]
        if result_rel:
            artifact(label+"_RESULT",ROOT,result_rel,"calculation","Unchanged exact output of "+label)
            refs.append("E_"+label+"_RESULT")
        row={"id":"X_"+label,"status":"completed" if run["exit_code"]==0 else "failed",
             "command":run["command"],"environment":dict(runtime),"evidence_refs":refs,
             "exit_code":run["exit_code"],"reason":failed_reason,
             "wall_seconds":run.get("wall_seconds",run.get("elapsed_seconds")),
             "peak_rss_kib":run.get("peak_rss_kib"),"new_source_calls":0,"new_root_solves":0,"history_replays":0}
        executions.append(row)
        return refs
    for label,directory in (("MAIN01","checks/application/run01"),("NEUMANN01","checks/application/neumann01")):
        artifact(label+"_CODE",ROOT,directory+"/SOURCE.py","implementation","Preserved exact source executed in the first failed attempt")
        artifact(label+"_DIAG",ROOT,directory+"/DIAGNOSIS.json","review","Observed first-attempt failure and implemented correction")
    execution("MAIN01","checks/application/run01","RUN_RECORD.json","PRE_RUN.json","E_MAIN01_CODE",
              failed_reason="KeyError on outgoing field; preserved PHYS11 schema uses outgoing_joint. Stopped before candidate result.")
    execution("MAIN02","checks/application/run02","RUN_RECORD.json","PRE_RUN.json","E_MAIN_CODE",
              "checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json")
    execution("FORCING01","checks/application/forcing01","RUN_RECORD.json","PRE_RUN.json","E_FORCING_CODE",
              "checks/application/forcing01/results/FORCING_FEEDBACK_RESULTS.json")
    execution("NEUMANN01","checks/application/neumann01","RUN_RECORD.json","PRE_RUN.json","E_NEUMANN01_CODE",
              failed_reason="Outward-copied endpoint norm exceeded inherited exact a; assertion detected missing serialization envelope.")
    execution("NEUMANN02","checks/application/neumann02","RUN_RECORD.json","PRE_RUN.json","E_NEUMANN_CODE",
              "checks/application/neumann02/results/DERIVATIVE_NEUMANN_RESULTS.json")
    execution("REVIEW01","review","INDEPENDENT_REVIEW_RUN.json","INDEPENDENT_REVIEW_PRE_RUN.json","E_REVIEW_CODE_01",
              "review/arithmetic01/INDEPENDENT_ARITHMETIC_RESULTS.json",
              "26/29 checks passed; reviewer equality assumption failed on conservative outward copies. Actual intervals were valid.")
    execution("REVIEW02","review","INDEPENDENT_REVIEW_RUN_02.json","INDEPENDENT_REVIEW_PRE_RUN_02.json","E_REVIEW_CODE_02",
              "review/arithmetic02/INDEPENDENT_ARITHMETIC_RESULTS.json")
    wl=read(ROOT,"checks/wolfram/WOLFRAM_XACT_EXECUTION.json")
    wls=read(ROOT,"checks/wolfram/SUMMARY.json")
    assert not wl["tool_result"].get("isError",False) and wls["all_exact_zero"]
    executions.append({"id":"X_WOLFRAM","status":"completed",
      "command":read(ROOT,"checks/wolfram/PRE_RUN.json")["command"],
      "environment":{"tool":wl["tool"],"Wolfram":wls["wolfram_version"],"xTensor":"1.3.0","xPerm":"1.2.4",
                     "backend":"xPerm Wolfram Language group algorithms","external_canonicalizer_used":False},
      "evidence_refs":["E_WL_PRE","E_WL_CODE","E_WL_RAW","E_WL_SUMMARY"],"exit_code":0,
      "exit_code_semantics":"Workflow success code for returned Completed evaluator result; tool did not return an OS process exit code.",
      "reason":"Actual exact symbolic execution completed; physical 35-slot inclusion is separately bound.",
      "wall_seconds":wl["wall_seconds"],"tensor_checks":6,"scalar_groups":9,"scalar_values":15})
    executions.append({"id":"X_NEXT_MIXED","status":"not_run","command":"",
      "environment":{"intended_location":"current environment after selection of next theory/application unit"},
      "evidence_refs":["E_NEXT_PROPOSAL"],"exit_code":None,
      "reason":"First mixed-response application is a selected successor, not part of this completed first-response execution."})
    def ck(cid,domain,result,refs,reason,x=None):
        checks.append({"id":cid,"domain":domain,"result":result,"evidence_refs":refs,"reason":reason,"execution_ref":x})
    ck("K_SOURCE","physics","pass_scoped",["E_SOURCE_REVIEW","E_SOURCE_IDENTITIES","E_REVIEW","E_THEOREM"],
       "Same physical source, C2 family, COMMON, threshold leaves, density and finite-temperature normalization.")
    ck("K_LITERATURE","math","pass_scoped",["E_LIT_REVIEW","E_LIT_BIB","E_LIT_SEARCH"],
       "Primary conditions checked; independent-tolerance inner claims not transferred; MB22 sufficient-condition scope corrected.")
    ck("K_MAIN01","implementation","fail",["E_MAIN01_RUN","E_MAIN01_DIAG"],"Original schema-field failure retained; resolved by MAIN02.","X_MAIN01")
    ck("K_MAIN02","numerics","pass_scoped",["E_MAIN02_RUN","E_MAIN02_RESULT","E_REVIEW"],
       "Frozen run02 includes both strict temperature derivative signs and exact P2/P4 transfer.","X_MAIN02")
    ck("K_FORCING","numerics","pass_scoped",["E_FORCING01_RUN","E_FORCING01_RESULT","E_REVIEW"],
       "Same-JF explicit/feedback decomposition; 245 photon intersections per parameter and 4 RHS intersections each.","X_FORCING01")
    ck("K_NEUMANN01","numerics","fail",["E_NEUMANN01_RUN","E_NEUMANN01_DIAG"],
       "Missing import envelope detected before result; corrected by conservative max in NEUMANN02.","X_NEUMANN01")
    ck("K_NEUMANN02","numerics","pass_scoped",["E_NEUMANN02_RUN","E_NEUMANN02_RESULT","E_REVIEW"],
       "Actual finite Neumann bounds with Jacobian-difference coefficient 1 and conservative imported a.","X_NEUMANN02")
    ck("K_REVIEW01","implementation","fail",["E_REVIEW01_RUN","E_REVIEW01_RESULT","E_REVIEW"],
       "26/29: equality versus outward-copy inclusion was an incorrect reviewer invariant; source and logs retained.","X_REVIEW01")
    ck("K_REVIEW02","numerics","pass_scoped",["E_REVIEW02_RUN","E_REVIEW02_RESULT","E_REVIEW_CODE_02","E_REVIEW"],
       "29/29 final exact Fraction checks; independent determinant/Cramer inverse; candidate and PHYS14 helper imports zero.","X_REVIEW02")
    ck("K_WOLFRAM","math","pass_scoped",["E_WL_RAW","E_WL_SUMMARY","E_WL_CODE","E_SOURCE_REVIEW"],
       "Actual 6 tensor and 15 scalar exact-zero checks; mathematical identities distinguished from physical inclusion.","X_WOLFRAM")
    ck("K_COROLLARIES","math","pass_scoped",["E_THEOREM","E_COROLLARIES","E_REVIEW02_RESULT"],
       "Same-alpha monotonicity, FTC finite changes, local level-curve and continuation, four-corner prior checked.","X_REVIEW02")
    ck("K_NEXT_MIXED","math","not_run",["E_NEXT_PROPOSAL"],
       "Next C2 mixed-response construction and actual evaluator remain a successor unit.","X_NEXT_MIXED")
    optional=[
      ("NEXT_DAG","next/NEXT_DAG.json","resource","Next research DAG: mixed response selected, no heavy launch"),
      ("NEXT_DAG_ROOT","NEXT_DAG.json","resource","Next research DAG: mixed response selected, no heavy launch"),
      ("NEXT_CONTRACT","contracts/MIXED_RESPONSE_CONTRACT.json","resource","Successor mixed-response contract, actual application not_run"),
      ("README","README.md","artifact","Current formal result and reproducibility entry point"),
      ("README_KO","README_KO.md","artifact","Korean current result entry point"),
      ("HANDOFF","HANDOFF.md","artifact","Current restart and successor handoff"),
      ("HANDOFF_KO","HANDOFF_KO.md","artifact","Current restart and successor handoff"),
      ("DEPENDENCIES","DEPENDENCIES.json","resource","Declared dependency and artifact bindings"),
    ]
    optional_refs=[]
    for label,rel,kind,scope in optional:
        if (ROOT/rel).is_file():optional_refs.append(artifact(label,ROOT,rel,kind,scope))
    scope_text="Same fixed admissible alpha and COMMON; global lambda,b in [0,1]^2; inherited source-aligned geometric-isotropic C2 family; first derivatives of d=g2-gF and finite DeltaT=T2-TF."
    claim_refs=[
      ["E_THEOREM","E_FORMULA_REVIEW","E_INPUT_FULL_SOURCE","E_INPUT_EXPORT_MAPPING","E_MAIN02_RESULT","E_REVIEW"],
      ["E_THEOREM","E_INPUT_FIRST_FULL_UV","E_INPUT_SECOND_HALF_UV","E_MAIN02_RESULT","E_SOURCE_REVIEW","E_REVIEW"],
      ["E_THEOREM","E_SOURCE_IDENTITIES","E_SOURCE_REVIEW","E_WL_RAW","E_MAIN02_RESULT","E_REVIEW"],
      ["E_THEOREM","E_INPUT_FULL_COMPONENTS","E_INPUT_HALF_COMPONENTS","E_SOURCE_REVIEW","E_MAIN02_RESULT","E_REVIEW"],
      ["E_THEOREM","E_INPUT_PHOTON_CARRY","E_MAIN02_RESULT","E_FORCING01_RESULT","E_WL_RAW","E_REVIEW"],
      ["E_THEOREM","E_INPUT_PRECONDITIONER","E_INPUT_PHYS16_REMAINDER","E_NEUMANN02_RESULT","E_REVIEW02_RESULT","E_REVIEW"],
      ["E_THEOREM","E_MAIN02_RESULT","E_FORCING01_RESULT","E_WL_RAW","E_SOURCE_REVIEW","E_REVIEW"],
      ["E_THEOREM","E_COROLLARIES","E_MAIN02_RESULT","E_REVIEW02_RESULT","E_REVIEW"],
    ]
    claims=[]
    for i,c in enumerate(theory["claims"]):
        row={"id":c["id"],"statement":c["title"],"scope":scope_text,
             "basis":["derived","numerically checked","implementation-verified"],
             "evidence_refs":[*claim_refs[i],"E_DECISION"],"obligations":[],
             "equation_locator":c["locator"],"decision":"PROMOTE_SCOPED"}
        if c["id"]=="P17-T5":
            row["subclaim_scope"]="Seven-sector actual derivative evaluated; additional photon ledger and endpoint readout formulae in section 6.2 derived, not all numerically evaluated."
        claims.append(row)
    def stage(n,status,refs,reason):
        ids=sorted({d for e in refs for d in ev_index[e]["dependency_ids"]})
        return {"id":"R"+str(n),"status":status,"evidence_refs":refs,"dependency_ids":ids,"reason":reason,
                "reuse":{"dependency_identities":{d:dep_index[d]["identity"] for d in ids},
                         "reason":"Same frozen source/family and P1-P4 contract; actual input hashes unchanged."}
                        if status=="reused" else None}
    stages=[
      stage(1,"reused",["E_CONTRACT","E_ENTRY","E_PARENT_DECISION","E_PARENT_REMOTE"],"Inherited PHYS16 successor scope and user-authorized theory loop; 14 original bindings match."),
      stage(2,"complete",["E_ENTRY","E_LIT_REVIEW","E_LIT_BIB","E_LIT_SEARCH","E_SOURCE_IDENTITIES"],"Read original source and primary literature; preserve prior valid source/root/adjoint evidence."),
      stage(3,"complete",["E_CLAIMS","E_THEOREM","E_SOURCE_REVIEW","E_CONTRACT"],"Eight scientific claims quantified on the fixed same-COMMON C2 family with units and derivative slots."),
      stage(4,"complete",["E_FORMULA_REVIEW","E_THEOREM","E_MAIN_CODE","E_FORCING_CODE"],"Selected direct implicit differentiation, correlated stage increment, isothermal He projector and seven-sector response."),
      stage(5,"complete",["E_THEOREM","E_COROLLARIES","E_MAIN_CODE","E_FORCING_CODE","E_NEUMANN_CODE"],"Seven completed constructive theorems and corollary close all current first-response obligations."),
      stage(6,"complete",["E_REVIEW","E_SOURCE_REVIEW","E_REVIEW01_RESULT","E_REVIEW02_RESULT","E_WL_RAW","E_WL_SUMMARY"],"Independent source/formula and exact Cramer review complete, 29/29 final checks, first comparator correction retained."),
      stage(7,"complete",["E_MAIN01_DIAG","E_MAIN02_RUN","E_MAIN02_RESULT","E_FORCING01_RUN","E_FORCING01_RESULT","E_NEUMANN01_DIAG","E_NEUMANN02_RUN","E_NEUMANN02_RESULT","E_WL_RAW"],"Actual stored-enclosure discrimination completed; strict response signs, forcing/feedback and finite Neumann bounds obtained."),
      stage(8,"complete",["E_REVIEW","E_DECISION"],"Independent PROMOTE_SCOPED followed by root detached adoption; no blocking science finding or new strong no-go."),
      stage(9,"complete",["E_THEOREM","E_CLAIMS","E_COROLLARIES","E_NEXT_PROPOSAL",*optional_refs],"Formal equations, implementation/result bindings and mixed-response successor contract available; successor application not_run."),
      stage(10,"in_progress",["E_DECISION","E_NEXT_PROPOSAL",*optional_refs],"Final PDF QA, Git publication and current PHYS17 provider backup acknowledgements are to be attached by root before overall completion."),
    ]
    state.update({"scope":scope_text,"family_scope":family,"status":"in_progress",
      "updated_utc":stamp,"scientific_status":"PROMOTE_SCOPED","dependencies":deps,"evidence":evidence,
      "stages":stages,"claims":claims,"checks":checks,"executions":executions,
      "decisions":[{"id":"ADOPT_PHYS17","decision":"PROMOTE_SCOPED","adopter":"/root","evidence_refs":["E_DECISION","E_REVIEW"],
                    "reason":"Root adopted fixed first-response science following independent 29/29 review; execution and original candidate status preserved."}],
      "overrides":[],
      "failures":[
        {"id":"F_MAIN01","class":"implementation","execution_ref":"X_MAIN01","evidence_refs":["E_MAIN01_RUN","E_MAIN01_DIAG","E_MAIN01_CODE","E_MAIN02_RUN"],
         "observed":"PHYS11 outgoing field mapping KeyError; no candidate result emitted.","status":"resolved","next_action":"Completed: use preserved outgoing_joint field and run02."},
        {"id":"F_NEUMANN01","class":"numerics","execution_ref":"X_NEUMANN01","evidence_refs":["E_NEUMANN01_RUN","E_NEUMANN01_DIAG","E_NEUMANN01_CODE","E_NEUMANN02_RUN"],
         "observed":"Exact inherited a did not cover the outward-copied d/S norm before envelope correction.","status":"resolved","next_action":"Completed: max(inherited a, actual copied enclosure norm), with both values recorded in neumann02."},
        {"id":"F_REVIEW01","class":"implementation","execution_ref":"X_REVIEW01","evidence_refs":["E_REVIEW01_RUN","E_REVIEW01_RESULT","E_REVIEW_CODE_01","E_REVIEW_CODE_02","E_REVIEW02_RESULT","E_REVIEW"],
         "observed":"26/29 reviewer checks: exact equality incorrectly required for long rational versus outward-copied enclosures.","status":"resolved","next_action":"Completed: conservative inclusion and relative import-expansion check; arithmetic02 29/29 PASS; original science unchanged."}],
      "next_actions":[
        {"id":"CLOSEOUT_PDF","stage":"R10","status":"pending_root_evidence","action":"Attach final compiled PDF identity and actually completed render/QA record."},
        {"id":"CLOSEOUT_GIT","stage":"R10","status":"pending_root_evidence","action":"Attach actual Git commit/tree and draft PR or publication acknowledgement."},
        {"id":"CLOSEOUT_BACKUP","stage":"R10","status":"pending_root_evidence","action":"Attach actual current PHYS17 Dropbox/Google Drive acknowledgement; preserve parent receipts as parent-only evidence."},
        {"id":"NEXT_MIXED","stage":"successor","status":"not_run","node":"HH_DEFECT_MIXED_RESPONSE","evidence_refs":["E_NEXT_PROPOSAL",*([e for e in optional_refs if e=="E_NEXT_CONTRACT"])],
         "action":"Use original C2 W/Hessian data and proposed mixed forcing construction in the next authorized unit."}],
      "heavy_queue":[],"launch":False,"strong_no_go_claims":0,"global_nodes_newly_completed":[],
      "next_research_node":"HH_DEFECT_MIXED_RESPONSE","mixed_response_actual_application":"not_run",
      "new_source_calls":0,"new_root_solves":0,"history_replays":0,
      "native_authority_promoted":False,"continuous_exact_solution_error_claimed":False,
      "workflow_structure_check":{"record_path":"state/STRUCTURE_CHECK_01.json","status_managed_outside_state":True,
                                  "command":"python3 evidence/workflow_1_0_0/scripts/run_record.py check state/RESEARCH_STATE.json",
                                  "scope":"structure_and_references; scientific validity assessed by the separately linked review/decision"},
      "record_migration":{"preserved_before":"state/RESEARCH_STATE_BEFORE_COMPLETION_UPDATE.json",
                          "change":"scope object preserved verbatim as family_scope; scope is a descriptive string required by workflow 1.0.0.",
                          "scientific_claim_or_candidate_mutation":False},
      "execution_counts":{"successful_application_executions":3,"failed_initial_application_executions":2,
                          "independent_review_program_executions":2,"independent_review_final_checks":29,
                          "wolfram_xact_executions":1,"wolfram_tensor_checks":6,"wolfram_scalar_groups":9,"wolfram_scalar_values":15},
      "literature_counts":review["literature_counts"]})
    (STATE/"RESEARCH_STATE.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
    audit={"schema":"WU088_HH_PHYS17_STATE_ASSEMBLY_V1","created_utc":stamp,
      "scope":"Metadata assembly and file identity checks only; no scientific reexecution",
      "contract_inputs_verified":14,"scientific_claim_count":len(claims),
      "dependency_count":len(deps),"evidence_count":len(evidence),"execution_records":len(executions),
      "optional_existing_artifacts":optional_refs,"state_identity":ident(ROOT,"state/RESEARCH_STATE.json"),
      "source_identity":ident(ROOT,"state/assemble_research_state.py"),
      "root_decision_identity":ident(ROOT,"review/DECISION.json"),
      "unchanged_independent_review_identity":ident(ROOT,"review/INDEPENDENT_REVIEW.json")}
    (STATE/"STATE_ASSEMBLY_RECORD.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(audit,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
