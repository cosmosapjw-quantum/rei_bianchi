"""One bounded, zero-IVP check of recovered orchestration; no scientific reruns."""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/'pilot/code/run.py'
STAGE_B=ROOT.parents[2]/'intake/REI_ISOTOPE_QUOTIENT_STAGE_B_20261022.zip'
sys.dont_write_bytecode=True
sys.path.insert(0,str(CODE.parent))
import run


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_tree():
    files=[ROOT/'PHYSICS_CONTRACT.md',ROOT/'INHERITED_PHYSICAL_CONTRACT.md',
           ROOT/'SOURCE_MANIFEST.json',ROOT/'pilot/code/atomic_quotient.py',
           ROOT/'pilot/code/compact_transport.py',ROOT/'pilot/summary.json',
           ROOT/'pilot/summary.csv',ROOT/'review/INDEPENDENT_REVIEW.md']
    for directory in ('pilot/data','pilot/results','pilot/figures','pilot/figures_final'):
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file())
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(files)}


def frozen_ast(source):
    tree=ast.parse(source)
    names={'amplitudes_to_axes','Coupled','case_id','case_configurations',
           'run_case','point_checks','profile','reanalyze_existing_profile'}
    return {n.name:ast.dump(n,include_attributes=False) for n in tree.body
            if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names}


def forbidden(*args,**kwargs):
    raise AssertionError('IVP, worker, or pool entered during completed-work check')


def expect_rejection(call):
    try:call()
    except (RuntimeError,FileNotFoundError,KeyError,ValueError):return True
    raise AssertionError('incomplete/invalid saved evidence was accepted')


def main():
    before=frozen_tree()
    with zipfile.ZipFile(STAGE_B) as archive:
        original=archive.read('research/rei_isotope_quotient_pilot_20261022/pilot/code/run.py').decode()
    assert hashlib.sha256(original.encode()).hexdigest()==\
        '26c8f78d6361654be9c16cc87db540b0b986631a6e4bf75c14b4eed9b3e7e3ba'
    current=CODE.read_text()
    compile(current,str(CODE),'exec')
    assert frozen_ast(current)==frozen_ast(original)
    assert original[:original.index('def amplitudes_to_axes')]==current[:current.index('def amplitudes_to_axes')]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',
             OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    help_result=subprocess.run([sys.executable,str(CODE),'--help'],env=env,
                               capture_output=True,text=True,check=True)
    assert all(token in help_result.stdout for token in ('all','audit-existing','summarize'))
    with patch.object(run,'solve_ivp',side_effect=forbidden), \
         patch.object(run,'run_case',side_effect=forbidden), \
         patch.object(run,'execute_config',side_effect=forbidden), \
         patch.object(run,'ProcessPoolExecutor',side_effect=forbidden):
        completed=run.all_action(4)
        summarized=run.summarize()
        no_stage=run.run_stage([run.case_configurations()[0][7]],4,'controls_stage')
    assert completed['status']==summarized['status']=='COMPLETE_NO_WORK'
    assert completed['new_cases']==summarized['new_cases']==no_stage['new_cases']==0
    assert completed['validated_quotients']==82 and completed['validated_reference']==1
    assert completed['validated_controls']==3
    original_exists=Path.exists
    missing=run.OUT/'quotient_L16_S0_Am0_Ar0.json'
    with patch.object(Path,'exists',lambda p: False if p==missing else original_exists(p)):
        missing_case_rejected=expect_rejection(lambda:run.saved_inventory())
    original_read=Path.read_text
    summary=ROOT/'pilot/summary.json'
    def failed_control(p,*args,**kwargs):
        data=original_read(p,*args,**kwargs)
        if p==summary:
            payload=json.loads(data)
            payload['controls']['quotient_L24_S0_Am0_Ar0']['passed']=False
            return json.dumps(payload)
        return data
    with patch.object(Path,'read_text',failed_control):
        failed_control_rejected=expect_rejection(lambda:run.saved_inventory())
    after=frozen_tree()
    assert before==after
    return dict(status='PASS',ivps=0,point_checks_rerun=0,benchmark_runs=0,
                frozen_ast_equal=True,cli_all_present=True,
                completed_all_no_work=True,summarize_no_write=True,
                stage_no_work_receipt_preserved=True,
                missing_case_rejected=missing_case_rejected,
                failed_control_rejected=failed_control_rejected,
                frozen_file_hashes_before=before,frozen_file_hashes_after=after,
                recovered_runner_sha256=digest(CODE),recovered_runner_bytes=CODE.stat().st_size)


if __name__=='__main__':
    result=main()
    (ROOT/'delivery/RUNTIME_RECOVERY_VERIFICATION.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if not k.startswith('frozen_file_hashes')},indent=2))
