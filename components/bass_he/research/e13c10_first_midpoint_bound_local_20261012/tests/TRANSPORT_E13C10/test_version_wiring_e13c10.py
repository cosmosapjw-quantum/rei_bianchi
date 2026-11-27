#!/usr/bin/env python3
"""One tiny E13C10 delivery-version wiring fixture; no actual predecessor run.

The in-memory dependency pins are replaced ONLY for this test process. The
production source bytes and all fixed production pins remain unchanged. The
fake E13C9 child reports a simulated receipt so new receipt/path wiring can be
checked without restoring the actual 173 MB chain. Never use fixture archives
as research delivery evidence or actual hydration evidence.
"""
import ast
import contextlib
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import zipfile

import restore_transfer_e13c10 as restore
import build_complete_e13c10 as complete
import build_recovery_kit_e13c10 as kit


FAKE_PRIOR_HELPER = '''#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--manifest-sha256',required=True)
p.add_argument('--archive',type=Path,required=True)
p.add_argument('--output-dir',type=Path,required=True)
p.add_argument('--hydrate',action='store_true')
a=p.parse_args()
assert a.hydrate and a.output_dir.name=='E13C9'
assert a.manifest.name=='BASS_HE_E13C9_TRANSFER_MANIFEST.json'
assert a.archive.name=='E13C9_COMPLETE.zip'
assert hashlib.sha256(a.manifest.read_bytes()).hexdigest()==a.manifest_sha256
assert a.archive.read_bytes()==b'E13C9 COMPLETE TINY WIRING FIXTURE ONLY\\n'
a.output_dir.mkdir(parents=True,exist_ok=False)
package=a.output_dir/'package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1'
package.mkdir(parents=True,exist_ok=False)
r={'schema':'bass-he-e13c9-restore-receipt-v1','status':'PASS_COMPLETE_RESTORE',
'FIXTURE_ONLY':True,'scientific_kernel_calls':0,'MPI_invocations':0,
'NCP_execute_invocations':0,'prior_restore_helper_invocations':1,
'automatic_retries':0,'package_directory':str(package.resolve()),
'hydrated_E13C8':{'returncode':0,'FIXTURE_ONLY':'simulated child status; no real E13C8 helper invoked'},
'actual_fake_child_argv':{'manifest':str(a.manifest),'archive':str(a.archive),'output_dir':str(a.output_dir),'hydrate':a.hydrate}}
(a.output_dir/'RESTORE_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\\n')
print('FIXTURE_FAKE_PREDECESSOR_CALLED_ONCE; ACTUAL_PINNED_PREDECESSOR_CALLS=0')
'''


def invoke(module, arguments, output):
    old_argv = sys.argv
    try:
        sys.argv = [str(module.__file__)] + [str(x) for x in arguments]
        with output.with_suffix('.stdout').open('x') as stdout, output.with_suffix('.stderr').open('x') as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = module.main()
        if code != 0:
            raise AssertionError('fixture entry point exit: ' + str(code))
        return code
    finally:
        sys.argv = old_argv


