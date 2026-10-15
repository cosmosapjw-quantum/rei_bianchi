#!/usr/bin/env python3
"""Build faithful C16B v3 offline source replay from frozen PR149 v2."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,zipfile
H=Path.home()
ORIG=H/"Dropbox/bianchi/rei_bianchi/research/REI_C16_CASEA_SOURCE_BACKUPS/REI_C16_CASEA_ESCAPE_20261015_4f55234d_v2.zip"
R=H/"rei_worktrees/rei_c16_escape_20261015"
W=H/"chat_research/WU088_HH"
OUT=Path(__file__).resolve().parent
NAME="REI_C16_CASEA_ESCAPE_20261015_4f55234d"
ZIP_ROOT="REI_C16_CASEA_ESCAPE_20261015"
REI="4f55234dee39e538de929b119c865dfcdbb5c673"
WU="4b36f178d5effa2ccf960d5285372f2f51d21327"
C="research/r31ao_unequal_ladder/hh_phys19_parameter_curvature_theory_20261013_v1/contracts/NEXT_CONSUMER_CONTRACT.json"
PIN={
"rust/rei_microphysics/src/coverage.rs":"0c542eaf42cd8ece217a2f02cc7fbb500f0bea8b983c1f18d44c96d0aea050c1",
"rust/rei_microphysics/src/axbi_sources.rs":"606e3c2ec367dd9951ebbf2f53486f2232b49c0218896d66d8dc13dd5ee83bfe",
"rust/rei_microphysics/src/ft03_controlled.rs":"61e11471482bb49d99e5d0eb79504d3f67538fbe6361653a0462d1abb0b672db",
"research/rei_crossrepo_integration_20261015/suppliers/wu/phys44_rei_guard.py":"590cc733ecbc30431e8b5cdd9128f10aadf044b6ff3b5af7cfcc01885ccd3838",
"offline_wu/"+C:"001e65e0fcd64c0f167c5eea78a856d3127da3c453da29946b40ba77d9040be5"}
sha=lambda b:hashlib.sha256(b).hexdigest()
runner=r'''#!/usr/bin/env python3
"""Cold v3 source-only replay; original WU HH guard is unchanged and fail-closed."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time
root=Path(__file__).resolve().parent
meta=json.loads((root/"V3_MANIFEST.json").read_text())
digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
for rel,record in meta["payload_sha256"].items():
    assert digest(root/rel)==record["sha256"],"payload mismatch: "+rel
for rel,h in meta["pinned_source_sha256"].items():
    assert digest(root/rel)==h,"pinned source mismatch: "+rel
def init_git(path):
    if not (path/".git").exists():
        subprocess.run(["git","init","-q"],cwd=path,check=True)
        subprocess.run(["git","add","-A"],cwd=path,check=True)
        subprocess.run(["git","-c","user.name=REI derived replay",
                        "-c","user.email=rei-replay@example.invalid",
                        "commit","-q","-m","derived restored snapshot (NOT original commit)"],
                        cwd=path,check=True)
    return subprocess.check_output(["git","rev-parse","HEAD"],cwd=path,text=True).strip()
wu=root/"offline_wu"
rei_derived=init_git(root)
wu_derived=init_git(wu)
env=os.environ.copy()
env.update({"WU088_HH_LOCAL_REPO":str(wu),"REI_NATIVE_CONSUMER_ROOT":str(root),
            "PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1"})
groups=[
("C12",["research/rei_crossrepo_integration_20261015/test_crossrepo.py"],6),
("C13",["research/rei_c13_live_source_20261015/test_short_interval.py",
        "research/rei_c13_live_source_20261015/test_coalesce.py",
        "research/rei_c13_live_source_20261015/test_pr136.py"],16),
("C14",["research/rei_c14_thomson_receiver_20261015/test_dynamic_thomson.py"],9),
("C15",["research/rei_c15_two_way_shear_20261015/test_c15_coupled.py"],11),
("C16A",["research/rei_c16_source_energy_20261015/test_c16_exchange.py"],9),
("C16B",["research/rei_c16_escape_20261015/test_escape_transport.py"],11)]
report={"schema":"rei.c16B.v3.replay.v1","science_commit":meta["science_commit"],
"source_sha_verified":True,"derived_repo_commit_not_original":rei_derived,
"derived_wu_commit_not_original":wu_derived,"wu_rate_admission":"HOLD","tests":[]}
for group,paths,expected in groups:
    total=0
    for p in paths:
        start=time.perf_counter()
        v=subprocess.run([sys.executable,p],cwd=root,env=env,capture_output=True,text=True)
        output=v.stdout+"\n"+v.stderr
        m=re.search(r"Ran (\d+) tests?",output)
        count=int(m.group(1)) if m else -1
        passed=v.returncode==0 and bool(re.search(r"(?m)^OK\s*$",output))
        row={"group":group,"path":p,"count":count,"exit":v.returncode,
             "pass":passed,"time_s":round(time.perf_counter()-start,4),
             "output_tail":output[-2000:]}
        report["tests"].append(row)
        total+=count
        print(group,p,count,"PASS" if passed else "FAIL",flush=True)
        if not passed:break
    if total!=expected or not all(x["pass"] for x in report["tests"] if x["group"]==group):
        report["status"]="FAIL_"+group
        break
