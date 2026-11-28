"""Artificial file fixtures only; no scientific solver or integral calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

STAGE=Path(__file__).resolve().parents[1]
REAL=STAGE.parent/'BASS_HE_C2D_LARGE_R_SCALED_20261001_v1'
sys.path[:0]=[str(STAGE/'code'),str(REAL/'code')]
import recovery_support as recovery
from mpi_batch import code_identity,json_bytes


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for name in ('code','native','inputs','review','provenance','evidence/FOLLOWUP_MPI'):
            (self.root/name).mkdir(parents=True,exist_ok=True)
        (self.root/'code/task_worker.py').write_text('pass\n')
        (self.root/'code/process_guard.py').write_text('# manufactured guard identity\n')
        (self.root/'native/kernel.f90').write_text('! manufactured fixture\n')
        self.contract={'operational_limits':{'total_active_science_wall_seconds':3600,
          'task_wall_seconds':300,'parity_evaluations_max':4,'overlap_edge_orders_max':240,
          'operator_refinement_tasks_max':16,'new_eigenstates_total_max':84}}
        self.write('CONTRACT.json',self.contract)
        self.tasks=[{'task_id':'done','parameters':{'kind':'overlap','fixture':0}},
                    {'task_id':'interrupted','parameters':{'kind':'overlap','fixture':1}},
                    {'task_id':'unstarted','parameters':{'kind':'parity','fixture':2}}]
        self.manifest={'schema':1,'tasks':self.tasks,'limits':{'per_worker_memory_gib':1.5,'task_wall_seconds':300}}
        self.write('inputs/FOLLOWUP_TASKS.json',self.manifest)
        self.original_code=code_identity(self.root)
        self.batch=self.root/'evidence/FOLLOWUP_MPI'
        self.run={'code':self.original_code,'backend':'native','selected_backend':{'backend':'native','manufactured':True},
                  'manifest_sha256':hashlib.sha256(json_bytes(self.manifest)).hexdigest()}
        self.write('evidence/FOLLOWUP_MPI/MANIFEST_INPUT.json',self.manifest)
        self.write('evidence/FOLLOWUP_MPI/RUN_IDENTITY.json',self.run)
        self.launch={'returncode':124,'timed_out':True,'cleanup_complete':True,'source_unchanged':True,
                     'preflight_passed':True,'wall_cap_seconds':1800,'elapsed_seconds':1800.2,
                     'source_identity_before':self.original_code,'manifest_sha256':self.run['manifest_sha256']}
        self.write('evidence/FOLLOWUP_MPI_LAUNCH.json',self.launch)
        self.make_pass(self.batch,self.tasks[0],self.run)
        (self.batch/'interrupted').mkdir()
        self.write('evidence/FOLLOWUP_MPI/interrupted/TASK_INPUT.json',self.tasks[1])
        with zipfile.ZipFile(self.root/'provenance/FOLLOWUP_CODE_SNAPSHOT.zip','w') as archive:
            for name in self.original_code['files']:archive.write(self.root/name,name)

    def tearDown(self):self.temp.cleanup()

    def write(self,name,value):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(json_bytes(value))

    def make_pass(self,batch,task,run):
        folder=batch/task['task_id'];folder.mkdir(parents=True,exist_ok=True)
        (folder/'TASK_INPUT.json').write_bytes(json_bytes(task))
        data={'task_id':task['task_id'],'parameters':task['parameters'],'new_eigenstates':0,'value':{'fixture':True}}
        (folder/'DATA.json').write_bytes(json_bytes(data))
        result={'status':'PASS','task_id':task['task_id'],'parameters':task['parameters'],
                'input_sha256':recovery.sha(folder/'TASK_INPUT.json'),'code_identity_sha256':run['code']['sha256'],
                'selected_backend':run['selected_backend'],'backend':run['backend'],'new_eigenstates':0,
                'evidence_file':'DATA.json','evidence_bytes':(folder/'DATA.json').stat().st_size,
                'evidence_sha256':recovery.sha(folder/'DATA.json')}
        (folder/'RESULT.json').write_bytes(json_bytes(result))
        execution={'status':'WORKER_RESULT_PASS','returncode':0,'task_id':task['task_id'],
                   'task_sha256':result['input_sha256'],'code_sha256':run['code']['sha256'],
                   'selected_backend':run['selected_backend'],'worker_result_sha256':recovery.sha(folder/'RESULT.json'),
                   'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':recovery.sha(p)} for p in folder.iterdir() if p.is_file()}}
        (folder/'TASK_EXECUTION.json').write_bytes(json_bytes(execution))
        return execution

    def prepare(self):
        index,manifest,plan=recovery.make_recovery_plan(self.root,'evidence/FOLLOWUP_MPI','inputs/RECOVERY_TASKS.json','evidence/RECOVERY_MPI')
        self.write('evidence/FOLLOWUP_MPI/PARTIAL_BATCH_INDEX.json',index)
        self.write('inputs/RECOVERY_TASKS.json',manifest)
        plan=recovery.finalize_plan_source(self.root,plan);self.write('review/RECOVERY_PLAN.json',plan)
        return index,manifest,plan

    def finish_fixture(self):
        index,manifest,plan=self.prepare();batch=self.root/'evidence/RECOVERY_MPI';batch.mkdir()
        run=copy.deepcopy(self.run);run['code']=plan['source_identity_for_recovery'];run['manifest_sha256']=plan['recovery_manifest_sha256']
        self.write('evidence/RECOVERY_MPI/MANIFEST_INPUT.json',manifest);self.write('evidence/RECOVERY_MPI/RUN_IDENTITY.json',run)
        executions=[self.make_pass(batch,t,run) for t in manifest['tasks']]
        self.write('evidence/RECOVERY_MPI/BATCH_SUMMARY.json',{'manifest_sha256':run['manifest_sha256'],'code_sha256':run['code']['sha256'],'tasks':executions})
        launch={'returncode':0,'timed_out':False,'cleanup_complete':True,'source_unchanged':True,'preflight_passed':True,
                'wall_cap_seconds':plan['wall_budget']['recovery_wall_cap_seconds'],'elapsed_seconds':200,
                'source_identity_before':run['code'],'manifest_sha256':run['manifest_sha256']}
        self.write('evidence/RECOVERY_MPI_LAUNCH.json',launch)
        return plan

    def test_partial_sidecar_contains_only_actual_pass(self):
        index,manifest,plan=self.prepare()
        self.assertEqual([r['classification'] for r in index['tasks']],['COMPLETED_VALIDATED','INTERRUPTED_WITHOUT_RESULT','NOT_STARTED'])
        view=recovery.load_partial_batch(self.root,self.batch)
        self.assertEqual(view['tasks'][0]['status'],'WORKER_RESULT_PASS')
        self.assertFalse((self.batch/'BATCH_SUMMARY.json').exists())
        self.assertEqual([t['task_id'] for t in manifest['tasks']],['rec_interrupted','rec_unstarted'])
        self.assertEqual(manifest['tasks'][0]['parameters'],self.tasks[1]['parameters'])
        self.assertEqual(plan['wall_budget']['recovery_wall_cap_seconds'],1769)
        self.assertEqual(plan['predicted_actual_attempts_after_recovery']['overlap'],3)

    def test_result_without_final_pass_blocks_automatic_replay(self):
        self.write('evidence/FOLLOWUP_MPI/interrupted/RESULT.json',{'status':'PASS'})
        with self.assertRaisesRegex(ValueError,'MANUAL_CLASSIFICATION_REQUIRED'):
            self.prepare()

    def test_source_change_blocks_plan(self):
        (self.root/'native/kernel.f90').write_text('! mutated physics\n')
        with self.assertRaisesRegex(ValueError,'FROZEN_SCIENTIFIC_SOURCE_CHANGED'):
            self.prepare()

    def test_non_timeout_or_incomplete_cleanup_rejected(self):
        for field,value in [('timed_out',False),('cleanup_complete',False),('returncode',1),('wall_cap_seconds',1900)]:
            changed=self.launch|{field:value};self.write('evidence/FOLLOWUP_MPI_LAUNCH.json',changed)
            with self.assertRaisesRegex(ValueError,'NOT_ELIGIBLE'):
                recovery.derive_partial_index(self.root,'evidence/FOLLOWUP_MPI')
        self.write('evidence/FOLLOWUP_MPI_LAUNCH.json',self.launch)

    def test_sidecar_rejects_changed_completed_artifact(self):
        self.prepare();(self.batch/'done/DATA.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'ARTIFACT_CHANGED'):
            recovery.load_partial_batch(self.root,self.batch)

    def test_parity_attempt_budget_counts_incomplete_attempts(self):
        counts={'parity':5,'overlap':4}
        with self.assertRaisesRegex(ValueError,'ATTEMPT_BUDGET_EXCEEDED'):
            recovery._budget_check(self.contract,counts)

    def test_successful_fixture_recovery_verifies(self):
        self.finish_fixture()
        result=recovery.verify_recovered(self.root,'review/RECOVERY_PLAN.json')
        self.assertEqual(result['status'],recovery.RECOVERED)
        self.assertEqual(result['completed_task_replays'],0)
        self.assertEqual(result['original_task_count'],3)

    def test_final_verifier_rejects_mapping_duplication(self):
        plan=self.finish_fixture();plan['task_mapping'][1]=copy.deepcopy(plan['task_mapping'][0])
        self.write('review/RECOVERY_PLAN.json',plan)
        with self.assertRaisesRegex(ValueError,'MAPPING_CHANGED'):
            recovery.verify_recovered(self.root,'review/RECOVERY_PLAN.json')

    def test_final_verifier_rejects_total_cap_laundering(self):
        plan=self.finish_fixture();plan['wall_budget']['original_total_seconds']=7200
        self.write('review/RECOVERY_PLAN.json',plan)
        with self.assertRaisesRegex(ValueError,'WALL_PLAN_NOT_ORIGINAL_BUDGET'):
            recovery.verify_recovered(self.root,'review/RECOVERY_PLAN.json')

    def test_prior_wall_copy_must_match_bound_receipt(self):
        plan=self.finish_fixture();plan['prior_attempt_inventory']['launches'][0]['elapsed_seconds']=1
        self.write('review/RECOVERY_PLAN.json',plan)
        with self.assertRaisesRegex(ValueError,'PRIOR_WALL_COPY_DIFFERS'):
            recovery.verify_recovered(self.root,'review/RECOVERY_PLAN.json')

    def killed_fixture(self):
        folder=self.batch/'interrupted'
        owned={'schema':1,'task_id':'interrupted','batch_owner_token':'batch-token',
               'task_owner_token':'task-token','boot_id':'fixture-boot',
               'leader':{'pid':148,'pid_namespace_inode':42,'procfs_pid':100148,'start_time_ticks':5438372}}
        self.write('evidence/FOLLOWUP_MPI/interrupted/OWNED_PROCESS.json',owned)
        for name in ('STDOUT.txt','STDERR.txt'):(folder/name).write_bytes(b'')
        execution={'status':'FAILED','failure_class':'WORKER_NONZERO_EXIT','returncode':-9,
          'task_id':'interrupted','code_sha256':self.run['code']['sha256'],
          'selected_backend':self.run['selected_backend'],
          'task_sha256':recovery.sha(folder/'TASK_INPUT.json'),
          'process_cleanup':{'status':'NO_LIVE_OWNED_MEMBERS'},
          'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':recovery.sha(p)} for p in folder.iterdir()}}
        self.write('evidence/FOLLOWUP_MPI/interrupted/TASK_EXECUTION.json',execution)
        launch=self.launch|{'batch_owner_token':'batch-token','memory_events_delta':{'oom':0,'oom_kill':0},
          'owned_process_cleanup':[{'stage':'tasks_after_term','reports':[{'task_id':'interrupted',
            'status':'NO_LIVE_OWNED_MEMBERS','remaining':[],
            'signals':[{'signal':9,'pid':148,'start_time_ticks':5438372}]}]}]}
        self.write('evidence/FOLLOWUP_MPI_LAUNCH.json',launch)
        index=recovery.derive_partial_index(self.root,'evidence/FOLLOWUP_MPI')
        self.write('evidence/FOLLOWUP_MPI/PARTIAL_BATCH_INDEX.json',index)
        return launch,index

    def test_explicit_owned_timeout_kill_admission_preserves_original_class(self):
        launch,index=self.killed_fixture()
        classification=recovery.timeout_kill_classification(self.root,'evidence/FOLLOWUP_MPI',['interrupted'])
        self.write('review/KILLED.json',classification)
        with self.assertRaisesRegex(ValueError,'MANUAL_CLASSIFICATION_REQUIRED'):
            recovery.make_recovery_plan(self.root,'evidence/FOLLOWUP_MPI','inputs/RECOVERY_TASKS.json','evidence/RECOVERY_MPI')
        new_index,manifest,plan=recovery.make_recovery_plan(self.root,'evidence/FOLLOWUP_MPI','inputs/RECOVERY_TASKS.json',
            'evidence/RECOVERY_MPI',classification_relative='review/KILLED.json')
        self.assertEqual(index,new_index)
        self.assertEqual(new_index['tasks'][1]['classification'],'FINAL_EXECUTION_FAILED_REQUIRES_CLASSIFICATION')
        self.assertEqual([t['task_id'] for t in manifest['tasks']],['rec_interrupted','rec_unstarted'])
        self.assertIsNotNone(plan['timeout_kill_classification'])

    def test_signal_pid_or_start_time_mismatch_is_not_admitted(self):
        launch,index=self.killed_fixture()
        launch['owned_process_cleanup'][0]['reports'][0]['signals'][0]['start_time_ticks']+=1
        self.write('evidence/FOLLOWUP_MPI_LAUNCH.json',launch)
        self.write('evidence/FOLLOWUP_MPI/PARTIAL_BATCH_INDEX.json',recovery.derive_partial_index(self.root,'evidence/FOLLOWUP_MPI'))
        with self.assertRaisesRegex(ValueError,'NO_UNIQUE_BOUND'):
            recovery.timeout_kill_classification(self.root,'evidence/FOLLOWUP_MPI',['interrupted'])

    def test_oom_signal9_cannot_use_timeout_exception(self):
        launch,index=self.killed_fixture();launch['memory_events_delta']['oom_kill']=1
        self.write('evidence/FOLLOWUP_MPI_LAUNCH.json',launch)
        self.write('evidence/FOLLOWUP_MPI/PARTIAL_BATCH_INDEX.json',recovery.derive_partial_index(self.root,'evidence/FOLLOWUP_MPI'))
        with self.assertRaisesRegex(ValueError,'OOM_CAUSE_NOT_EXCLUDED'):
            recovery.timeout_kill_classification(self.root,'evidence/FOLLOWUP_MPI',['interrupted'])


if __name__=='__main__':unittest.main()
