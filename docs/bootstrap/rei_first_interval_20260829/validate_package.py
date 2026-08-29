#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES={"PACKAGE.json","IMPLEMENTATION_PLAN.md","CODEX_HANDOFF.md","validate_package.py"}
HEAD="ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e";TREE="c8167922076f52628b1f7243c9ebd8b40ebe7508";BRANCH="audit/ode-four-loop-external-20260823"
BLOBS={"PROJECT_STATE.json":"183b3fa4daa4abbbc37ff1d38b6325f825ba1657","handoff/CURRENT_HANDOFF_PROMPT.md":"efa4ea901cc3bab65d7116402fa73bea4691a6dd","docs/science/current_00_READ_FIRST.md":"cc48d951fbc006beaec93e2ff534eb45cf904698","external/rec_bianchi.lock.json":"230c0b61acd7154d4f64b59f7102b6227d990318","src/rei_bianchi/run_first_interval_refinement.py":"5d39fef633662178a71685dac90e4ffe9a0a788d"}
def fail(x):raise SystemExit("FAIL: "+x)
def dig(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(r,*a):
 p=subprocess.run(["git","--no-replace-objects",*a],cwd=r,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode:fail("git "+" ".join(a)+": "+p.stderr.strip())
 return p.stdout.removesuffix("\n")
def local():
 e={}
 for line in (ROOT/"MANIFEST.sha256").read_text().splitlines():
  if line.strip():d,n=line.split(maxsplit=1);e[n]=d
 if set(e)!=FILES:fail("manifest closure")
 for n,d in e.items():
  if dig(ROOT/n)!=d:fail("digest "+n)
 p=json.loads((ROOT/"PACKAGE.json").read_text())
 if p["package_id"]!="REI-BIANCHI-FIRST-INTERVAL-BOOTSTRAP-20260829-R2":fail("id")
 if p["exact_next_action"]!="REI-AUDIT-COMPAT-00_THEN_REI-INTERVAL-02":fail("next")
 if p["audit_shadow"]["wholesale_import"]!="FORBIDDEN":fail("shadow")
 if p["rec_dependency"]["numerical_import"]!="FORBIDDEN":fail("rec")
 if p["rec_dependency"]["package_head"]!="47e19df30a5e71e536d3d5167ffa3b78638a59c5":fail("rec package head")
 if p["rec_dependency"]["package_tree"]!="e7400fda8511e582f5bc4944b96183977412f4f3":fail("rec package tree")
 if p["rec_dependency"]["consumption"]!="MONITORING_METADATA_ONLY_NO_NUMERICAL_IMPORT":fail("rec consumption")
 if p["mock_roundtrip"]["pr"]!=10:fail("mock")
def live(repo):
 repo=Path(git(repo,"rev-parse","--show-toplevel"))
 if git(repo,"rev-parse","--verify","refs/remotes/origin/"+BRANCH)!=HEAD:fail("branch")
 if git(repo,"rev-parse",HEAD+"^{tree}")!=TREE:fail("tree")
 for path,blob in BLOBS.items():
  if git(repo,"rev-parse",HEAD+":"+path)!=blob:fail("blob "+path)
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--live",action="store_true");ap.add_argument("--repo",default=".");a=ap.parse_args();local()
 if a.live:live(a.repo)
 print(json.dumps({"status":"PASS","package_id":"REI-BIANCHI-FIRST-INTERVAL-BOOTSTRAP-20260829-R2","next":"REI-AUDIT-COMPAT-00_THEN_REI-INTERVAL-02","live":a.live},sort_keys=True))
