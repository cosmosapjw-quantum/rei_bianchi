"""Runtime recovery of the prescribed four-node mechanical central delta.

No science or original assembler is executed. Source publication must be bound
to observed root verification before the candidate may be published.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDS = {"HE-EXCHANGE","HE-EXP-PAIR","HE-CLOSURE","HE-EXP-CLOSURE"}
STATUS = "status/HE_EXP_FINITE_DRIFT_20261027.json"
SCRIPT = "assembly/apply_he_finite_drift_observation.py"
PREFIX = "research/orchestration_expansion_20261025/"


def load(path):
    return json.loads(path.read_text())


def formatted(value):
    return json.dumps(value,ensure_ascii=False,indent=2)+"\n"


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(formatted(value))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def prepare(observation_path):
    base,result=ROOT/"base",ROOT/"result"
    meta=load(ROOT/"BASE_METADATA.json")
    assert blob(base/"DAG.json")==meta["dag_blob"]
    assert blob(base/"AGENTS.md")==meta["agents_blob"]
    for name,value in meta["files"].items():
        assert blob(base/name)==value["blob"],name
    before=load(base/"DAG.json")
    after=copy.deepcopy(before)
    o=copy.deepcopy(load(observation_path))
    source=o["source_intake"]["source_commit"]
    assert re.fullmatch("[0-9a-f]{40}",source)
    assert o["unit_id"]=="HE-EXP-DRIFT-02"
    assert set(o["observations"])==IDS
    assert o["source_intake"]["repository"]=="cosmosapjw-quantum/BASS_HE"
    old={n["id"]:n for n in before["nodes"]}
    new={n["id"]:n for n in after["nodes"]}
    assert len(old)==len(before["nodes"])==88
    assert "previous_observations" not in o
    o["previous_observations"]={i:copy.deepcopy(old[i]["status_observation"]) for i in sorted(IDS)}
    for i in sorted(IDS):
        v=o["observations"][i]
        assert v["source_commit"]==source and v["source_repository"]=="cosmosapjw-quantum/BASS_HE"
        assert v["physical_provider_admitted"] is False and v["activation"] is False
        assert v["production_status"]=="NOT_APPROVED" and v["physical_allocation"]=="UNALLOCATED"
        assert v["current_scoped_state"]==old[i]["current_status"]
        new[i]["status_observation"]={"source_file":STATUS,"json_pointer":"/observations/"+i,"value":copy.deepcopy(v)}
    write(result/STATUS,o)
    template=(ROOT/"reapply_template.py").read_text()
    structure={i:{k:v for k,v in old[i].items() if k not in {"current_status","status_observation"}} for i in IDS}
    for key,value in {
        "__OBSERVATION_SHA256__":sha(result/STATUS),"__TARGETS_SHA256__":fingerprint(structure),
        "__NODE_IDS_SHA256__":fingerprint([n["id"] for n in before["nodes"]]),
        "__TOP_SHA256__":fingerprint({k:v for k,v in before.items() if k!="nodes"}),
    }.items():template=template.replace(key,value)
    target=result/SCRIPT
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(template)
    spec=importlib.util.spec_from_file_location("bounded_reapply",target)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    write(result/"DAG.json",after)
    rows=load(base/"status/CURRENT_STATUS.json")
    write(result/"status/CURRENT_STATUS.json",module.status_rows(after,rows))
    for i in sorted(IDS):
        write(result/"contracts"/(i+".json"),new[i])
        p=result/"node_plans"/(i+".md")
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(module.plan(new[i]))
    assert before.keys()==after.keys()
    assert {k:v for k,v in before.items() if k!="nodes"}=={k:v for k,v in after.items() if k!="nodes"}
    assert [n["id"] for n in before["nodes"]]==[n["id"] for n in after["nodes"]]
    assert {i for i in old if old[i]!=new[i]}==IDS
    for i in IDS:
        assert {k for k in old[i].keys()|new[i].keys() if old[i].get(k)!=new[i].get(k)}=={"status_observation"}
        assert o["previous_observations"][i]==old[i]["status_observation"]
    status=load(result/"status/CURRENT_STATUS.json")
    assert {a["id"] for a,b in zip(rows,status) if a!=b}==IDS
    assert sum(a==b for a,b in zip(rows,status))==84
    assert after["global_physical_completion"] is None and after["L4_ready"] is False
    expected={"DAG.json",STATUS,"status/CURRENT_STATUS.json",SCRIPT}|{f"{d}/{i}{s}" for i in IDS for d,s in (("contracts",".json"),("node_plans",".md"))}
    actual={str(p.relative_to(result)) for p in result.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert actual==expected
    with tempfile.TemporaryDirectory(prefix="reapply_recovery_",dir=ROOT) as tmp:
        t=Path(tmp)
        write(t/"DAG.json",before)
        write(t/"status/CURRENT_STATUS.json",rows)
        write(t/STATUS,o)
        module.apply(t)
        assert all((t/n).read_bytes()==(result/n).read_bytes() for n in expected if n!=SCRIPT)
    write(ROOT/"REAPPLY_VALIDATION.json",{"status":"PASS","runtime_recovery":True,"data_outputs_compared":11,"unchanged_current_status_rows":84,"scientific_execution":False,"publication_performed":False})
    write(ROOT/"tree_elements.json",[{"path":PREFIX+n,"mode":"100644","type":"blob","content":(result/n).read_text()} for n in sorted(expected)])
    write(ROOT/"DELTA_VALIDATION.json",{
        "status":"PASS","scope":"mechanical_delta_only","runtime_recovery":True,
        "base_head":meta["base_head"],"base_dag_blob":meta["dag_blob"],"nodes":88,
        "changed_nodes":sorted(IDS),"changed_fields":["status_observation"],"unchanged_nodes":84,"unchanged_current_status_rows":84,
        "all_other_fields_claim_gates_budgets_readiness_dependencies_owners_unchanged":True,
        "prior_observations_preserved_verbatim":True,"historical_assembler_prior_reapply_charter_task_assignment_unchanged":True,
        "HE_RESERVOIR_HE101_EXPORT_WU_species_unchanged":True,
        "global_physical_completion":None,"L4_ready":False,
        "scientific_tests_or_assembler_run":False,"publication_performed":False,
        "source_commit":source,"source_publication_status":o["source_intake"]["source_publication_status"],
        "source_published":o["source_intake"]["source_published"],
        "historical_mechanical_failure":"MECHANICAL_VALIDATION_FIRST_ATTEMPT.json",
        "payload_files":len(expected),"file_sha256":{n:sha(result/n) for n in sorted(expected)},
    })
    shutil.rmtree(result/"assembly/__pycache__",ignore_errors=True)
    print(json.dumps({"status":"PASS","runtime_recovery":True,"payload_files":12,"unchanged_current_status_rows":84,"source_published":o["source_intake"]["source_published"]}))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observation",type=Path)
    prepare(parser.parse_args().observation)
