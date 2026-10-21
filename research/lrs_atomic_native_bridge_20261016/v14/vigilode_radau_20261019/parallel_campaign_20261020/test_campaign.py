"""Process orchestration tests; fake children are not physics validation."""
import csv
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
import campaign
import shards

class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.child=self.root/'child.py'
        self.child.write_text('''import json,os,pathlib,subprocess,sys,time
mode,out=sys.argv[1:3]
if mode=='fail':raise SystemExit(7)
if mode=='grandchild':
 subprocess.Popen([sys.executable,'-c',"import pathlib,time;time.sleep(.4);pathlib.Path("+repr(out)+").write_text('survived')"])
 time.sleep(5)
if mode=='slow':time.sleep(.3)
pathlib.Path(out).write_text(json.dumps({'completed':True,'affinity':sorted(os.sched_getaffinity(0))}))
''')
    def tearDown(self):self.temp.cleanup()
    def job(self,name,mode='good',**kw):
        d={'id':name,'argv':[sys.executable,str(self.child),mode,'{attempt}/raw.json'],'identity_files':[str(self.child)],'timeout_s':2,'outputs':[{'path':'raw.json','kind':'json','completed_required':True}]};d.update(kw);return d
    def test_slots_and_resume(self):
        m={'jobs':[self.job('a'),self.job('b')],'aggregate_caps_s':{}}
        result=campaign.run(m,self.root/'run',max_workers=2,nominal_job_mb=32)
        self.assertEqual(result['overall_exit_code'],0)
        cpus=[s['outcome']['assigned_cpus']for s in result['states'].values()]
        self.assertFalse(set(cpus[0])&set(cpus[1]))
        for state in result['states'].values():
            raw=json.loads((Path(state['attempt'])/'raw.json').read_text());self.assertEqual(raw['affinity'],state['outcome']['assigned_cpus'])
        resumed=campaign.run(m,self.root/'run',max_workers=2,nominal_job_mb=32)
        self.assertTrue(all(s['status']=='REUSED_COMPLETED'for s in resumed['states'].values()))
        self.assertEqual(len(list((self.root/'run/jobs').glob('*/attempt_*'))),2)
    def test_failure_blocks_dependency_but_independent_continues(self):
        m={'jobs':[self.job('bad','fail'),self.job('blocked',deps=['bad']),self.job('good')],'aggregate_caps_s':{}}
        r=campaign.run(m,self.root/'run',max_workers=2,nominal_job_mb=32)
        self.assertEqual(r['overall_exit_code'],1);self.assertEqual(r['states']['blocked']['status'],'BLOCKED_DEPENDENCY');self.assertEqual(r['states']['good']['status'],'COMPLETED')
    def test_timeout_kills_process_group(self):
        marker=self.root/'survivor';j=self.job('slow','grandchild',timeout_s=.08,outputs=[]);j['argv'][-1]=str(marker)
        r=campaign.run({'jobs':[j],'aggregate_caps_s':{}},self.root/'run',max_workers=1,nominal_job_mb=32)
        self.assertEqual(r['states']['slow']['outcome']['reason'],'JOB_TIMEOUT')
        time.sleep(.45);self.assertFalse(marker.exists())
    def test_resume_input_mismatch_is_not_reused_or_overwritten(self):
        m={'jobs':[self.job('a')],'aggregate_caps_s':{}}
        first=campaign.run(m,self.root/'run',max_workers=1,nominal_job_mb=32)
        self.child.write_text(self.child.read_text()+'\n# different source\n')
        second=campaign.run(m,self.root/'run',max_workers=1,nominal_job_mb=32)
        self.assertEqual(second['states']['a']['status'],'FAILED_IDENTITY_MISMATCH')
        self.assertTrue((Path(first['states']['a']['attempt'])/'raw.json').exists())
        with self.assertRaisesRegex(ValueError,'MANIFEST_IDENTITY_MISMATCH'):
            campaign.run({'jobs':[self.job('changed')],'aggregate_caps_s':{}},self.root/'run',max_workers=1,nominal_job_mb=32)
    def test_changed_restore_input_blocks_old_completed_dependents(self):
        recipe=self.root/'restore.py';recipe.write_text('# original restore recipe\n')
        prep=self.job('prepare');prep['identity_files'].append(str(recipe))
        m={'jobs':[prep,self.job('dependent',deps=['prepare'])],'aggregate_caps_s':{}}
        first=campaign.run(m,self.root/'run',max_workers=1,nominal_job_mb=32)
        self.assertEqual(first['overall_exit_code'],0)
        recipe.write_text('# changed restoration recipe\n')
        second=campaign.run(m,self.root/'run',max_workers=1,nominal_job_mb=32)
        self.assertEqual(second['states']['prepare']['status'],'FAILED_IDENTITY_MISMATCH')
        self.assertEqual(second['states']['dependent']['status'],'BLOCKED_DEPENDENCY_IDENTITY')
        self.assertEqual(len(list((self.root/'run/jobs').glob('*/attempt_*'))),2)
    def test_aggregate_charges_active_and_preserves_failure_attempts(self):
        m={'jobs':[self.job('a','slow',budget_groups=['g']),self.job('b','slow',budget_groups=['g'])],'aggregate_caps_s':{'g':.12}}
        r=campaign.run(m,self.root/'run',max_workers=2,nominal_job_mb=32,poll_s=.005)
        self.assertEqual(r['overall_exit_code'],1)
        self.assertTrue(any(s.get('outcome',{}).get('reason')=='AGGREGATE_CAP'for s in r['states'].values()))
        resumed=campaign.run(m,self.root/'run',max_workers=2,nominal_job_mb=32)
        self.assertTrue(all(s['status']=='NOT_RUN_AGGREGATE_CAP'for s in resumed['states'].values()))
    def test_missing_or_duplicate_csv_coverage_rejected(self):
        p=self.root/'rows.csv'
        p.write_text('case,n,step,value,dt_s\na,2,1,3,.5\na,2,2,4,.5\n')
        result=campaign.merge_csv([p],self.root/'merged.csv',['case','n'],[('a',2)],lambda _:2,columns=5)
        self.assertEqual(result['rows'],2)
        with self.assertRaisesRegex(ValueError,'missing CSV keys'):campaign.merge_csv([p],self.root/'missing.csv',['case','n'],[('a',2),('b',2)],lambda _:2)
        with self.assertRaisesRegex(ValueError,'duplicate CSV'):campaign.merge_csv([p,p],self.root/'duplicate.csv',['case','n'],[('a',2)],lambda _:2)
    def test_full_v12_merge_shape_and_original_order(self):
        keys=[(c,m,n)for c in shards.CASES for m in shards.MODES12 for n in shards.LEVELS]
        p=self.root/'all.csv';header=['case','mode','n','step']+['v'+str(i)for i in range(42)]
        with p.open('w',newline='')as f:
            w=csv.writer(f);w.writerow(header)
            for c,m,n in reversed(keys):
                for step in range(n,0,-1):w.writerow([c,m,n,step]+['0']*42)
        r=campaign.merge_csv([p],self.root/'merged.csv',['case','mode','n'],keys,lambda key:int(key[2]),46)
        self.assertEqual((r['histories'],r['rows'],r['columns']),(144,12096,46))
        with(self.root/'merged.csv').open()as f:reader=csv.DictReader(f);first=next(reader)
        self.assertEqual((first['case'],first['mode'],first['n'],first['step']),('D1_X1E5','owner_like_be','8','1'))
    def test_memory_estimate_separates_inactive_cache_and_nominal(self):
        cg=self.root/'cg';cg.mkdir();(cg/'cpu.max').write_text('200000 100000');(cg/'memory.max').write_text('1000000000');(cg/'memory.current').write_text('900000000');(cg/'memory.stat').write_text('inactive_file 400000000\nfile 600000000\n')
        p=campaign.resources(64,nominal_job_mb=32,cgroup_root=cg)
        self.assertEqual(p['cpu_budget'],2);self.assertEqual(p['cgroup_remaining_bytes'],100000000)
        self.assertEqual(p['cgroup_remaining_plus_inactive_file_estimate_bytes'],500000000)
        self.assertFalse(p['nominal_memory_is_measured_peak_RSS'])

if __name__=='__main__':unittest.main()
