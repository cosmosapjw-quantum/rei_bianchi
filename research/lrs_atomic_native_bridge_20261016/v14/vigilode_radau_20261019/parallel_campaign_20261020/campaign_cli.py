#!/usr/bin/env python3
"""One-command, offline, bounded NCP reproduction of the still-pending LRS backlog."""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from collections import defaultdict
import campaign
import shards

HERE=Path(__file__).resolve().parent
SCIENCE='5248822167e3fbe374f4333f7f2efdcdbfdaeeaf'

def crate(work,variant):return Path(work)/'variants'/variant/'native_owner/rust/rei_microphysics'
def binary(work,variant,name):return Path(work)/'targets'/variant/'release/examples'/name
def preserve_partial(path):
    path=Path(path)
    if path.exists():path.rename(path.with_name(path.name+'.partial_'+str(time.time_ns())))

def prepare_variant(inputroot,work,variant):
    inputroot=Path(inputroot);work=Path(work);destination=work/'variants'/variant
    marker=destination/'PREPARED_VARIANT.json'
    if marker.exists():
        old=json.loads(marker.read_text())
        for name,expected in old['source_sha256'].items():
            if campaign.digest(destination/name)!=expected:raise ValueError('PREPARED_SOURCE_IDENTITY_MISMATCH')
        return old
    preserve_partial(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    if variant=='v12':
        destination.mkdir();shutil.copytree(inputroot/'v12/native_owner',destination/'native_owner',ignore=shutil.ignore_patterns('target','.git','__pycache__'))
    elif variant=='v13':
        destination.mkdir()
        subprocess.run([sys.executable,str(inputroot/'v13/RESTORE_NATIVE.py'),'--base',str(inputroot/'v12/native_owner'),'--out',str(destination/'native_owner')],check=True)
    elif variant=='ssprk':
        subprocess.run([sys.executable,str(inputroot/'v14/time_centered_ssprk2_20261019/restore_ssprk2_native.py'),'--input-root',str(inputroot),'--output-root',str(destination)],check=True)
    else:raise ValueError('unknown variant')
    if variant in('v12','v13'):
        examples=crate(work,variant)/'examples'
        original=examples/('v12_thermal_clock_sweep.rs'if variant=='v12'else'v13_source_clock_sweep.rs')
        shards.derive(original,examples/f'{variant}_clock_shard.rs',variant)
    hashes={str(p.relative_to(destination)):campaign.digest(p)for p in sorted(destination.rglob('*'))if p.is_file()and not any(x in('target','.git','__pycache__')for x in p.relative_to(destination).parts)}
    result={'status':'PREPARED_VERIFIED','variant':variant,'source_sha256':hashes,'original_sources_modified':False,'new_example_edits':'mandatory selector guard only'if variant!='ssprk'else'NONE;normal SSPRK restore reused'}
    campaign.write(marker,result);return result

def duration_inputs(path,variant):
    """Read saved final-row times only. These are heuristic scheduling inputs."""
    if not path or not Path(path).is_file():return {},{'status':'ABSENT_USE_N_HEURISTIC','path':str(path)if path else None}
    durations={}
    with Path(path).open(newline='')as f:
        for row in csv.DictReader(f):
            n=int(row['n'if variant=='v12'else'N'])
            if int(row['step'])!=n:continue
            key=(row['case'],row['mode'],n)if variant=='v12'else(row['mode'],n)
            durations[key]=float(row['elapsed_wall_s'if variant=='v12'else'wall_s'])
    return durations,{'status':'SAVED_LOCAL_LAST_ROW_TIMES_ONLY','path':str(path),'sha256':campaign.digest(path),'histories':len(durations),'W_sum_s':sum(durations.values()),'L_max_s':max(durations.values(),default=0),'scope':'Local historical timing input; not an NCP runtime prediction or measured parallel speedup.'}

def restoration_inputs(inputroot,variant):
    """Files actually consumed by the committed restore chain, not unrelated evidence."""
    root=Path(inputroot);files=[]
    if variant in('v13','ssprk'):
        spec=root/'v13/SOURCE_DELTA.json';d=json.loads(spec.read_text())
        files += [root/'v13/RESTORE_NATIVE.py',spec]+[root/'v13'/name for name in d['patch_chunks']]
    if variant=='ssprk':
        spec=root/'v14/SOURCE_DELTA.json';d=json.loads(spec.read_text())
        files += [root/'v14/RESTORE_V14.py',spec]+[root/'v14'/name for name in d['files']]
        ss=root/'v14/time_centered_ssprk2_20261019';spec=ss/'SOURCE_DELTA_SSPRK2.json';d=json.loads(spec.read_text())
        files += [ss/'restore_ssprk2_native.py',spec]+[ss/'native_files'/name for name in d['payload_sha256']]
    return sorted(str(p)for p in set(files))

def make_manifest(inputroot,work,cargo,build_jobs=1,reference_root=None):
    inputroot=Path(inputroot).resolve();work=Path(work).resolve();cargo=Path(shutil.which(str(cargo))or str(cargo)).absolute()
    if not 1<=build_jobs<=64:raise ValueError('build jobs must be1..64')
    source_files=[str(p)for p in sorted(HERE.glob('*.py'))if not p.name.startswith('test_')]
    jobs=[];last=None
    for variant in ['v12','v13','ssprk']:
        deps=[last]if last else[]
        prep_id='prepare_'+variant
        prep_inputs=restoration_inputs(inputroot,variant)
        jobs.append({'id':prep_id,'kind':'prepare','argv':[sys.executable,str(HERE/'campaign_cli.py'),'_prepare','--input-root',str(inputroot),'--work-root',str(work),'--variant',variant],'deps':deps,'timeout_s':90,'identity_files':source_files+prep_inputs,'identity_roots':[str(inputroot/'v12/native_owner')],'outputs':[{'path':str(work/'variants'/variant/'PREPARED_VARIANT.json'),'kind':'json'}]})
        build_id='build_'+variant;man=crate(work,variant)/'Cargo.toml'
        examples=[f'{variant}_clock_shard']if variant!='ssprk'else['v15_ssprk_transport_diagnostic','v15_ssprk_coupled_diagnostic']
        argv=[str(cargo),'build','--offline','--locked','--release','--manifest-path',str(man),'-j',str(build_jobs)]
        for ex in examples:argv += ['--example',ex]
        env={'CARGO_TARGET_DIR':str(work/'targets'/variant)}
        if(cargo.parent/'rustc').is_file():env['RUSTC']=str(cargo.parent/'rustc')
        jobs.append({'id':build_id,'kind':'build','argv':argv,'deps':[prep_id],'timeout_s':180,'cpu_slots':build_jobs,'nominal_memory_mb':1024*build_jobs,'environment':env,'identity_roots':[str(crate(work,variant))],'outputs':[{'path':str(binary(work,variant,ex))}for ex in examples]})
        testid='tests_'+variant
        tests=['axbi_driver','axbi_covariant_transport','v12_thermal_clocks']+(['v13_source_clocks']if variant=='v13'else[])if variant!='ssprk'else['ssprk_transport','ssprk_coupled']
        argv=[str(cargo),'test','--offline','--locked','--release','--manifest-path',str(man),'-j',str(build_jobs)]
        for test in tests:argv+=['--test',test]
        argv+=['--','--test-threads=1','--nocapture']
        jobs.append({'id':testid,'kind':'build','argv':argv,'deps':[build_id],'timeout_s':120 if variant=='ssprk'else 240,'cpu_slots':build_jobs,'nominal_memory_mb':1024*build_jobs,'environment':env,'identity_roots':[str(crate(work,variant))],'outputs':[]})
        last=testid
    caps={'v12':180,'v13_1e-5':180,'v13_1e-4':180,'ssprk':300}
    reference_root=Path(reference_root).resolve()if reference_root else inputroot
    d12,timing12=duration_inputs(reference_root/'v12/evidence/NATIVE_SWEEP_RAW.csv','v12')
    v12_ids=[]
    for case in shards.CASES:
        for mode in shards.MODES12:
            for n in shards.LEVELS:
                jid=f'v12_{case}_{mode}_{n}';v12_ids.append(jid)
                jobs.append({'id':jid,'kind':'native','argv':[str(binary(work,'v12','v12_clock_shard')),'{attempt}/rows.csv'],'deps':[last],'timeout_s':180,'budget_groups':['v12'],'environment':{'LRS_SHARD_CASE':case,'LRS_SHARD_MODE':mode,'LRS_SHARD_N':str(n)},'estimated_duration_s':d12.get((case,mode,n),float(n)),'estimate_basis':'saved_local_final_elapsed_wall_s'if(case,mode,n)in d12 else'N_ordering_heuristic_not_seconds','identity_roots':[str(crate(work,'v12'))],'outputs':[{'path':'rows.csv','kind':'csv','rows':n,'columns':46,'key_fields':{'case':case,'mode':mode,'n':str(n)},'step_column':'step'}]})
    v13_ids={};timing13={}
    for x in ['1e-5','1e-4']:
        # Only equal cells/tolerance saved data can provide per-setting duration inputs.
        name='sourceon_x1e5_cells32.csv'if x=='1e-5'else'sourceon_x1e4_cells32.csv'
        dur,meta=duration_inputs(reference_root/'v13/evidence'/name,'v13');timing13[x]=meta;v13_ids[x]=[]
        for mode in shards.MODES13:
            for n in shards.LEVELS:
                jid=f'v13_{x}_{mode}_{n}';v13_ids[x].append(jid)
                jobs.append({'id':jid,'kind':'native','argv':[str(binary(work,'v13','v13_clock_shard')),'{attempt}/rows.csv',x,'256','32','1e-15'],'deps':[last],'timeout_s':180,'budget_groups':['v13_'+x],'environment':{'LRS_SHARD_CASE':x,'LRS_SHARD_MODE':mode,'LRS_SHARD_N':str(n)},'estimated_duration_s':dur.get((mode,n),float(n)),'estimate_basis':'saved_local_final_wall_s'if(mode,n)in dur else'N_ordering_heuristic_not_seconds','identity_roots':[str(crate(work,'v13'))],'outputs':[{'path':'rows.csv','kind':'csv','rows':n,'columns':31,'key_fields':{'mode':mode,'cells':'32','N':str(n)},'step_column':'step'}]})
    for family,deps in [('v12',v12_ids),('v13_1e-5',v13_ids['1e-5']),('v13_1e-4',v13_ids['1e-4'])]:
        jobs.append({'id':'merge_'+family,'kind':'analysis','argv':[sys.executable,str(HERE/'campaign_cli.py'),'_merge','--work-root',str(work),'--family',family],'deps':deps,'timeout_s':60,'identity_files':source_files,'outputs':[{'path':str(work/'merged'/(family+'.csv')),'kind':'csv','rows':12096 if family=='v12'else 3528,'columns':46 if family=='v12'else 31}]})
    for mode in ['transport','fixed','birth']:
        ex='v15_ssprk_transport_diagnostic'if mode=='transport'else'v15_ssprk_coupled_diagnostic';filename='transport.csv'if mode=='transport'else'coupled_'+mode+'.csv'
        outputs=[{'path':filename,'kind':'csv','rows':52 if mode=='transport'else(504 if mode=='fixed'else 1984)}]
        if mode!='transport':outputs += [{'path':filename+suffix,'kind':'csv'}for suffix in ['.segments.csv','.cells.csv','.births.csv']]
        jobs.append({'id':'ssprk_'+mode,'kind':'native','argv':[str(binary(work,'ssprk',ex)),'{attempt}/'+filename]+([]if mode=='transport'else[mode]),'deps':[last],'timeout_s':60 if mode=='transport'else 180,'budget_groups':['ssprk'],'identity_roots':[str(crate(work,'ssprk'))],'outputs':outputs})
    jobs.append({'id':'analysis_v12_saved_reference','kind':'analysis','argv':[sys.executable,str(HERE/'campaign_cli.py'),'_analyze-v12','--input-root',str(reference_root),'--work-root',str(work)],'deps':['merge_v12'],'timeout_s':60,'identity_files':source_files,'outputs':[{'path':str(work/'analysis/V12_REPRODUCTION_SUMMARY.json'),'kind':'json'}]})
    jobs.append({'id':'analysis_v13','kind':'analysis','argv':[sys.executable,str(inputroot/'v13/analyze_source_clocks.py'),str(work/'merged/v13_1e-5.csv'),str(work/'merged/v13_1e-4.csv'),'--output',str(work/'analysis/V13_ANALYSIS.json')],'deps':['merge_v13_1e-5','merge_v13_1e-4'],'timeout_s':60,'identity_files':[str(inputroot/'v13/analyze_source_clocks.py')],'outputs':[{'path':str(work/'analysis/V13_ANALYSIS.json'),'kind':'json'}]})
    jobs.append({'id':'analysis_ssprk','kind':'analysis','argv':[sys.executable,str(HERE/'campaign_cli.py'),'_analyze-ssprk','--input-root',str(inputroot),'--work-root',str(work)],'deps':['ssprk_transport','ssprk_fixed','ssprk_birth'],'timeout_s':60,'identity_files':source_files+[str(inputroot/'v14/time_centered_ssprk2_20261019/theory/independent_coupled_audit.py')],'outputs':[{'path':str(work/'analysis/SSPRK_MECHANICAL_ANALYSIS.json'),'kind':'json'}]})
    return {'schema':'rei.lrs.parallel_backlog.v1','metadata_base':'96aaad584bbecded34485526a4bb53a49708ffc6','current_radau_science_source':SCIENCE,'new_unique_scientific_models':0,'default_skipped_completed':['current_Radau19','borrowed_N2','original_V14_84'],'scope':{'v12_histories':144,'v13_histories':84,'ssprk_transport_rows':52,'ssprk_coupled_histories':16},'timing_inputs':{'v12':timing12,'v13':timing13},'aggregate_caps_s':caps,'jobs':jobs}

def completed_path(work,jid,name):
    receipt=json.loads((Path(work)/'run/CAMPAIGN_RECEIPT.json').read_text());state=receipt['states'][jid]
    if state['status']not in('COMPLETED','REUSED_COMPLETED'):raise ValueError('dependency not completed '+jid)
    return Path(state['attempt'])/name

def merge_family(work,family):
    work=Path(work);m=json.loads((work/'MANIFEST.json').read_text())
    ids=[j['id']for j in m['jobs']if j.get('kind')=='native'and family in j.get('budget_groups',[])]
    paths=[completed_path(work,j,'rows.csv')for j in ids]
    dest=work/'merged'/(family+'.csv')
    preserve_partial(dest)
    if family=='v12':keys=[(c,m,n)for c in shards.CASES for m in shards.MODES12 for n in shards.LEVELS];fields=['case','mode','n'];columns=46
    else:keys=[(m,n)for m in shards.MODES13 for n in shards.LEVELS];fields=['mode','N'];columns=31
    result=campaign.merge_csv(paths,dest,fields,keys,lambda key:int(key[-1]),columns)
    if family=='v12'and(result['histories'],result['rows'])!=(144,12096):raise ValueError('V12 full coverage')
    if family!='v12'and(result['histories'],result['rows'])!=(42,3528):raise ValueError('V13 full coverage')
    campaign.write(dest.with_suffix('.merge.json'),result);return result

def analyze_v12(reference_root,work):
    work=Path(work);source=work/'merged/v12.csv';groups=defaultdict(list);maxima={};rows=0
    with source.open(newline='')as f:
        for row in csv.DictReader(f):
            rows+=1;groups[(row['case'],row['mode'],int(row['n']))].append(int(row['step']))
            for name in ['photon_count_residual_per_H','total_energy_residual_eV_per_H','newton_residual']:
                value=float(row[name])
                if not math.isfinite(value):raise ValueError('nonfinite stored diagnostic '+name)
                maxima[name]=max(maxima.get(name,0),abs(value))
            residuals={
                'electron_per_H_identity':float(row['electrons_per_H'])-(float(row['HII_per_H'])+float(row['HeII_per_H'])+2*float(row['HeIII_per_H'])),
                'hydrogen_per_H_normalization':float(row['HI_per_H'])+float(row['HII_per_H'])-1,
                'helium_per_H_normalization':float(row['HeI_per_H'])+float(row['HeII_per_H'])+float(row['HeIII_per_H'])-float(row['nHe_proper_cm3'])/float(row['nH_proper_cm3']),
                'source_photons_per_H':float(row['source_photons_per_H']),
                'source_energy_eV_per_H':float(row['source_energy_eV_per_H'])}
            for name,value in residuals.items():
                if not math.isfinite(value):raise ValueError('nonfinite reconstructed diagnostic '+name)
                maxima[name]=max(maxima.get(name,0),abs(value))
    expected={(c,m,n)for c in shards.CASES for m in shards.MODES12 for n in shards.LEVELS}
    if set(groups)!=expected or any(v!=list(range(1,k[2]+1))for k,v in groups.items()):raise ValueError('V12 exact matrix coverage')
    refs=[]
    for p in (Path(reference_root)/'v12/evidence').rglob('*.json'):
        refs.append({'path':str(p),'sha256':campaign.digest(p),'scope':'Historical reference/analysis reused as preserved evidence; not a newly integrated reference.'})
    result={'schema':'rei.lrs.v12.stdlib_reproduction_summary.v1','histories':len(groups),'rows':rows,'max_absolute_recorded_and_reconstructed_diagnostics':maxima,'diagnostic_threshold_decision':'OBSERVATIONS_ONLY_NO_NEW_TOLERANCE_OR_SCIENTIFIC_PASS','existing_reference_files':refs,'reference_reintegration':'NOT_RUN_INTENTIONAL','original_analyzer':'Not automatically executed: imports SciPy/numpy and three reference IVPs. Existing reference decisions remain historical.','scientific_admission':'NOT_INFERRED_FROM_EXIT_OR_COVERAGE','comparison_or_reference_obligation':'Historical reference absent'if not refs else'Root review of preserved reference and new raw diagnostics; no tolerance changed.'}
    campaign.write(work/'analysis/V12_REPRODUCTION_SUMMARY.json',result);return result

def analyze_ssprk(inputroot,work):
    work=Path(work);alias=work/'analysis/ssprk_alias';alias.mkdir(parents=True,exist_ok=True);mapping=[]
    expected=set([('fixed_geometry',n)for n in shards.LEVELS]+[(k,n)for k in ['physical_gl2','seeded_disabled_gl2']for n in [32,64,128,256,512]])
    groups=defaultdict(list);counts={'macro':0,'segments':0,'births':0,'cells':0}
    for mode,target in [('fixed','fixed_geometry'),('birth','birth_histories')]:
        p=completed_path(work,'ssprk_'+mode,'coupled_'+mode+'.csv')
        for suffix in ['', '.segments.csv','.cells.csv','.births.csv']:
            original=Path(str(p)+suffix);destination=alias/(target+'.csv'+suffix)
            if destination.exists()and campaign.digest(destination)!=campaign.digest(original):raise ValueError('different SSPRK alias already exists')
            if not destination.exists():shutil.copyfile(original,destination)
            mapping.append({'source':str(original),'alias':str(destination),'sha256':campaign.digest(original)})
            with original.open(newline='')as f:rows=list(csv.DictReader(f))
            which={ '':'macro','.segments.csv':'segments','.cells.csv':'cells','.births.csv':'births'}[suffix];counts[which]+=len(rows)
            if not suffix:
                for row in rows:groups[(row['kind'],int(float(row['m'])))].append(int(float(row['step'])))
    if set(groups)!=expected or any(v!=list(range(1,n+1))for(_,n),v in groups.items()):raise ValueError('SSPRK exact history/step matrix')
    if counts!={'macro':2488,'segments':6456,'births':3968,'cells':2048}:raise ValueError('SSPRK sidecar coverage '+str(counts))
    out=work/'analysis/ssprk_original_audit';out.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(Path(inputroot)/'v14/time_centered_ssprk2_20261019/theory/independent_coupled_audit.py'),'--raw-dir',str(alias),'--out-dir',str(out)]
    subprocess.run(command,check=True)
    result={'schema':'rei.lrs.ssprk.mechanical_analysis.v1','command':command,'alias_mapping':mapping,'counts':counts,'histories':len(groups),'audit_output':str(out/'COUPLED_INDEPENDENT_AUDIT.json'),'audit_sha256':campaign.digest(out/'COUPLED_INDEPENDENT_AUDIT.json'),'reviewer_identity_scope':'Original audit program contains historical reviewer metadata. Running it mechanically does not constitute a new independent review.','actual_mechanical_executor':'parallel_campaign_20261020','scientific_admission':'NOT_ISSUED_BY_THIS_SCRIPT'}
    campaign.write(work/'analysis/SSPRK_MECHANICAL_ANALYSIS.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['all','plan','run','_prepare','_merge','_analyze-v12','_analyze-ssprk'])
    p.add_argument('--input-root',type=Path);p.add_argument('--work-root',type=Path,required=True);p.add_argument('--cargo',default=shutil.which('cargo')or'cargo');p.add_argument('--build-jobs',type=int,default=1);p.add_argument('--max-workers',type=int,default=64);p.add_argument('--memory-limit-mb',type=float);p.add_argument('--nominal-job-memory-mb',type=float,default=512);p.add_argument('--reference-root',type=Path);p.add_argument('--variant',choices=['v12','v13','ssprk']);p.add_argument('--family',choices=['v12','v13_1e-5','v13_1e-4']);a=p.parse_args();work=a.work_root.resolve()
    if a.action=='_prepare':print(json.dumps(prepare_variant(a.input_root,work,a.variant),indent=2));return 0
    if a.action=='_merge':print(json.dumps(merge_family(work,a.family),indent=2));return 0
    if a.action=='_analyze-v12':print(json.dumps(analyze_v12(a.input_root,work),indent=2));return 0
    if a.action=='_analyze-ssprk':print(json.dumps(analyze_ssprk(a.input_root,work),indent=2));return 0
    work.mkdir(parents=True,exist_ok=True);(work/'analysis').mkdir(exist_ok=True)
    path=work/'MANIFEST.json'
    if a.action in('all','plan'):
        if not a.input_root:p.error('--input-root required')
        manifest=make_manifest(a.input_root,work,a.cargo,a.build_jobs,a.reference_root)
        campaign.validate_manifest(manifest)
        if path.exists()and campaign.identity(json.loads(path.read_text()))!=campaign.identity(manifest):raise ValueError('existing manifest identity differs; existing results preserved')
        campaign.write(path,manifest)
        campaign.write(work/'RESOURCE_PREVIEW.json',campaign.resources(a.max_workers,a.memory_limit_mb,a.nominal_job_memory_mb))
    else:manifest=json.loads(path.read_text())
    if a.action=='plan':print(json.dumps({'manifest':str(path),'jobs':len(manifest['jobs']),'scope':manifest['scope'],'timing_inputs':manifest['timing_inputs']},indent=2));return 0
    result=campaign.run(manifest,work/'run',a.max_workers,a.memory_limit_mb,a.nominal_job_memory_mb)
    print(json.dumps({'overall_status':result['overall_status'],'overall_exit_code':result['overall_exit_code'],'receipt':str(work/'run/CAMPAIGN_RECEIPT.json')},indent=2));return result['overall_exit_code']

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,subprocess.CalledProcessError)as exc:print(str(exc),file=sys.stderr);raise SystemExit(1)