def main():
    started = time.monotonic()
    here = Path(__file__).resolve().parent
    output = here / 'VERSION_WIRING_CONTROL'
    output.mkdir(exist_ok=False)
    checks = []
    def check(name, actual):
        checks.append({'name': name, 'passed': bool(actual)})
        if not actual:
            raise AssertionError(name)
    source_names = ['restore_transfer_e13c10.py', 'build_complete_e13c10.py', 'build_recovery_kit_e13c10.py']
    source_pins = {name: restore.pin(here/name) for name in source_names}
    production_dependency_pins = json.loads(json.dumps(restore.DEPENDENCIES))
    production_prior_pins = json.loads(json.dumps(restore.PRIOR_RECOVERY))
    try:
        prior_manifest = b'{"scope":"E13C9 TINY WIRING FIXTURE ONLY"}\n'
        predecessor = output / 'predecessor_fixture'
        predecessor.mkdir()
        (predecessor/'restore_transfer.py').write_text(FAKE_PRIOR_HELPER)
        (predecessor/'BASS_HE_E13C9_TRANSFER_MANIFEST.json').write_bytes(prior_manifest)
        prior_pins = {name:restore.pin(predecessor/name) for name in ('restore_transfer.py','BASS_HE_E13C9_TRANSFER_MANIFEST.json')}
        restore.save(predecessor/'KIT_MANIFEST.json', {'schema':'bass-he-e13c9-recovery-kit-manifest-v1','files':prior_pins,'FIXTURE_ONLY':True})
        package = output / restore.PACKAGE_ROOT
        (package/'code').mkdir(parents=True)
        (package/'dependencies').mkdir()
        for name in source_names:
            shutil.copyfile(here/name,package/'code'/name)
        (package/'CURRENT_STATE.json').write_text('{"decision":"FIXTURE_ONLY_NOT_SCIENTIFIC_ADMISSION","new_NCP_work_units":[]}\n')
        (package/'NCP_HANDOFF_INTERNAL_KO.md').write_text('TINY DELIVERY WIRING FIXTURE. NO SCIENTIFIC WORK.\n')
        (package/'NEXT_DAG.json').write_text('{"FIXTURE_ONLY":true,"new_heavy_tasks":0}\n')
        (package/'dependencies/E13C9_COMPLETE.zip').write_bytes(b'E13C9 COMPLETE TINY WIRING FIXTURE ONLY\n')
        with zipfile.ZipFile(package/'dependencies/E13C9_RECOVERY_KIT.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(predecessor.iterdir()):
                z.write(path,path.name)
        restore.DEPENDENCIES.clear()
        restore.DEPENDENCIES.update({
            'E13C9_COMPLETE':{'relative_archive':'dependencies/E13C9_COMPLETE.zip',**restore.pin(package/'dependencies/E13C9_COMPLETE.zip')},
            'E13C9_RECOVERY_KIT':{'relative_archive':'dependencies/E13C9_RECOVERY_KIT.zip',**restore.pin(package/'dependencies/E13C9_RECOVERY_KIT.zip')},
        })
        restore.PRIOR_RECOVERY.clear()
        restore.PRIOR_RECOVERY.update({
            'helper':{'relative_path':'restore_transfer.py',**prior_pins['restore_transfer.py']},
            'transfer_manifest':{'relative_path':'BASS_HE_E13C9_TRANSFER_MANIFEST.json',**prior_pins['BASS_HE_E13C9_TRANSFER_MANIFEST.json']},
        })
        delivery = output/'COMPLETE_FIXTURE'
        check('complete_entry_exit_zero',invoke(complete,['--package',package,'--output-dir',delivery,'--stamp','20261012T000000Z'],output/'COMPLETE_ENTRY')==0)
        build=restore.load_json((delivery/'BUILD_RECEIPT.json').read_bytes())
        transfer_path=delivery/'BASS_HE_E13C10_TRANSFER_MANIFEST.json'
        transfer=restore.load_json(transfer_path.read_bytes())
        check('new_package_and_transfer_names',transfer['schema']=='bass-he-e13c10-transfer-manifest-v1' and transfer['restore_helper']['relative_path']=='restore_transfer_e13c10.py')
        check('predecessor_E13C9_pins_are_wired',transfer['dependencies']==restore.DEPENDENCIES and transfer['prior_recovery']==restore.PRIOR_RECOVERY)
        archive=Path(build['archive_path'])
        check('fixture_archive_is_small',archive.stat().st_size<128*1024)
        restored=output/'RESTORE_FIXTURE'
        check('restore_entry_exit_zero',invoke(restore,['--manifest',transfer_path,'--manifest-sha256',restore.sha(transfer_path),'--archive',archive,'--output-dir',restored,'--hydrate'],output/'RESTORE_ENTRY')==0)
        receipt=restore.load_json((restored/'RESTORE_RECEIPT.json').read_bytes())
        nested=receipt['hydrated_E13C9']
        check('new_receipt_and_nested_return',receipt['schema']=='bass-he-e13c10-restore-receipt-v1' and nested['returncode']==0)
        check('nested_output_path',Path(nested['package_directory']).relative_to(restored).as_posix()=='runtime/E13C9/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1')
        check('new_legacy_receipt_key',nested['prior_hydrated_E13C8']['returncode']==0)
        check('one_fake_predecessor_invocation',receipt['prior_restore_helper_invocations']==1)
        check('no_scientific_or_NCP_invocation',all(receipt[k]==0 for k in ('scientific_kernel_calls','MPI_invocations','NCP_execute_invocations','automatic_retries')))
        locations=output/'FIXTURE_LOCATIONS.json'
        restore.save(locations,{'FIXTURE_ONLY':True,'archive':transfer['archive'],'parts':transfer['parts']})
        scope=output/'FIXTURE_SCOPE.txt'
        scope.write_text('FIXTURE ONLY: no actual E13C9 restoration, no actual upload.\n')
        kit_output=output/'KIT_FIXTURE'
        check('kit_entry_exit_zero',invoke(kit,['--package',package,'--delivery-dir',delivery,'--output-dir',kit_output,'--stamp','20261012T000000Z','--backup-locations',locations,'--restore-output',restored,'--extra-file','controls/FIXTURE_SCOPE.txt='+str(scope)],output/'KIT_ENTRY')==0)
        kit_receipt=restore.load_json((kit_output/'RECOVERY_KIT_BUILD_RECEIPT.json').read_bytes())
        kit_archive=Path(kit_receipt['archive']['path'])
        with zipfile.ZipFile(kit_archive) as z:
            km=restore.load_json(z.read('KIT_MANIFEST.json'))
            check('kit_schema_and_helper_wired',km['schema']=='bass-he-e13c10-recovery-kit-manifest-v1' and 'restore_transfer_e13c10.py' in km['files'])
            check('kit_transfer_pin',km['external_transfer_manifest_sha256']==restore.sha(transfer_path))
            check('kit_receipt_and_optional_evidence',all(name in km['files'] for name in ('ACTUAL_RESTORE_RECEIPT.json','BACKUP_LOCATIONS.json','controls/FIXTURE_SCOPE.txt')))
        old_tree=ast.parse((here.parent/'recovery_kit/restore_transfer.py').read_text())
        new_tree=ast.parse((here/'restore_transfer_e13c10.py').read_text())
        def functions(tree):
            return {x.name:ast.dump(x,include_attributes=False) for x in tree.body if isinstance(x,ast.FunctionDef)}
        old_functions,new_functions=functions(old_tree),functions(new_tree)
        unchanged=[name for name in old_functions if old_functions[name]==new_functions[name]]
        check('unchanged_transport_security_functions',set(old_functions)-set(unchanged)=={'main','validate_transfer'})
        check('production_tool_bytes_unchanged',all(restore.pin(here/name)==identity for name,identity in source_pins.items()))
        report={'schema':'bass-he-e13c10-version-wiring-control-v1','status':'PASS_TINY_FIXTURE_ONLY',
            'scope':'Modified E13C10/E13C9 names, pins, nested paths, receipt keys, and kit assembly; fake predecessor pins only in test memory.',
            'checks':checks,'checks_passed':len(checks),'checks_failed':0,
            'source_pins':source_pins,'unchanged_restore_functions':unchanged,
            'production_dependency_pins_unchanged_on_disk':production_dependency_pins,
            'production_prior_pins_unchanged_on_disk':production_prior_pins,
            'tiny_complete_archive':restore.pin(archive),'tiny_kit_archive':restore.pin(kit_archive),
            'actual_large_complete_builds':0,'actual_pinned_predecessor_invocations':0,
            'fake_predecessor_subprocess_invocations':1,'fixture_complete_builder_invocations':1,
            'fixture_new_restore_invocations':1,'fixture_kit_builder_invocations':1,
            'scientific_kernel_calls':0,'MPI_invocations':0,'NCP_execute_invocations':0,'external_mutations':0,
            'automatic_retries':0,'elapsed_seconds':time.monotonic()-started,
            'admission':'This is not production restore evidence and not scientific admission.'}
        restore.save(output/'VERSION_WIRING_CONTROL_RECEIPT.json',report)
        print(json.dumps({'status':report['status'],'checks':len(checks),'elapsed_seconds':report['elapsed_seconds'],'receipt':str(output/'VERSION_WIRING_CONTROL_RECEIPT.json')}))
    except BaseException as error:
        restore.save(output/'FIRST_FAILURE.json',{'status':'FIXTURE_FAILURE_PRESERVED','error_type':type(error).__name__,'error':str(error),'checks':checks,'automatic_retries':0})
        raise
    finally:
        restore.DEPENDENCIES.clear()
        restore.DEPENDENCIES.update(production_dependency_pins)
        restore.PRIOR_RECOVERY.clear()
        restore.PRIOR_RECOVERY.update(production_prior_pins)


if __name__=='__main__':
    main()
