"""Recipe shape and restore-input identity tests; no native histories."""
import json
from pathlib import Path
import sys,tempfile,unittest
import campaign,campaign_cli

class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name);self.inputs=self.r/'input'
        files={'v12/native_owner/rust/rei_microphysics/Cargo.toml':'base',
            'v13/RESTORE_NATIVE.py':'restore_v13',
            'v13/SOURCE_DELTA.json':json.dumps({'patch_chunks':['source_delta/0.txt']}),
            'v13/source_delta/0.txt':'patch',
            'v14/RESTORE_V14.py':'restore_v14',
            'v14/SOURCE_DELTA.json':json.dumps({'files':{'native_files/add.rs':{}}}),
            'v14/native_files/add.rs':'v14payload',
            'v14/time_centered_ssprk2_20261019/restore_ssprk2_native.py':'restore_ssprk',
            'v14/time_centered_ssprk2_20261019/SOURCE_DELTA_SSPRK2.json':json.dumps({'payload_sha256':{'src/add.rs':'hash'}}),
            'v14/time_centered_ssprk2_20261019/native_files/src/add.rs':'ssprkpayload'}
        for name,data in files.items():p=self.inputs/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
    def tearDown(self):self.temp.cleanup()
    def test_exact_backlog_and_private_target_paths(self):
        m=campaign_cli.make_manifest(self.inputs,self.r/'work',sys.executable,1);campaign.validate_manifest(m)
        self.assertEqual(m['scope'],{'v12_histories':144,'v13_histories':84,'ssprk_transport_rows':52,'ssprk_coupled_histories':16})
        self.assertEqual(len([j for j in m['jobs']if j.get('kind')=='native']),231)
        self.assertEqual(len([j for j in m['jobs']if 'v12'in j.get('budget_groups',[])]),144)
        self.assertEqual(len([j for j in m['jobs']if 'v13_1e-4'in j.get('budget_groups',[])]),42)
        targets=[j['environment']['CARGO_TARGET_DIR']for j in m['jobs']if j['id'].startswith('build_')]
        self.assertEqual(len(set(targets)),3)
        self.assertEqual(m['default_skipped_completed'],['current_Radau19','borrowed_N2','original_V14_84'])
        self.assertEqual(m['aggregate_caps_s'],{'v12':180,'v13_1e-5':180,'v13_1e-4':180,'ssprk':300})
    def test_build_jobs_64_resource_contract_and_65_rejected(self):
        m=campaign_cli.make_manifest(self.inputs,self.r/'work',sys.executable,64)
        campaign.validate_manifest(m)
        builds=[j for j in m['jobs']if j['kind']=='build']
        self.assertEqual(len(builds),6)
        for job in builds:
            self.assertEqual(job['cpu_slots'],64)
            self.assertEqual(job['nominal_memory_mb'],64*1024)
            self.assertEqual(job['argv'][job['argv'].index('-j')+1],'64')
        with self.assertRaisesRegex(ValueError,'1..64'):
            campaign_cli.make_manifest(self.inputs,self.r/'other',sys.executable,65)
    def test_full_restore_closure_is_bound(self):
        paths=campaign_cli.restoration_inputs(self.inputs,'ssprk')
        self.assertEqual(len(paths),9)
        self.assertTrue(any(p.endswith('RESTORE_NATIVE.py')for p in paths))
        self.assertTrue(any(p.endswith('native_files/src/add.rs')for p in paths))
        job={'id':'prepared','argv':[sys.executable], 'identity_files':paths}
        first=campaign.binding(job)
        p=self.inputs/'v14/time_centered_ssprk2_20261019/native_files/src/add.rs';p.write_text('changed_restore_payload')
        self.assertNotEqual(first,campaign.binding(job))
    def test_saved_times_are_last_row_inputs_not_new_execution(self):
        p=self.r/'old.csv';p.write_text('case,mode,n,step,elapsed_wall_s\na,m,2,1,1\na,m,2,2,3\nb,m,4,4,5\n')
        values,summary=campaign_cli.duration_inputs(p,'v12')
        self.assertEqual(values,{('a','m',2):3.,('b','m',4):5.})
        self.assertEqual((summary['W_sum_s'],summary['L_max_s']),(8,5))
        self.assertIn('not an NCP runtime prediction',summary['scope'])

if __name__=='__main__':unittest.main()
