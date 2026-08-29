#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

AUDIT_HEAD='ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e'
AUDIT_TREE='c8167922076f52628b1f7243c9ebd8b40ebe7508'
PKG_BRANCH='agent/plans/rei-first-interval-rec-bridge-20260829-r1'
PKG_PREFIX='docs/bootstrap/rei_first_interval_rec_bridge_20260829/'
ROOT=Path(__file__).resolve().parent

def fail(msg): raise SystemExit('FAIL: '+msg)
def git(repo,*args):
 p=subprocess.run(['git','--no-replace-objects',*args],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 if p.returncode: fail('git '+' '.join(args)+': '+p.stderr.strip())
 return p.stdout.strip()
def local():
 for name in ['PACKAGE.json','REC_REI_INTERFACE_BRIDGE.json','WORK_UNITS.json','BASS_TRANSFER_MATRIX.json']:
  json.loads((ROOT/name).read_text())
 package=json.loads((ROOT/'PACKAGE.json').read_text())
 units=json.loads((ROOT/'WORK_UNITS.json').read_text())
 if package['audit_source']['head']!=AUDIT_HEAD or package['audit_source']['tree']!=AUDIT_TREE: fail('audit identity')
 if units['exact_next_action']!='REI-BOOT-00': fail('next action')
 if package['audit_source']['candidate_verdict']!='STOP_INVALID_HOLD': fail('audit claim boundary')
 if package['rec_dependency']['surrogate_or_silent_replacement'] is not False: fail('rec dependency firewall')
def live(repo_arg):
 repo=Path(git(repo_arg,'rev-parse','--show-toplevel'))
 pkg=git(repo,'rev-parse','--verify','refs/remotes/origin/'+PKG_BRANCH)
 audit=git(repo,'rev-parse','--verify','refs/remotes/origin/audit/ode-four-loop-external-20260823')
 if audit!=AUDIT_HEAD or git(repo,'rev-parse',audit+'^{tree}')!=AUDIT_TREE: fail('audit ref moved')
 base=git(repo,'merge-base','refs/remotes/origin/main',pkg)
 changed=git(repo,'diff','--name-only',base+'..'+pkg).splitlines()
 if not changed or any(not p.startswith(PKG_PREFIX) for p in changed): fail('package changed-path closure')
 lock='external/rec_bianchi.lock.json'
 if git(repo,'rev-parse',base+':'+lock)!=git(repo,'rev-parse',pkg+':'+lock): fail('rec lock changed by package')
 print(json.dumps({'status':'PASS','package_head':pkg,'implementation_base':base,'changed_paths':len(changed),'rec_lock':'UNCHANGED','exact_next_action':'REI-BOOT-00'}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--live',action='store_true');ap.add_argument('--repo',default='.')
 a=ap.parse_args();local();
 if a.live: live(a.repo)
 else: print(json.dumps({'status':'PASS','exact_next_action':'REI-BOOT-00','live':False}))
