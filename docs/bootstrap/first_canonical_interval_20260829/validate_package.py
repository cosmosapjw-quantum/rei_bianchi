#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PACKAGE="REI-FIRST-CANONICAL-INTERVAL-BOOTSTRAP-20260829-R1"
BASE="ae3402713c4b6530ab2b27f008f5f5d5c6a999ed";BASE_TREE="e7bce0e77797f7c755059a1c88e284591728b77c"
AUDIT="ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e";AUDIT_TREE="c8167922076f52628b1f7243c9ebd8b40ebe7508"
STAGE="stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY";STAGE_TREE="213c29c4b9d6bf4a626111c105bc2d7979507c49"
FILES={"PACKAGE.json","CODEX_HANDOFF.md","validate_package.py"}
def fail(x): raise SystemExit("FAIL: "+x)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(repo,*args):
 p=subprocess.run(["git","--no-replace-objects",*args],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode: fail("git "+" ".join(args)+": "+p.stderr.strip())
 return p.stdout.removesuffix("\n")
def local():
 e={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():
   d,n=line.split(maxsplit=1)
   if n in e: fail("duplicate manifest")
   e[n]=d
 if set(e)!=FILES: fail("manifest closure")
 for n,d in e.items():
  if sha(ROOT/n)!=d: fail("digest "+n)
 p=json.loads((ROOT/"PACKAGE.json").read_text())
 if p["package_id"]!=PACKAGE: fail("package id")
 if p["exact_next_action"]!="FIRST_CANONICAL_INTERVAL_BOOTSTRAP_RUN": fail("next action")
 if p["stage"]["tree"]!=STAGE_TREE: fail("stage tree")
def live(repoarg):
 repo=Path(git(repoarg,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse",BASE+"^{tree}")!=BASE_TREE: fail("base tree")
 if git(repo,"rev-parse",AUDIT+"^{tree}")!=AUDIT_TREE: fail("audit tree")
 if git(repo,"rev-parse","HEAD:"+STAGE)!=STAGE_TREE: fail("stage extraction")
 dep=repo/"external/rec_bianchi.bootstrap_dependency_candidate.json"
 if not dep.is_file(): fail("dependency candidate missing")
 d=json.loads(dep.read_text())
 if d["status"]!="MONITOR_ONLY_NO_NUMERICAL_IMPORT": fail("dependency status")
 if d["rec_bootstrap"]["head"]!="2fb8af1c08b3622322d5b54889f386c3a7587344": fail("rec dependency head")
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--live",action="store_true");ap.add_argument("--repo",default=".");a=ap.parse_args()
 local()
 if a.live: live(Path(a.repo))
 print(json.dumps({"status":"PASS","package_id":PACKAGE,"stage_tree":STAGE_TREE,
 "exact_next_action":"FIRST_CANONICAL_INTERVAL_BOOTSTRAP_RUN",
 "claim":"NO_PASS_FIRST_CANONICAL_INTERVAL","live":a.live},sort_keys=True))
