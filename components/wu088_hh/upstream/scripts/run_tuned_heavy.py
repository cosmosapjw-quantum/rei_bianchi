#!/usr/bin/env python3
"""Prepare the R31M candidate sidecar and invoke the durable H orchestrator."""
from pathlib import Path
import argparse,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from build_native import build
from wu088_hh.autotune import validate_tuning_profile
from wu088_hh.hardware import inspect_host
from wu088_hh.promotion import validate_science_regression, sanitize_trusted_native_environment
import hashlib

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--tuning-profile',type=Path,required=True)
    p.add_argument('--regression',type=Path,default=ROOT/'evidence/host_5900x/SCIENCE_RESOLUTION_NATIVE_REGRESSION.json')
    p.add_argument('--n',type=int,choices=(160,192),required=True);p.add_argument('--g',type=int,default=80);p.add_argument('--z',type=float,required=True)
    p.add_argument('--gamma-scale',choices=('unit','R'),default='unit');p.add_argument('--max-new-pairs',type=int,default=12);p.add_argument('--max-wall-seconds',type=float,default=180.)
    p.add_argument('--execution-lane',choices=('local',),default='local');p.add_argument('--describe',action='store_true');a=p.parse_args()
    built=build();profile=json.loads(a.tuning_profile.read_text());selected=profile['selected']
    host=inspect_host(use_smt=bool(selected.get('use_smt',False)),requested_workers=int(selected['processes']),kernel_threads=int(selected['kernel_threads']))
    validate_tuning_profile(profile,host,built['build_key'])
    regression=json.loads(a.regression.read_text());promotion=validate_science_regression(regression,profile_sha256=sha(a.tuning_profile),build_key=built['build_key'])
    env=sanitize_trusted_native_environment(
        os.environ,
        R31K_RUNTIME_ROOT=str(a.runtime.resolve()),
        WU088_R31M_CANDIDATE_SO=built['libraries']['candidate']['path'],
        WU088_R31M_TUNING_PROFILE=str(a.tuning_profile.resolve()),
        WU088_R31M_REGRESSION=str(a.regression.resolve()),
        WU088_R31M_BUILD_KEY=built['build_key'],
    )
    cmd=[sys.executable,str(ROOT/'scripts/wide_hybrid_orchestrator_cost.py'),'--n',str(a.n),'--g',str(a.g),'--z',repr(a.z),'--gamma-scale',a.gamma_scale,
         '--max-new-pairs',str(a.max_new_pairs),'--max-wall-seconds',str(a.max_wall_seconds),'--execution-lane','local',
         '--legacy-runner',str(ROOT/'vendor/orchestration/r31m_tuned_local_adapter.py'),'--tuning-profile',str(a.tuning_profile.resolve())]
    if a.describe:cmd.append('--describe')
    print(json.dumps({'status':'R31M_TUNED_ROUTE_READY','promotion':promotion,'selected':selected,'candidate_so':built['libraries']['candidate']['path'],'command':cmd}),flush=True)
    raise SystemExit(subprocess.run(cmd,env=env).returncode)
if __name__=='__main__':main()
