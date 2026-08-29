#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PACKAGE_ID="REI-FIRST-CANONICAL-INTERVAL-BOOTSTRAP-20260829-R1"
MAIN="ae3402713c4b6530ab2b27f008f5f5d5c6a999ed";MAIN_TREE="e7bce0e77797f7c755059a1c88e284591728b77c"
AUDIT="ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e";AUDIT_TREE="c8167922076f52628b1f7243c9ebd8b40ebe7508"
STAGE="stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY";STAGE_TREE="213c29c4b9d6bf4a626111c105bc2d7979507c49"
REC_MAIN="5a09f3797210284f83a1a1adb0e0092d1ac48475";REC_MAIN_TREE="4002915ad851afc2ab71f94a882cc99d81748062"
FILES={"README.md","PACKAGE.json","IMPLEMENTATION_PLAN.md","CODEX_HANDOFF.md","validate_package.py"}
def fail(x):raise SystemExit("FAIL: "+x)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):
 p=subprocess.run(["git","--no-replace-objects",*args],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode:fail("git "+" ".join(args)+": "+p.stderr.strip())
 return p.stdout.removesuffix("\n")
def local():
 e={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   d,n=line.split(maxsplit=1)
   if n in e:fail("duplicate manifest")
   e[n]=d
 if set(e)!=FILES:fail("manifest closure")
 for n,d in e.items():
  if sha(ROOT/n)!=d:fail("digest "+n)
 p=json.loads((ROOT/"PACKAGE.json").read_text())
 if p["package_id"]!=PACKAGE_ID:fail("package id")
 if p["state"]["exact_next_action"]!="REI-BOOTSTRAP-00":fail("next action")
 if p["source"]["reviewed_stage"]["tree"]!=STAGE_TREE:fail("stage tree")
 if p["rec_dependency"]["current_first_interval"]["rec_numerical_import"] is not False:fail("rec import")
 if p["rec_dependency"]["future_primordial_splice"]["may_proceed"] is not False:fail("splice gate")
 if [x["id"] for x in p["work_units"]] != ["REI-BOOTSTRAP-00","REI-ENDPOINT-01","REI-FIRST-INTERVAL-02","REI-AUDIT-03","REI-DELIVER-04"]:fail("DAG")
def live(repoarg,ref):
 repo=Path(git(repoarg,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse",MAIN+"^{tree}")!=MAIN_TREE:fail("main tree")
 if git(repo,"rev-parse",AUDIT+"^{tree}")!=AUDIT_TREE:fail("audit tree")
 if git(repo,"rev-parse",AUDIT+":"+STAGE)!=STAGE_TREE:fail("stage tree")
 if git(repo,"rev-parse",ref+"^{commit}")!=ref:fail("implementation commit")
 if git(repo,"rev-parse",ref+":"+STAGE)!=STAGE_TREE:fail("implementation stage")
 lock=json.loads((repo/"external/rec_bianchi.lock.json").read_text())
 if lock["head_sha"]!=REC_MAIN or lock["head_tree"]!=REC_MAIN_TREE:fail("rec lock")
 if lock["first_interval_dependency"]!="MONITOR_ONLY_NONBLOCKING_NO_REC_NUMERICAL_IMPORT":fail("rec first interval firewall")
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--live",action="store_true");ap.add_argument("--repo",default=".");ap.add_argument("--implementation-ref");a=ap.parse_args()
 local()
 if a.live:
  if not a.implementation_ref:fail("--implementation-ref required")
  live(Path(a.repo),a.implementation_ref)
 print(json.dumps({"status":"PASS","package_id":PACKAGE_ID,"exact_next_action":"REI-BOOTSTRAP-00","claim":"NO_PASS_FIRST_CANONICAL_INTERVAL","live":a.live},sort_keys=True))