else:
    report["total_pass"]=sum(x["count"] for x in report["tests"])
    report["status"]="PASS" if report["total_pass"]==62 else "FAIL_TOTAL"
(root/"V3_TEST_RECEIPT.json").write_text(json.dumps(report,indent=2)+"\n")
print("FINAL:",report["status"],report.get("total_pass"),flush=True)
sys.exit(0 if report["status"]=="PASS" else 1)
'''
readme="""REI C16B PR149 source-restorable v3. The 195 original v2 entries are
unchanged. This bundle additionally carries exact C12-negative-provider
REI rust source, an original WU PHYS19 contract and offline replay runner.
Extract as one top-level folder, run python3 replay_v3.py with numpy installed.
Requires git only for DERIVED local replay HEADs demanded by the *unmodified*
original WU guard; source provenance is pinned SHA256 and original commit IDs,
NEVER the derived git commits. HH physical rate still HOLD. NO production
physics promotion, no historical AX08 private state, no source solver changes.
BACKUP_MANIFEST.json refers historically to v2; V3_MANIFEST covers all v3.
"""
assert sha(ORIG.read_bytes())=="005bda53ada3c81077b7bd6e9246a2296e8009dadaa8804fbd3f010d3c483635"
with zipfile.ZipFile(ORIG) as z:
    entries={n[len(ZIP_ROOT)+1:]:z.read(n) for n in z.namelist()
             if n.startswith(ZIP_ROOT+"/") and not n.endswith("/")}
assert len(entries)==195,len(entries)
for rel in ("rust/rei_microphysics/src/coverage.rs",
            "rust/rei_microphysics/src/axbi_sources.rs",
            "rust/rei_microphysics/src/ft03_controlled.rs"):
    d=subprocess.check_output(["git","-C",str(R),"show",REI+":"+rel])
    assert sha(d)==PIN[rel],rel
    if rel in entries:assert entries[rel]==d
    entries[rel]=d
wu_guard="research/rei_crossrepo_integration_20261015/suppliers/wu/phys44_rei_guard.py"
assert sha(entries[wu_guard])==PIN[wu_guard]
d=subprocess.check_output(["git","-C",str(W),"show",WU+":"+C])
assert sha(d)==PIN["offline_wu/"+C]
entries["offline_wu/"+C]=d
entries["replay_v3.py"]=runner.encode()
entries["README_RESTORE_V3.txt"]=readme.encode()
manifest={
 "schema":"rei.c16B.v3.full_payload.v1",
 "created_utc":datetime.now(timezone.utc).isoformat(),
 "science_commit":REI,"WU_source_commit":WU,
 "parent_v2_sha256":sha(ORIG.read_bytes()),
 "original_v2_entries":195,"science_source_changes":0,
 "physical_HH_rate":"HOLD_NOT_ADMITTED",
 "pinned_source_sha256":PIN,
 "payload_sha256":{n:{"sha256":sha(b),"bytes":len(b)} for n,b in sorted(entries.items())}}
entries["V3_MANIFEST.json"]=(json.dumps(manifest,indent=2)+"\n").encode()
dst=OUT/(NAME+"_v3.zip")
with zipfile.ZipFile(dst,"w",zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for n,b in sorted(entries.items()):
        z.writestr(ZIP_ROOT+"/"+n,b)
with zipfile.ZipFile(dst) as z:
    assert z.testzip() is None and len(z.namelist())==len(entries)
    for n,m in manifest["payload_sha256"].items():
        assert sha(z.read(ZIP_ROOT+"/"+n))==m["sha256"],n
receipt={"schema":"rei.c16B.v3.local_build.v1","archive":dst.name,
"sha256":sha(dst.read_bytes()),"bytes":dst.stat().st_size,
"entries":len(entries),"science_commit":REI}
(OUT/"V3_BUILD_RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
