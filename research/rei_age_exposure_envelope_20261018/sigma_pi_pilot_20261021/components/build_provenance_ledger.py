#!/usr/bin/env python3
"""Mechanically join recovered and new receipts; no IVP or gate replay."""
import sys,json,csv,math,hashlib,time
ENTRY_STARTED=time.monotonic()
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import unified_pilot as u
WORK=next(p for p in u.ROOT.parents if (p/'recovery_backups/provider_metadata').exists())
OUT=WORK/'rei_unified_20261021'
META=WORK/'recovery_backups/provider_metadata'
AROOT=WORK/'recovery_backups/pr198_extracted/repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021'
KERNEL='3b85dedce84d37b3e165da00685a8a984950aafe'
COSMO=json.loads((u.ROOT/'vendor/REI_BACKGROUND_FAMILY_LOCK.json').read_text())
UNKNOWN='UNRESOLVED_NOT_RECORDED'

def j(path):return json.loads(Path(path).read_text())
def jsonable(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def attrs(path):return {'path':str(path),'size':path.stat().st_size if path.exists() else UNKNOWN}
def common(lane,identifier,parent,kind,z):
    return {'record_kind':kind,'lane':lane,'case_id':identifier,'parent_id':parent,'source_kernel_commit':KERNEL,
      'z_range':z,'cosmology':COSMO['cosmology'],'clock':COSMO['clock'],'metric_signature':'(-,+,+,+)',
      'frame':'comoving orthonormal normal frame; pi_hat=diag(-p,-p,2p)',
      'solver':'DOP853','rtol':3e-11,'atol':3e-13,
      'comparison_relationship':'QUALITATIVE_COMPARISON_ONLY','comparison_case_ids':[],
      'comparison_scope':'A/B differing wrapper and 8 versus40/56 states; compare only after explicit norm/physical-axis mapping',
      'provider_current_archive':'PENDING_ROOT_PUBLICATION_PROVIDER_OVERLAY'}

def amap(record,matter):
    c=record['case'];initial=record['initial'];identity=record['identity'];prefix='A606:' if matter else 'A625:'
    row=common('A',prefix+record['case_id'],None,'numerical_segment',[20,4]);row.update(
      config=identity.get('config',identity.get('configuration',{})),case_config=c,
      executed_wrapper_sha256=identity.get('parent_immutable_files',identity.get('model_files',{})),
      wrapper_publication_identity='PR198 historical source hashes; reviewed_source_b140170ce0c58159368b6b81be49ac35ca764851',
      norms={'Sigma_half':'sqrt(3)*abs(s)/H','Pi_half_signed':'sqrt(3)*(8*pi*G/c^2)*p/H^2','A_to_B_Frobenius':'multiply all signed axes and magnitudes by sqrt(2)'},
      species='reduced common even radiation energy vector; canonical massive Vlasov + cold dust + Lambda',
      state_entries=8,epochs=65,species_IC=initial,realized_axes=initial.get('realized',{'signed_Sigma0':initial['realized_Sigma']*c['eps_sigma'],'signed_Pi_m0':0.,'signed_Pi_r0':initial['realized_signed_Pi']}) if not matter else initial['realized'],
      target_axes={'signed_Sigma0':c.get('signed_Sigma0',c.get('Sigma0',0.)*c.get('eps_sigma',0)),'signed_Pi_m0':c.get('signed_Pi_m0',0.),'signed_Pi_r0':c.get('signed_Pi_r0',c.get('Pi0',0.)*c.get('eps_pi',0))},
      raw_path=str(AROOT/record['raw_path']),raw_sha256=record['raw_sha256'],raw_size=record['raw_size'],
      receipt_path=str(AROOT/record['receipt_path']),receipt_sha256=record['receipt_sha256'],
      status=record['status'],exit=record['exit_status'],review_scope='PR198 PASS_SCOPED_PRELIMINARY z20→4; historical review retained',
      archive_sha256='2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d',
      provider_historical_archive='Drive+Dropbox REI_BIANCHI_MATTER_RADIATION_FINAL_20261021.tar.gz; recovered exact SHA')
    if matter:row['executed_wrapper_sha256']={**row['executed_wrapper_sha256'],'matter_radiation_20261021/component_pilot.py':identity['new_model_sha256']}
    command=AROOT/('matter_radiation_20261021/receipts/new_sweep/command.json' if matter else 'receipts/pilot/command.json')
    row['argv']=j(command).get('argv',UNKNOWN);row['command_receipt_path']=str(command);row['command_receipt_sha256']=u.sha(command)
    return row

def bmap(identifier,c,result,folder,phase,historical=None,controller=None):
    tail=phase=='b2';row=common('B',('Btail:' if tail else 'Bprefix:')+identifier,'Bprefix:'+identifier if tail else None,'numerical_segment',[4,2] if tail else [20,4])
    old=historical is not None;raw=folder/('tail.npz' if tail else 'raw.npz');receipt=folder/'RESULT.json'
    row.update(config=c,executed_wrapper_sha256=historical['executed_wrapper_sha256'] if old else controller['execution_code_identity']['sha256'],
      wrapper_publication_identity='UNPUBLISHED_WITH_SHA256' if old else 'UNIFIED_EXTENSION_EXACT_SOURCE_SHA256_PENDING_PUBLICATION',
      norms={'Sigma_F':'sqrt(6)*abs(s)/H','signed_shear':'sqrt(6)*s/H','P_species':'sqrt(6)*(8*pi*G/c^2)*p_species/H^2','Sigma_half':'Sigma_F/sqrt(2)'},
      species='independent gamma/nu energy+number; common radiation quadrupole, canonical massive Vlasov + cold dust + Lambda',
      species_IC=c['calibration'],target_axes={'Sigma_F_i':c['Sigma_F_i'],'P_m_i':c.get('P_m_i',0.),'P_r_i':c.get('P_r_i',c['Pi_F_signed_i'])},
      realized_axes={k:result.get('initial',{}).get(k,UNKNOWN) for k in ('Sigma_F','P_m','P_r','Pi_F_signed_matter','Pi_F_signed_gamma','Pi_F_signed_nu')},
      initial_observables=result.get('initial',{}),endpoint_observables=result.get('endpoint',{}),
      state_entries=56 if c['guard'] else 40,epochs=33 if tail else 121,combined_epochs=153 if tail else 121,
      raw_path=str(raw),raw_size=historical['raw_size'] if old else raw.stat().st_size if raw.exists() else UNKNOWN,
      raw_sha256=historical['raw_sha256'] if old else result.get('tail_raw_sha256' if tail else 'raw_sha256',UNKNOWN),
      receipt_path=str(receipt),receipt_sha256=historical['receipt_sha256'] if old else u.sha(receipt),
      status=result['status'],exit=result.get('exit',UNKNOWN),argv=controller.get('argv',UNKNOWN) if controller else UNKNOWN,
      review_scope='Original94 PASS_SCOPED_PRELIMINARY z20→4' if old else 'New finite-grid/tail checks; independent result review pending',
      archive_sha256='4699dfe6f559ae4011b7ccfed1936ac35e80163cd54f6bfd9a9853aabd96d6c9' if old else 'PENDING_CURRENT_ARCHIVE',
      provider_historical_archive='Recovered from prior scratch; nested RAW_RESULTS archive SHA verified; now preserved in D0D1 dual-provider archive' if old else 'PENDING_ROOT_PROVIDER_OVERLAY')
    initial=result.get('initial',{})
    row['realized_axes']['P_m']=initial.get('P_m',initial.get('Pi_F_signed_matter',UNKNOWN))
    row['realized_axes']['P_r']=initial.get('P_r',initial['Pi_F_signed_gamma']+initial['Pi_F_signed_nu'] if 'Pi_F_signed_gamma' in initial and 'Pi_F_signed_nu' in initial else UNKNOWN)
    row['realized_axes']['signed_shear']=math.sqrt(6)*initial['s']/initial['H'] if 's' in initial and 'H' in initial else UNKNOWN
    if old:row['D0D1_provider_preservation']={'archive_sha256':'25e1196e3050ae535273f1b88baf99183656bcd0930be49ff9a359e960594abf','archive_bytes':10829091,'drive_id':'1qHeeBL1y1uIbd7vY0pwo8t4asdNI8kbh','dropbox_id':'id:BSpOijBcT10AAAAAAD_gLA','full_readback_receipt':'recovery_backups/checkpoints/D0D1/FULL_READBACK.json','readback_both_HTTP':200}
    row.update(completion_basis=result.get('completion_basis','ORIGINAL_COMPLETED_RECEIPT'),
        historical_execution_status=result.get('historical_execution_status',result['status']),
        recorded_supervisor_exit=result.get('recorded_supervisor_exit',result.get('exit',UNKNOWN)),
        recorded_nfev=result.get('nfev',UNKNOWN),recorded_solver_message=result.get('solver_message',UNKNOWN),
        observed_solver_success=result.get('observed_solver_success',result.get('checks',{}).get('solver_success',UNKNOWN)),
        recovery_execution=result.get('recovery_execution',None),
        historical_failure_receipt_sha256=result.get('historical_failure_receipt_sha256',None),
        historical_failure_receipt_path=result.get('historical_failure_receipt_path',None),
        unavailable_metadata_reason=result.get('unavailable_metadata_reason',None))
    if tail:row.update(combined_raw_path=str(folder/'raw.npz'),combined_raw_sha256=result.get('raw_sha256',UNKNOWN),prefix_provenance=result.get('prefix_provenance',{}),clock={**COSMO['clock'],'a_end':1/3})
    if not old:
        attempt=j(folder/'ATTEMPT.json');row['attempt_receipt']=attempt;row['controller_receipt_path']=str(controller.get('_path',UNKNOWN)) if controller else UNKNOWN
    return row

def main():
    rows=[amap(r,False) for r in j(META/'PR198_625_CASE_RECOVERY.json')]+[amap(r,True) for r in j(META/'PR198_606_CASE_RECOVERY.json')]
    historical=j(META/'LANEB_94_CASE_RECOVERY.json')
    for r in historical:rows.append(bmap(r['case_id'],r['config'],r,u.ROOT/'results/cases'/r['case_id'],'b1',historical=r))
    for phase,relative in [('b1','components/results'),('b2','z2_extension/results')]:
        base=u.ROOT/relative;manifest=j(base/'MANIFEST.json');controllers={p.stem:{**j(p),'_path':str(p)} for p in (base/'controllers').glob('*.json')}
        for c in manifest['cases']:
            if 'reuse' in c:continue
            folder=base/'cases'/c['id'];result=j(folder/'RESULT.json');attempt=j(folder/'ATTEMPT.json');rows.append(bmap(c['id'],c['config'],result,folder,phase,controller=controllers.get(attempt['controller'])))
    original_by_id={r['case_id']:r for r in rows if r['record_kind']=='numerical_segment'}
    for c in u.component_cases():
        if 'reuse' not in c:continue
        r=c['reuse'];parent='Bprefix:'+r['original_case_id'];alias={**original_by_id[parent],'record_kind':'reference_alias','case_id':'Bcomponent_alias:'+c['id'],'parent_id':parent,'reference_relationship':'IDENTICAL_REUSABLE_CASE','alias_config':c['config'],'IVP_count_contribution':0};rows.append(alias)
    reference_file=AROOT/'matter_radiation_20261021/reference_controls.json';references=j(reference_file)
    for r in references['references']:
        parent='A625:'+r['old_case_id'];source=original_by_id[parent]
        if source['raw_sha256']!=r['old_npz_sha256'] or source['receipt_sha256']!=r['old_json_sha256']:raise ValueError('A25_ALIAS_IDENTITY_MISMATCH')
        rows.append({**source,'record_kind':'reference_alias','case_id':'Aneutral_alias:'+r['old_case_id'],'parent_id':parent,'reference_relationship':'IDENTICAL_REUSABLE_CASE','IVP_count_contribution':0,'reference_manifest_sha256':u.sha(reference_file)})
    # Explicitly identify only exact zero target axes, matched physical configuration.
    a_neutral=[r for r in rows if r['record_kind']=='numerical_segment' and r['lane']=='A' and all(v==0 for v in r['target_axes'].values())]
    b_neutral=[r for r in rows if r['record_kind']=='numerical_segment' and r['case_id'].startswith('Bprefix:') and all(v==0 for v in r['target_axes'].values())]
    for a in a_neutral:
        for b in b_neutral:
            for r,other in [(a,b),(b,a)]:
                r['comparison_relationship']='COMPARABLE_AFTER_EXPLICIT_TRANSFORM';r['comparison_case_ids'].append(other['case_id']);r['comparison_scope']='z20→4 zero physical targets; same kernel/cosmology/L8/24×12/Gauss3/fm.1/M30, A half→B Frobenius multiply sqrt2; A8 common energy reduction versus B40 energy+number; distinct execution, no identical reuse'
    from collections import Counter
    counts=Counter((r['record_kind'],r['lane']) for r in rows)
    assert counts[('numerical_segment','A')]==1231 and counts[('numerical_segment','B')]==474
    assert counts[('reference_alias','A')]==25 and counts[('reference_alias','B')]==35
    result={'schema':'rei.case_provenance_ledger.v1','counts':{'A_historical_segments':1231,'B_prefix_segments':237,'B_tail_segments':237,'B_unique_trajectories':237,'B_nominal':231,'B_guards':6,'reference_aliases':60,'numerical_segments':1705,'rows':len(rows)},'source_script_sha256':u.sha(__file__),'notes':['Aliases contribute zero IVPs.','Historical argv absent from B receipts remains UNRESOLVED_NOT_RECORDED.','Current archive/provider and final scientific review overlays belong to root.'],'rows':rows}
    u.atomic_json(OUT/'CASE_PROVENANCE_LEDGER.json',result)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/'CASE_PROVENANCE_LEDGER.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows({k:jsonable(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)
    u.atomic_json(u.ROOT/'z2_extension/results/controllers'/(str(time.time_ns())+'.json'),{'profile':'sandbox','controller_elapsed_s':time.monotonic()-ENTRY_STARTED,'operation':'provenance_ledger','argv':sys.argv,'scientific_solver_calls':0})
    print(json.dumps(result['counts'],indent=2))
if __name__=='__main__':main()
