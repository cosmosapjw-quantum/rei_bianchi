#!/usr/bin/env python3
"""Prepare, never execute, the separately reviewable T2 finite native package."""
import argparse,ast,hashlib,json,shutil
from pathlib import Path
UNIT=Path(__file__).resolve().parents[1];REPO=UNIT.parents[1]
T1=REPO/'research/rei_ax11_t1_wave_20261116'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def once(s,old,new):
    assert s.count(old)==1,(old,s.count(old));return s.replace(old,new)

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);out=p.parse_args().output
    assert not out.exists();(out/'harness').mkdir(parents=True);(out/'inputs').mkdir()
    source=T1/'harness/ax11_production_segment.rs';executor=T1/'harness/native_executor.py'
    assert sha(source)=='2bf123ea1a5dd1b82ef62c74e7999f6fad482d834b09890b32afd1bb72ccf1b4'
    assert sha(executor)=='8bb3839fb33faabef2abc5d620fc908bac566f7b47c5cb3852a7c9e105d977c9'
    wrapper=source.read_text();replacements={'T1':'T2','1_800_000':'4_000_000','5_400_000':'12_500_000',
      '43_200_000':'100_000_000','9000.0':'39000.0','2.5e-6':'6.25e-7','1e-4':'1e-10'}
    for old,new in replacements.items():assert old in wrapper;wrapper=wrapper.replace(old,new)
    (out/'harness/ax11_production_segment.rs').write_text(wrapper)
    code=executor.read_text().replace('T1','T2')
    code=code.replace('at256','at16').replace('==256','==16').replace('>256','>16').replace('56+256*','56+16*').replace('full_state_at256','full_state_at16').replace('at128/256','at8/16')
    code=code.replace('T2_ORIGINAL_START','T2_FLOOR_START')
    code=once(code,"[('PLUS',0,'IC',128),('PLUS',1,str(ROOT/'preflight/PLUS_0/checkpoint.txt'),128),('ZERO',0,'IC',256)]", "[('PLUS',0,'IC',8),('PLUS',1,str(ROOT/'preflight/PLUS_0/checkpoint.txt'),8),('ZERO',0,'IC',16)]")
    code=once(code,"(ROOT/'logs').mkdir();(ROOT/'preflight').mkdir();(ROOT/'cases').mkdir();save()", "(ROOT/'logs').mkdir();(ROOT/'preflight').mkdir();(ROOT/'cases').mkdir();save()\n verify_prefixes()")
    code=once(code,"'pool_rule':'Shared13 full starts after3 preflight starts; at most8 percase, exhaustion is censored, never retried'", "'pool_rule':'32 full starts after3 preflight starts; at most16 percase, exhaustion is censored, never retried'")
    code=once(code,"'launch_controller_reservation':{'CPU_s':60,'wall_s':60},'cases':{}", "'launch_controller_reservation':{'CPU_s':60,'wall_s':60},'postprocess_reservation':{'CPU_s':1200,'wall_s':1200},'cases':{}")
    code=once(code,"(C['aggregate_CPU_s']-spent['CPU_s']-60)/2", "(C['aggregate_CPU_s']-spent['CPU_s']-60-1200)/2")
    code=once(code,"(C['aggregate_sum_job_wall_s']-spent['wall_s']-60)/2", "(C['aggregate_sum_job_wall_s']-spent['wall_s']-60-1200)/2")
    code=once(code,"cfg=ROOT/'inputs'/f'{case}_T2_BOUND.cfg'", "caps['output_bytes']=min(C['per_case_output_bytes'],(C['aggregate_scientific_output_bytes']-bytes_in(ROOT/'preflight'))//2)\n  cfg=ROOT/'inputs'/f'{case}_T2_BOUND.cfg'")
    code=once(code,"plan['cases'][case]={'caps':caps,'config_path':str(cfg),'config_sha256':sha(cfg)}", "plan['cases'][case]={'caps':caps,'config_path':str(cfg),'config_sha256':sha(cfg),'prefix':ALLOC['prefixes'][case]}")
    code=once(code,"source=verify_source();binary=source['binary'];assert sha(binary['path'])==binary['sha256']", "source=verify_source();verify_prefixes();binary=source['binary'];assert sha(binary['path'])==binary['sha256']")
    code=once(code,"(ROOT/'cases'/case).mkdir();records=[];previous='IC';used_wall=used_cpu=0.;accepted=0", "(ROOT/'cases'/case).mkdir();records=[];previous=b['prefix']['native_path'];used_wall=used_cpu=0.;accepted=b['prefix']['accepted']")
    code=once(code,"cp=Path(previous);assert sha(cp)==records[-1]['checkpoint_sha256'];assert sha(cp.parent/'source_identity.txt')==source['reused_compiled_library_identity_sha256']\n     assert sha(cp.parent/'config.cfg')==b['config_sha256']", "cp=Path(previous)\n     if records:\n      assert sha(cp)==records[-1]['checkpoint_sha256'];assert sha(cp.parent/'config.cfg')==b['config_sha256']\n     else:assert sha(cp)==b['prefix']['sha256']\n     assert sha(cp.parent/'source_identity.txt')==source['reused_compiled_library_identity_sha256']")
    code=once(code,"if wall<=12 or cpu<=2 or accepted>=caps['accepted']:break", "if wall<=12 or cpu<=2 or accepted>=caps['accepted']:break\n    if caps['output_bytes']-bytes_in(ROOT/'cases'/case)<C['segment_output_MiB']*1024**2:break")
    code=once(code,"assert bytes_in(ROOT/'cases'/case)<=C['per_case_output_bytes']", "assert bytes_in(ROOT/'cases'/case)<=caps['output_bytes']")
    code=once(code,"assert spent['accepted']<=C['aggregate_accepted'] and spent['trials']<=C['aggregate_trials'] and spent['RHS']<=C['aggregate_RHS']", "cumulative={k:spent[k]+sum(p[k] for p in ALLOC['prefixes'].values()) for k in ['accepted','trials','RHS']}\n  LEDGER['cumulative_count_debit_including_reused_prefix']=cumulative\n  assert cumulative['accepted']<=C['aggregate_accepted'] and cumulative['trials']<=C['aggregate_trials'] and cumulative['RHS']<=C['aggregate_RHS']")
    code=once(code,"assert spent['CPU_s']<=C['aggregate_CPU_s'] and spent['wall_s']<=C['aggregate_sum_job_wall_s']", "LEDGER['postprocess_reserved_remaining']={'CPU_s':1200,'wall_s':1200}\n  assert spent['CPU_s']+1200<=C['aggregate_CPU_s'] and spent['wall_s']+1200<=C['aggregate_sum_job_wall_s']")
    prefix_function='''
def verify_prefixes():
 """Original successful full-state prefixes; never overwrite or reset counts."""
 manifest=json.loads((ROOT/'PREFIX_INPUT_MANIFEST.json').read_text())
 for case,files in manifest.items():
  for name,v in files.items():
   p=Path(v['path']);assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],case+':'+name
  reference=Path(ALLOC['prefixes'][case]['native_path']);c=checkpoint(reference)
  assert c['sha256']==ALLOC['prefixes'][case]['sha256']
  assert c['accepted']==4096 and c['trials']==12288 and c['RHS']==85890
  assert c['next_dln_a']>=1e-10
  original=dict(x.split('=',1) for x in (reference.parent/'config.cfg').read_text().splitlines())
  proposed=dict(x.split('=',1) for x in (ROOT/ALLOC['configs'][case]['path']).read_text().splitlines())
  resource_keys={'max_steps','max_attempts','max_rhs','max_wall_s','output_budget_mib'}
  assert {k:v for k,v in original.items() if k not in resource_keys}=={k:v for k,v in proposed.items() if k not in resource_keys}
  # Exact saved state, including all photon bins and cumulative ledger/counts.
  lines=reference.read_text().splitlines();v=list(map(float,lines[1].split()));n=list(map(int,lines[2].split()))
  vals=[v[0],*v[3:10],*map(float,lines[3].split())]
  counts=[n[0],n[1],n[5],n[2],n[3],n[4]];photons=list(map(float,lines[4].split()))
  with (reference.parent/'raw/state_trace.bin').open('rb') as f:
   header=f.read(56);assert header[:8]==b'AX11TRC1'
   _,_,_,size,records,_=struct.unpack('<6Q',header[8:]);assert records==4097
   f.seek(56+4096*size);saved=f.read(size)
  actual=struct.pack('<32d6Q',*vals,*counts)+struct.pack('<'+'d'*len(photons),*photons)
  assert actual==saved,case+' prefix differs from full-state trace'

'''
    code=once(code,'def prepare():',prefix_function+'def prepare():')
    ast.parse(code);(out/'harness/native_executor.py').write_text(code)
    proposal=json.loads((UNIT/'T2_FINITE_PROPOSAL.json').read_text())
    allocation=json.loads((T1/'ALLOCATION.json').read_text())
    allocation.update(schema='rei.ax11.t2-native-allocation.v1',unit='REI_AX11_T2_WAVE_20261116',status='PROPOSED_NOT_AUTHORIZED_NOT_RUN',
      authorization={'status':'PENDING_SEPARATE_FINITE_T2_APPROVAL','prior_T1_scope':'ZERO/PLUS T1 only; unused remainder is not new T2 allowance',
                     'next_command_after_approval':'python3 harness/native_executor.py ABSOLUTE_ISOLATED_ROOT prepare; then inspect preflight and launch within this exact allocation'},
      prior_debit=proposal['prior_known_debits'],prefixes=proposal['prefixes'])
    caps=allocation['caps'];pc=proposal['per_case_caps'];ac=proposal['aggregate_caps']
    caps.update(aggregate_accepted=ac['accepted_cumulative'],aggregate_trials=ac['trials_cumulative'],aggregate_RHS=ac['RHS_cumulative'],
      aggregate_CPU_s=ac['CPU_s'],aggregate_sum_job_wall_s=ac['sum_job_wall_s'],aggregate_scientific_output_bytes=ac['scientific_output_bytes'],backup_copy_reserve_bytes=ac['backup_reserve_bytes'],
      per_case_accepted=pc['accepted_cumulative'],per_case_trials=pc['trials_cumulative'],per_case_RHS=pc['RHS_cumulative'],
      per_case_CPU_s=pc['CPU_s'],per_case_wall_s=pc['wall_s'],per_case_output_bytes=pc['output_bytes'],
      per_case_full_segments=16,all_segment_starts_including_preflight=35,build_starts=1)
    allocation['preflight']={'cases':['PLUS8fromIC','PLUS8fromprevious8','ZERO16fromIC'],'accepted_budget':32,
       'purpose':'T2 entry + full-state restore vs saved exact original T2 trace; later full runs reuse accepted4096 prefixes',
       'debit_rule':'All new preflight work charged; full cumulative counter ceilings also include retained4096 prefixes; prior native CPU remains separately retained'}
    allocation['source']['new_entry_sha256']=sha(out/'harness/ax11_production_segment.rs')
    allocation['source']['existing_T1_binary_reuse']='FORBIDDEN_T1_PHYSICAL_CONFIG_MISMATCH'
    allocation['source']['new_build_required']=True
    allocation['configs']={}
    for case in ['ZERO','PLUS']:
        ref=REPO/f'research/rei_ax11_profile_20261116/prefix_results/native_receipts/{case}_T2_FLOOR_START/config.cfg'
        cfg=dict(line.split('=',1) for line in ref.read_text().splitlines())
        cfg.update(max_steps='4000000',max_attempts='12500000',max_rhs='100000000',max_wall_s='39000')
        target=out/f'inputs/{case}_T2.cfg';target.write_text(''.join(f'{k}={v}\n' for k,v in cfg.items()))
        allocation['configs'][case]={'path':f'inputs/{case}_T2.cfg','sha256':sha(target),'basis_config_sha256':sha(ref),
                                    'changes_from_T2_prefix':'Resource fields only; target6.25e-7, initial step1e-10 and physical IC unchanged'}
    allocation['executor_sha256']=sha(out/'harness/native_executor.py')
    allocation['count_accounting']='Fresh execution debit excludes preexisting prefix cost; finite cumulative count ceilings include both prefixes exactly once. Full histories compose prefix then segments, duplicate boundary once.'
    allocation['postprocess_reservation']={'CPU_s':1200,'wall_s':1200,'within_aggregate_caps':True}
    allocation.pop('guard_cost_risk',None)
    allocation['risk']='T1 factor4 estimate is conditional. First T2 native segment updates costs; caps may censor before endpoint. All raw outputs/cadence and original guards remain unchanged.'
    dump(out/'ALLOCATION.json',allocation)
    shutil.copyfile(UNIT/'receipts/T2_PREFIX_INPUT_MANIFEST.json',out/'PREFIX_INPUT_MANIFEST.json')
    dump(out/'PACKAGE_MANIFEST.json',{'status':'PREPARED_SOURCE_NOT_BUILT_NOT_LAUNCHED','files':{str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in out.rglob('*') if p.is_file()},
      'base_wrapper_sha256':sha(source),'wrapper_text_replacements':replacements,'base_executor_sha256':sha(executor),
      'physical_library_changes':False,'old_binary_incompatible':True,'native_runtime_preflight':'NOT_RUN'})
    print(json.dumps({'package':str(out),'executor_sha256':allocation['executor_sha256'],'entry_sha256':allocation['source']['new_entry_sha256'],'status':'PREPARED_NOT_RUN'}))
if __name__=='__main__':main()
