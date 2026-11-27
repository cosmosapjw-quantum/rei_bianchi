"""Additive, resource-planned pinned backend builder. Dry-run by default.

Only build concurrency changes relative to the prior strict compiler flags.
No installation into the old runtime and no scientific numerical execution.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time

HERE=Path(__file__).resolve().parent
NEW=HERE.parent
PRIOR=NEW.parent/'host_synthetic_readiness_20261001_v1'
PINS={'backend_runner.py':'0749c157640e849194d88173098e8220206f5a4b404e7c6b7a5ffb628e2dc3ac',
      'provenance_gate.py':'12857ebed9dbcf6e14484388da491fd407c0af9a997588fe49e2b13048e42c5e'}
GiB=1024**3


def load(path,name,sha=None):
    if sha and hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
        raise ValueError('immutable module pin mismatch: '+path.name)
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod


def modules():
    return (load(PRIOR/'backend_runner.py','_ncp_prior_builder',PINS['backend_runner.py']),
            load(PRIOR/'provenance_gate.py','_ncp_prior_provenance',PINS['provenance_gate.py']),
            load(NEW/'host_plan/planner.py','_ncp_host_planner'))


def configuration(prior,host_plan,requested_jobs=None):
    # Each compiler gets a 2-GiB address-space cap. This is not aggregate cgroup enforcement.
    if host_plan['status']!='PLAN_READY':raise ValueError('host resource plan blocked')
    capacity=min(64,max(1,host_plan['cpu_budget']-1),host_plan['job_memory_budget_bytes']//(2*GiB))
    if capacity<1:raise ValueError('less than one bounded compiler fits')
    if requested_jobs is not None and (type(requested_jobs)is not int or not 1<=requested_jobs<=capacity):
        raise ValueError('requested build jobs exceed CPU/memory capacity')
    c=dict(prior.CONFIG);c.update(jobs=capacity if requested_jobs is None else requested_jobs,memory_mib=2048)
    return c


def steps(prior,root,tools,c):
    root=Path(root);prefix=root/'prefix';out=[]
    for name,spec in prior.SOURCES.items():
        cwd=root/'sources'/name/spec['root']
        def add(stage,argv):out.append({'id':name+'-'+stage,'library':name,'stage':stage,'cwd':str(cwd),'argv':argv,'wall_seconds':c[stage+'_seconds']})
        if name=='flint':add('bootstrap',[tools['sh'],'./bootstrap.sh'])
        args=[tools['sh'],'./configure','--prefix='+str(prefix),'--libdir='+str(prefix/'lib')]
        if name in ('mpfr','flint'):args.append('--with-gmp='+str(prefix))
        if name=='flint':args.extend(['--with-mpfr='+str(prefix),'--with-blas=no','--with-ntl=no'])
        add('configure',args)
        add('build',[tools['make'],'-j'+str(c['jobs'])])
        # Keep test parallelism bounded separately: FLINT test subprocesses can fan out.
        check=[tools['make'],'-j'+str(min(c['jobs'],2)),'check']
        if name=='flint':check.append('MOD=arb acb acb_hypgeom acb_calc')
        add('check',check)
        add('install',[tools['make'],'-j'+str(c['jobs']),'install'])
    return out


def execute(prior,gate,pre,resource_plan,c):
    if pre['missing_tools']:raise ValueError('missing build tools: '+', '.join(pre['missing_tools']))
    root=Path(pre['output']);root.mkdir(exist_ok=False)
    prior.write_json(root/'PREFLIGHT.json',pre);prior.write_json(root/'HOST_RESOURCE_PLAN.json',resource_plan)
    prior.write_json(root/'FAST_BUILD_CONFIG.json',c)
    start=time.monotonic();deadline=start+c['global_wall_seconds'];completed=[]
    report={'status':'BUILD_STARTED','actual_HH_evaluations':0,'native_synthetic_executed':False,
            'scientific_promotion':False,'aggregate_memory_hard_limit':False}
    try:
        for name in ('sources','prefix','logs','home','tmp'):(root/name).mkdir()
        prefix=root/'prefix';tools=pre['tools'];env=prior.clean_environment(root,prefix,tools,c)
        for name,spec in prior.SOURCES.items():
            prior.safe_extract(pre['sources'][name]['path'],root/'sources'/name,
                               expected_sha256=spec['sha256'],expected_root=spec['root'])
            if time.monotonic()>=deadline:raise ValueError('global budget during extraction')
        def run(step):
            value=prior.run_stage(step,root,env,c,deadline);completed.append(value);return value
        compilers={}
        for key in ('cc','cxx'):
            r=run({'id':key+'-version','stage':'version','cwd':str(root),'argv':[tools[key],'--version'],'wall_seconds':10})
            compilers[key]={**prior.identity(tools[key]),'version':Path(r['stdout']['path']).read_text()[:16384]}
        for step in steps(prior,root,tools,c):run(step)
        record={'verified_build_provenance':True,'compatibility_assertion_only':True,
                'prefix':str(prefix),'compiler':compilers['cc'],'cxx_compiler':compilers['cxx'],
                'libraries':{},'execution_witness':'Additive fast-build stage receipts; not scientific admission.'}
        for name,spec in prior.SOURCES.items():
            binary=prior.identity(prefix/'lib'/('lib'+name+'.so'))
            if not Path(binary['path']).is_relative_to(prefix):raise ValueError('binary outside fresh prefix')
            logs=[{'stage':r['stage'],'path':r['receipt']['path'],'sha256':r['receipt']['sha256'],'exit_code':0,
                   'stdout':r['stdout'],'stderr':r['stderr']} for r in completed if r.get('library')==name]
            record['libraries'][name]={'version':spec['version'],'source_archive_path':pre['sources'][name]['path'],
               'source_archive_sha256':spec['sha256'],'binary_path':binary['path'],'binary_sha256':binary['sha256'],
               'compiler':compilers['cc'],'flags':env['CFLAGS'].split(),
               'abi':{'machine':platform.machine(),'system':platform.system(),'binary_format':'ELF'},
               'build_logs':logs,'build_log_sha256':next(x['sha256'] for x in logs if x['stage']=='build')}
        rec=root/'BACKEND_BUILD_PROVENANCE.json';prior.write_json(rec,record);gate.verify_backend(rec,prefix)
        report.update(status='PINNED_BACKEND_BUILD_IDENTITY_VERIFIED',backend_provenance=prior.identity(rec),
                      next_gate='Build and execute native_cache exact-ball fixtures and MPI smoke on this host')
        return report
    except Exception as exc:
        report.update(status='BUILD_FAILED',error=str(exc),error_type=type(exc).__name__);raise
    finally:
        report.update(wall_seconds=time.monotonic()-start,completed_stages=[x['id'] for x in completed])
        prior.write_json(root/'FAST_BUILD_RESULT.json',report)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--jobs',type=int);p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    try:
        prior,gate,hp=modules();pre=prior.preflight(a.source_dir,a.output);resource_plan=hp.plan(hp.detect())
        blocked=list(pre['missing_tools'])+resource_plan['blocked_reasons']
        c=None
        if resource_plan['status']=='PLAN_READY':c=configuration(prior,resource_plan,a.jobs)
        status='BLOCKED' if blocked else 'PLAN_READY'
        info={'status':status,'preflight':pre,'host_plan':resource_plan,'config':c,
              'blocked_reasons':blocked,'build_flags_unchanged':'-O2 -fno-fast-math -ffp-contract=off',
              'builder_identity':prior.identity(Path(__file__)),'prior_modules':PINS,
              'native_builds_executed':0,'actual_HH_evaluations':0,'scientific_promotion':False}
        if c:
            proposed={k:pre['tools'].get(k,'/UNAVAILABLE/'+v) for k,v in prior.TOOL_NAMES.items()}
            info['steps']=steps(prior,a.output,proposed,c)
        if a.execute:
            if blocked:raise ValueError('build prerequisites blocked: '+', '.join(blocked))
            info=execute(prior,gate,pre,resource_plan,c)
        print(json.dumps(info,indent=2));return 0 if status=='PLAN_READY' or a.execute else 3
    except Exception as exc:
        print(json.dumps({'status':'REFUSED','error':str(exc),'scientific_promotion':False}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
