#!/usr/bin/env python3
"""Generate a byte-bound HALF_MINUS launcher from proven MINUS one-shot code.

No science Popen, no private binding disclosure, no state/solver mutation.
The one-shot reservation and release require separate fresh runtime checks.
"""
from pathlib import Path
import hashlib
import json
import os

ROOT=Path.home()/"Dropbox/bianchi/rei_bianchi"
W=Path.home()/"rei_worktrees/ax08_halfminus_loop_20261015"
OLD=ROOT/"research/axbi_goal_20261014/driver/full/minus_continuation_001/launch_001"
NEW=W/"research/axbi_goal_20261014/driver/full/half_minus_continuation_001/launch_001"
H=ROOT/"research/axbi_goal_20261014/driver/full/half_minus_continuation_001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jsonread(p):return json.loads(p.read_text())
def save(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
source_review=ROOT/"research/axbi_goal_20261014/driver/full/signed_minus_bindings_review_001/INDEPENDENT_REVIEW.json"
upstream_review=jsonread(source_review)
assert upstream_review["decision"]=="PASS_SCOPED_EXACT_BINDINGS_CONDITIONAL_LAUNCH"
assert upstream_review["cases"]["SHEAR_HALF_MINUS"]=="PASS"
assert sha(H/"AUTHORITY.json")==upstream_review["reviewed_sha256"]["SHEAR_HALF_MINUS"]["AUTHORITY.json"]
for key,fn in (("EXECUTION.binding","EXECUTION.binding"),("EXECUTION_AUTHORITY.binding","EXECUTION_AUTHORITY.binding"),
               ("starting_state_debug.txt","starting_state_debug.txt"),("PREPARATION_RECEIPT.json","PREPARATION_RECEIPT.json")):
 assert sha(H/fn)==upstream_review["reviewed_sha256"]["SHEAR_HALF_MINUS"][key]
prep=jsonread(H/"PREPARATION_RECEIPT.json")
assert prep["status"]=="PREPARED_PENDING_INDEPENDENT_BINDING_REVIEW"
assert prep["execution_binding_sha256"]==sha(H/"EXECUTION.binding")
old=jsonread(OLD/"LAUNCH_CONTRACT.json")
c=json.loads(json.dumps(old))
def adapt(obj):
 if isinstance(obj,str):
  return obj.replace("SHEAR_MINUS","SHEAR_HALF_MINUS").replace("minus_continuation_001","half_minus_continuation_001")
 if isinstance(obj,list):return [adapt(x) for x in obj]
 if isinstance(obj,dict):return {k:adapt(v) for k,v in obj.items()}
 return obj
c=adapt(c)
c["schema"]="rei.axbi.shear_half_minus_serialized_launcher_contract.v1"
c["decision"]="EXISTING_ONE_START_SCIENCE_BINDING_PASS; PREPARE_AND_SEPARATELY_RELEASE_AFTER_FRESH_RUNTIME_REVIEW"
c["launch_now"]=False
c["existing_authority"].update({
 "path":str((H/"AUTHORITY.json").relative_to(ROOT)),"sha256":sha(H/"AUTHORITY.json"),
 "independent_binding_review":str(source_review.relative_to(ROOT)),
 "independent_review_sha256":sha(source_review),
 "review_decision":"PASS_SCOPED_EXACT_BINDINGS_CONDITIONAL_LAUNCH",
 "science_allocation_increase":0,
 "rule":"Reuses already reviewed SHEAR_HALF_MINUS single start, with no binary/physics/source change; current new launcher needs mechanical review and a fresh owner release.",
})
c["binding"].update({
 "path":str((H/"EXECUTION.binding").relative_to(ROOT)),
 "sha256":sha(H/"EXECUTION.binding"),
 "private_authority_binding_sha256":sha(H/"EXECUTION_AUTHORITY.binding"),
 "binary":prep["binary_path"],"binary_sha256":prep["binary_sha256"],
 "compiled_library_identity_sha256":"4de69c1e68ebd395fe2d0b5580d901b9a82bde86cadbd11bdd07e5ad2042b4a1"
})
c["launcher_preparation"]["owned_root"]=str(NEW.relative_to(W))
c["launcher_preparation"]["reuse_reference"]="Real tested MINUS one-start launch_001/launcher.py, adapted only for HALF_MINUS exact frozen bindings and previous MINUS terminal."
c["serialized_release_preconditions"]=[
 "PLUS typed observer false-positive incident independently classified; no false complete claim.",
 "SHEAR_HALF_PLUS actual terminal exit0 and composed312238 rows.",
 "SHEAR_MINUS actual terminal exit0, source-reviewed resource-only composer completed312238 rows, unique accepted312237; preserve exact RETURN SHA.",
 "Historical PLUS, HALF_PLUS and MINUS owner/science processes absent, no conflicting reserved future owner.",
 "Read all existing HALF_MINUS frozen authority/private mirror, original checkpoint/config/RETURN/source and science binary exact SHA versus archived independent review and PREPARATION_RECEIPT.",
 "One fresh local and actual NCP remote observation and pending/owner arbitration; >=4 GiB disk, >=2 GiB MemAvailable, allowed CPU0.",
 "New launcher source and contract mechanically checked, after release only one Popen and no automatic retry; fresh launch/terminal receipts."
]
c["execution"]["outer_argv"]=[adapt(x) for x in old["execution"]["outer_argv"]]
c["execution"]["outer_argv"][-1]=c["binding"]["sha256"]
caps=jsonread(H/"AUTHORITY.json")["allocation"]["binding_fields"]
c["execution"]["effective_trajectory_caps"]={
 "accepted":caps["effective_max_steps"],"tentative":caps["effective_max_attempts"],
 "rhs":caps["effective_max_rhs"],"solver_wall_s":caps["effective_max_wall_s"],
 "output_budget_mib":caps["effective_output_budget_mib"]}
c["execution"]["remaining_from_original_checkpoint"]["solver_wall_s"]=10800
c["execution"]["output"]=adapt(old["execution"]["output"])
c["execution"]["raw_output"]=adapt(old["execution"]["raw_output"])
c["cumulative_start_accounting"]={
 "verified_after_minus":{"original_cases":5,"ZERO_continuation_starts":1,
    "PLUS_reserved_attempts":2,"PLUS_observed_continuation_starts":1,
    "HALF_PLUS_continuation_starts":1,"MINUS_continuation_starts":1,
    "full_observed_starts":9,"history_observed_starts":12},
 "projected_after_half_minus":{"HALF_MINUS_continuation_starts":1,
    "full_observed_starts":10,"history_observed_starts":13},
 "rule":"Only conditional on actual current scheduling reconciliation; no additional wall allocation or retry."}
c["transition"]="HALF_PLUS and MINUS naturally terminal classified + original PLUS false-positive abort typed -> actual fresh controller release -> one HALF_MINUS science Popen; natural terminal must be composed separately."
save(NEW/"LAUNCH_CONTRACT.json",c)
assert c["case"]=="SHEAR_HALF_MINUS" and c["segment"]=="SHEAR_HALF_MINUS_RESOURCE_CONTINUATION_001"
assert c["execution"]["outer_argv"][-1]==sha(H/"EXECUTION.binding")
assert c["existing_authority"]["independent_review_sha256"]==sha(source_review)
# Make the already-tested process/resource controller use the exact HALF_MINUS identities.
l=(OLD/"launcher.py").read_text()
l=l.replace("SHEAR_MINUS","SHEAR_HALF_MINUS").replace("minus_continuation_001","half_minus_continuation_001")
l=l.replace('ROOT = Path(__file__).resolve().parents[6]',
            'ROOT = Path(os.environ.get("AX08_CANONICAL_ROOT", str(Path(__file__).resolve().parents[6])))')
l=l.replace('HALF_COMPOSED = AX / "runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002"',
'''HALF_COMPOSED = AX / "runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002"
MINUS_LAUNCH = AX / "driver/full/minus_continuation_001/launch_001"
MINUS_RETURN = AX / "runs/paired/32d11e733155/SHEAR_MINUS_continuation_001/RETURN.txt"
MINUS_COMPOSED = AX / "runs/paired/32d11e733155/SHEAR_MINUS_composed_001"''')
insert='''def classify_minus() -> dict:
    terminal=load(MINUS_LAUNCH/"TERMINAL_RECEIPT.json")
    ret=dict(line.split("=",1) for line in MINUS_RETURN.read_text().splitlines() if "=" in line)
    comp=load(MINUS_COMPOSED/"COMPOSITION_RECEIPT.json")
    if terminal.get("exit_code")!=0 or terminal.get("stop_reason") is not None or terminal.get("return_present") is not True:
        raise RuntimeError("PRIOR_MINUS_SOLVER_NOT_NATURALLY_TERMINAL")
    if not (ret.get("status")=="COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT" and ret.get("result")=="Ok(())"
            and float(ret.get("a","nan"))==.2 and int(ret.get("accepted",-1))==312237):
        raise RuntimeError("PRIOR_MINUS_SCIENTIFIC_RETURN_NOT_COMPLETE")
    if (comp.get("status")!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
         or comp.get("scientific_admission")!="NOT_ISSUED"
         or comp.get("row_counts",{}).get("history.csv",{}).get("composed_rows")!=312238
         or comp.get("source_compatibility",{}).get("relation")!="REVIEWED_RESOURCE_ONLY"):
        raise RuntimeError("PRIOR_MINUS_COMPLETED_HISTORY_NOT_REVIEWED")
    if comp.get("input_sha256",{}).get(str(MINUS_RETURN.relative_to(ROOT))) != hash_file(MINUS_RETURN):
        raise RuntimeError("PRIOR_MINUS_RETURN_BYTES_CHANGED")
    return {"terminal_sha256":hash_file(MINUS_RETURN),"terminal_exit":0,
        "accepted":312237,"a":.2,"composition_receipt_sha256":hash_file(MINUS_COMPOSED/"COMPOSITION_RECEIPT.json"),
        "scoped_composition":"REVIEWED_RESOURCE_ONLY","composed_rows":312238}

'''
assert "def preflight() -> dict:" in l
l=l.replace("def preflight() -> dict:",insert+"def preflight() -> dict:")
l=l.replace('str(BASE.relative_to(ROOT)/"EXECUTION_AUTHORITY.binding")',
            'str(Path(c["binding"]["path"]).parent/"EXECUTION_AUTHORITY.binding")')
l=l.replace('prep=load(BASE/"PREPARATION_RECEIPT.json")',
            'prep=load(ROOT/Path(c["binding"]["path"]).parent/"PREPARATION_RECEIPT.json")')
l=l.replace("    half=classify_half_plus()",'''    half=classify_half_plus()
    minus=classify_minus()
    # This original frozen independent binding review covered BOTH minus cases.
    prep=load(BASE/"PREPARATION_RECEIPT.json")
    if prep.get("status")!="PREPARED_PENDING_INDEPENDENT_BINDING_REVIEW" or prep.get("execution_binding_sha256")!=c["binding"]["sha256"]:
        raise RuntimeError("FROZEN_HALF_MINUS_PREPARATION_CHANGED")
    for rel,digest in prep["input_sha256"].items():
        if hash_file(ROOT/rel)!=digest:
            raise RuntimeError("HALF_MINUS_ORIGINAL_INPUT_CHANGED:"+rel)''')
l=l.replace('"half_plus_classification":half,"active_science_count":len(active)',
            '"half_plus_classification":half,"minus_classification":minus,"active_science_count":len(active)')
l=l.replace('if rel.get("half_plus_terminal_sha256")!=check["half_plus_classification"]["terminal_sha256"]:',
'''if rel.get("minus_terminal_sha256")!=check["minus_classification"]["terminal_sha256"]:
        raise RuntimeError("PRIOR_MINUS_TERMINAL_BINDING_CHANGED")
    if rel.get("half_plus_terminal_sha256")!=check["half_plus_classification"]["terminal_sha256"]:''')
start=l.index('    after={"original_starts":5,')
end=l.index('    safe_json(OWN/"RESERVATION.json"',start)
l=l[:start]+'''    after={"original_starts":5,"zero_continuation":1,"plus_attempted":2,
           "plus_observed":1,"half_plus_observed":1,"minus_observed":1,
           "half_minus_observed":1,"full_observed_starts":10,"history_observed_starts":13}
'''+l[end:]
# There is no adaptive resource escalation nor second solver Popen.
assert l.count("subprocess.Popen(")==1 and 'def classify_minus()' in l
(NEW/"launcher.py").write_text(l)
controller=(OLD/"controller_release.py").read_text()
controller=controller.replace('ROOT=Path(__file__).resolve().parents[6]',
    'ROOT=Path(os.environ.get("AX08_CANONICAL_ROOT",str(Path(__file__).resolve().parents[6])))')
controller=controller.replace("SHEAR_MINUS","SHEAR_HALF_MINUS").replace("minus_continuation_001","half_minus_continuation_001")
controller=controller.replace('"schema":"rei.axbi.shear_minus_controller_release.v1"',
                             '"schema":"rei.axbi.shear_half_minus_controller_release.v1"')
controller=controller.replace('"half_plus_terminal_sha256":pre["half_plus_classification"]["terminal_sha256"],',
''' "half_plus_terminal_sha256":pre["half_plus_classification"]["terminal_sha256"],
       "minus_terminal_sha256":pre["minus_classification"]["terminal_sha256"],''')
controller=controller.replace("    unix=time.time()",'''    # A previous local science reservation counts as pending unless it has its own
    # typed terminal receipt. This avoids silently reusing a scheduler slot.
    old_reservations=list((ROOT/"research/axbi_goal_20261014/driver/full").rglob("RESERVATION.json"))
    pending=[]
    for reservation in old_reservations:
        if reservation.parent==OWN:
            continue
        terminal=reservation.parent/"TERMINAL_RECEIPT.json"
        if not terminal.is_file():
            pending.append(str(reservation.relative_to(ROOT)))
    if pending:
        raise RuntimeError("UNRESOLVED_PREEXISTING_SCIENCE_RESERVATION:"+str(pending))
    unix=time.time()''')
assert 'minus_terminal_sha256' in controller
(NEW/"controller_release.py").write_text(controller)
tests=(OLD/"test_launcher.py").read_text()
tests=tests.replace("SHEAR_MINUS","SHEAR_HALF_MINUS").replace("ax08-minus","ax08-half-minus")
tests=tests.replace('self.assertEqual(result["half_plus_classification"]["last_accepted"],312237)',
'''self.assertEqual(result["half_plus_classification"]["last_accepted"],312237)
        self.assertEqual(result["minus_classification"]["accepted"],312237)
        self.assertEqual(result["minus_classification"]["composed_rows"],312238)''')
(NEW/"test_launcher.py").write_text(tests)
review=(OLD/"review_launcher_independent_checks.py").read_text()
review=review.replace('ROOT=Path(__file__).resolve().parents[6]',
   'ROOT=Path(__import__("os").environ.get("AX08_CANONICAL_ROOT",str(Path(__file__).resolve().parents[6])))')
review=review.replace("SHEAR_MINUS","SHEAR_HALF_MINUS").replace("minus_continuation_001","half_minus_continuation_001")
review=review.replace('"classify_half_plus","process_record"', '"classify_half_plus","classify_minus","process_record"')
review=review.replace('"half_plus_terminal_sha256",', '"half_plus_terminal_sha256","minus_terminal_sha256",')
review=review.replace('"prerequisite_half_plus_completed_rows":312238,','"prerequisite_half_plus_completed_rows":312238,"prerequisite_minus_completed_rows":312238,')
review=review.replace('    report={','''    terminal=load(ROOT/"research/axbi_goal_20261014/driver/full/minus_continuation_001/launch_001/TERMINAL_RECEIPT.json")
    require(terminal.get("exit_code")==0 and terminal.get("stop_reason") is None,"PRIOR_MINUS_TERMINAL_NOT_NATURAL")
    comp=load(ROOT/"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001/COMPOSITION_RECEIPT.json")
    require(comp["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION" and comp["row_counts"]["history.csv"]["composed_rows"]==312238,
            "PRIOR_MINUS_COMPLETE_COMPOSITION_MISSING")
    report={''')
(NEW/"review_launcher_independent_checks.py").write_text(review)
print("GENERATION_OK")
for path in ("LAUNCH_CONTRACT.json","launcher.py","controller_release.py","test_launcher.py","review_launcher_independent_checks.py"):
 print(path,sha(NEW/path),(NEW/path).stat().st_size)
