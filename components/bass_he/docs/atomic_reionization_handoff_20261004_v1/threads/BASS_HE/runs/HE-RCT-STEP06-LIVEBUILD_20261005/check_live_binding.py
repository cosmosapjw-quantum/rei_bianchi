"""Affected build-context checks. No old scientific suite or ODE solve is replayed."""
from pathlib import Path
from unittest.mock import patch
import argparse
import hashlib
import json
import sys
from make_live_config import ROOT, make_live_contract, verify_sources
import restart
from journal import JournalError

def check(worker: Path, output: Path, metadata: Path) -> dict:
    verify_sources()
    output.mkdir(parents=True, exist_ok=False)
    pin = json.loads((ROOT/'INPUT_PIN.json').read_text())
    md = json.loads(metadata.read_text())
    packages = md['packages']
    expected = {'rei_microphysics':'rei_microphysics','bass_he_rct_step_addon':'addon','bass_he_restart_bridge':'native'}
    assert len(packages) == 3
    for p in packages:
        assert p['name'] in expected and p['source'] is None
        assert Path(p['manifest_path']).resolve() == (ROOT/'staging'/expected[p['name']]/'Cargo.toml').resolve()
    prior = json.loads((ROOT/'inputs/STORED_PREFIXES.json').read_text())
    old_snapshots = json.loads((ROOT/'inputs/OLD_FINAL_SNAPSHOTS.json').read_text())
    results = []
    for label, source, offset in [('OFF','OFF',0.),('ON_Q','KF96',0.),('ON_Qminus1','KF96',-1.),('ON_Qplus1','KF96',1.)]:
        c = make_live_contract(worker, source, offset)
        (output/f'{label}.config.json').write_text(json.dumps(c,indent=2)+'\n')
        directory = output/f'fresh-{label}'
        result = restart.run(worker, directory, c, new=True)
        records = [json.loads(p.read_text()) for p in sorted(directory.glob('checkpoint-*.json'))]
        assert len(records) == 9 and result['snapshot']['status'] == 'COMPLETED'
        assert result['snapshot']['accepted'] == 8 and result['snapshot']['rejected'] == 0
        comparisons = 0
        for new_record, old in zip(records[1:], prior[label]):
            new = new_record['payload']
            be = sum(old['photo'],[]) + old['ci'] + old['rr'] + old['dr']
            pairs = [(new['payload'][:8], old['state']),
                     (new['last']['baseline'], be),
                     (new['last']['rct'], old['rct']),
                     (new['last']['metrics'], [old[k] for k in ('residual','state_estimator','event_estimator_per_h')])]
            for got, ref in pairs:
                assert got == [restart.encode(v) for v in ref], (label,new['accepted'],got,ref)
                comparisons += len(ref)
        old_final = old_snapshots[label]
        assert result['snapshot']['payload'] == old_final['payload']['payload']
        assert result['tip_sha256'] != old_final['sha256'], 'different binding must not be presented as the old chain'
        results.append({'case':label,'accepted_macro_steps':8,'step_scalar_bit_matches':comparisons,
                        'final_accumulator_state_bit_matches':29,'new_binding':result['binding'],
                        'new_tip_sha256':result['tip_sha256'],'old_tip_sha256':old_final['sha256'],
                        'same_numerical_payload':True,'same_hash_chain_claimed':False})
    old_config = json.loads((ROOT/'inputs/OLD_WORKER_CONFIG.json').read_text())
    assert old_config['worker_sha256'] != restart.sha(worker)
    attempted_dir = output/'old-binding-must-not-create'
    with patch('restart.native',side_effect=AssertionError('old checkpoint must not execute native')):
        try:
            restart.run(worker,attempted_dir,old_config)
        except JournalError as error:
            assert str(error)=='WORKER_IDENTITY_CHANGED'
        else:
            raise AssertionError('old worker contract accepted')
    assert not attempted_dir.exists()
    verify_sources()
    summary={'task':'HE-RCT-STEP06-LIVEBUILD','gate':'CURRENT_LIBRARY_LINK_AND_FIXED_API_PARITY_PASS',
             'consumer_commit':pin['consumer_commit'],'consumer_src_tree':pin['consumer_library_src_tree'],
             'source_files':23,'resolved_path_packages':3,'registry_dependencies':0,
             'current_library_built':True,'current_library_all_targets_tested':False,
             'frozen_fixture_cases':4,'native_macro_steps':32,'step_scalar_bit_matches':sum(x['step_scalar_bit_matches'] for x in results),
             'final_state_and_accumulator_matches':116,'native_init_calls_in_this_check':8,
             'old_worker_binding':'REFUSED_BEFORE_NATIVE_AND_DIRECTORY_CREATION',
             'new_checkpoint_chain_not_legacy_chain':True,'same_model_and_numerical_inputs':True,
             'original_rust_and_controller_body_edits':0,'remote_consumer_mutations':0,
             'old_full_scientific_suites_replayed':False,'new_ODE_reference_solves':0,'new_sigkill_tests':0,
             'worker_sha256':restart.sha(worker),'physical_admission':False,'owner_adoption':False,
             'independent_scientific_review':'NOT_RUN','cases':results}
    (output/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--worker',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    a=p.parse_args()
    result=check(a.worker.resolve(),a.output.resolve(),a.metadata.resolve())
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
