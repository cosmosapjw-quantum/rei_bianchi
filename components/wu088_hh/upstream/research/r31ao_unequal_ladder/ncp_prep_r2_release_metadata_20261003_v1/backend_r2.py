"""Explicit R2 orchestration derived from pinned fast.execute. Frozen modules untouched."""
from pathlib import Path
import time,platform
from support import ref
from cheap_gates import fast,fidelity
steps=fast.steps

def generated_metadata(root,step):
 rows=[]
 if 'library' not in step:return rows
 source=root/'sources'/step['library']
 for p in sorted(source.rglob('*')):
  if p.name in ('configure','configure.ac','aclocal.m4','Makefile.in','Makefile.am','gmp.info') and p.is_file():
   rows.append(dict(**ref(p),mtime_ns=p.stat().st_mtime_ns))
 return rows

def execute_r2(prior,gate,pre,resource_plan,c,extractor):
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
            extractor.safe_extract(pre['sources'][name]['path'],root/'sources'/name,
                               expected_sha256=spec['sha256'],expected_root=spec['root'])
            if time.monotonic()>=deadline:raise ValueError('global budget during extraction')
        prior.write_json(root/'EXTRACTION_METADATA_FIDELITY.json', {'extractor':ref(Path(extractor.__file__)), 'archives':[fidelity(Path(pre['sources'][name]['path']),root/'sources'/name) for name in prior.SOURCES]})
        def run(step):
            before=generated_metadata(root,step)
            try:
                value=prior.run_stage(step,root,env,c,deadline);completed.append(value);return value
            finally:
                prior.write_json(root/'logs'/step['id']/'GENERATED_METADATA_TRANSITION.json',{'before':before,'after':generated_metadata(root,step),'orchestration':ref(Path(__file__))})
        compilers={}
        for key in ('cc','cxx'):
            r=run({'id':key+'-version','stage':'version','cwd':str(root),'argv':[tools[key],'--version'],'wall_seconds':10})
            compilers[key]={**prior.identity(tools[key]),'version':Path(r['stdout']['path']).read_text()[:16384]}
        for step in steps(prior,root,tools,c):run(step)
        record={'verified_build_provenance':True,'compatibility_assertion_only':True,
                'prefix':str(prefix),'compiler':compilers['cc'],'cxx_compiler':compilers['cxx'],
                'r2_pipeline_identity':pre['r2_pipeline_identity'],'libraries':{},'execution_witness':'Additive fast-build stage receipts; not scientific admission.'}
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
