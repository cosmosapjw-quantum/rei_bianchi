"""Small invented hosts and Python-only pin/guard checks; no MPI/native build."""
import json,os,subprocess,sys,tempfile,unittest
import launcher
from pathlib import Path
from unittest.mock import patch
from planner import GiB,ancestor_limits,plan,identity
from launcher import mpi_argv,manifest_check,worklist_check


def host(cores=64,threads=1,quota=None,memory=128*GiB):
    cpus=[{'os_cpu':100+i+1000*t,'package':i//32,'core':i%32,'thread_siblings':[100+i+1000*x for x in range(threads)],'numa_nodes':[i//32]} for i in range(cores) for t in range(threads)]
    limits=[] if quota is None else [{'quota':str(quota)}]
    return {'cpus':cpus,'affinity_os_cpus':[x['os_cpu'] for x in cpus],
            'memory_total_bytes':memory,'memory_available_bytes':memory,
            'cgroup':{'ancestors':limits,'errors':[]},'errors':[]}


class HostTests(unittest.TestCase):
    def test_64_physical_reserves_coordinator(self):
        p=plan(host());self.assertEqual((p['rank_count'],p['worker_count']),(64,63))
        self.assertEqual(p['job_memory_budget_bytes'],112*GiB)
        self.assertEqual(p['calibration_total_ranks'],[1,2,4,8,16,32,64])

    def test_32_core_64_thread_distinction(self):
        h=host(32,2)
        self.assertEqual(plan(h)['rank_count'],32)
        self.assertEqual(plan(h,smt=True)['rank_count'],64)
        self.assertEqual(len(set(plan(h)['rank_os_cpus'])),32)

    def test_quota_including_fractional_and_ancestors(self):
        h=host(quota='8');h['cgroup']['ancestors'] += [{'quota':'15/2'}]
        p=plan(h);self.assertEqual((p['rank_count'],p['worker_count']),(7,6))
        self.assertEqual(plan(host(quota='8'))['rank_count'],8)
        self.assertEqual(plan(host(quota='1/2'))['status'],'BLOCKED')

    def test_ancestor_memory_remaining_limits_workers(self):
        h=host();h['cgroup']['ancestors']=[{'memory_limit':64*GiB,'memory_current':4*GiB},{'memory_limit':40*GiB,'memory_current':20*GiB}]
        p=plan(h);self.assertEqual(p['job_memory_budget_bytes'],4*GiB)
        self.assertEqual((p['rank_count'],p['worker_count']),(4,3))

    def test_tiny_host_blocks_default_but_rank1_fallback_explicit(self):
        h=host(1,memory=2*GiB)
        self.assertEqual(plan(h)['status'],'BLOCKED')
        p=plan(h,reserve_bytes=GiB)
        self.assertEqual((p['rank_count'],p['worker_count'],p['coordinator_reserved_ranks']),(1,1,0))

    def test_affinity_subset_counts_only_accessible_physical_cores(self):
        h=host(32,2);h['cpus']=h['cpus'][1::2];h['affinity_os_cpus']=[x['os_cpu'] for x in h['cpus']]
        p=plan(h);self.assertEqual(p['rank_count'],32)
        self.assertTrue(all(x>=1100 for x in p['rank_os_cpus']))
        p=plan(h,requested_ranks=64);self.assertEqual(p['status'],'BLOCKED')

    def test_v2_visible_ancestors(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);leaf=root/'a'/'b';leaf.mkdir(parents=True)
            for p,q,m,c in [(root,'800000 100000',100,20),(root/'a','400000 100000',60,30),(leaf,'max 100000',50,5)]:
                (p/'cpu.max').write_text(q);(p/'memory.max').write_text(str(m));(p/'memory.current').write_text(str(c))
            rows=ancestor_limits(leaf,root,2)
            self.assertEqual(len(rows),3);self.assertEqual(min(int(x['memory_limit'])-x['memory_current'] for x in rows),30)
            self.assertEqual([x['quota'] for x in rows if 'quota'in x],['4','8'])

    def test_v1_visible_ancestors(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);leaf=root/'a';leaf.mkdir()
            for p,q,m in [(root,200000,4*GiB),(leaf,-1,8*GiB)]:
                (p/'cpu.cfs_quota_us').write_text(str(q));(p/'cpu.cfs_period_us').write_text('100000')
                (p/'memory.limit_in_bytes').write_text(str(m));(p/'memory.usage_in_bytes').write_text(str(GiB))
            rows=ancestor_limits(leaf,root,1)
            self.assertEqual([x['quota'] for x in rows if 'quota'in x],['2'])
            self.assertEqual(min(x['memory_limit']-x['memory_current'] for x in rows),3*GiB)

    def test_os_cpu_ids_never_passed_as_hwloc_ids(self):
        p=plan(host());argv=mpi_argv(p,{'mpirun':{'command_path':'/usr/bin/mpirun'}},Path('/x/bin'),Path('/x/manifest'),Path('/x/worklist'),Path('/usr/bin/python3'),Path('/x/out'))
        self.assertNotIn('--cpu-list',argv);self.assertNotIn('--rankfile',argv)
        self.assertIn('localhost:64',argv);self.assertIn('none',argv)
        self.assertEqual(argv[-5:],['/x/bin','/usr/bin/python3',str(Path(__file__).resolve().parents[1]/'executor/worker.py'),'/x/manifest','/x/worklist'])

    def test_manifest_science_memory_and_worklist_refusals(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);mf=base/'m.json';wf=base/'w';p=plan(host())
            m={'schema':'WU088_NCP64_TASK_MANIFEST_V1','scope':'SYNTHETIC_ONLY','output_root':str(base/'new'),'tasks':[{'task_id':'a','cost_hint':0,'limits':{'wall_seconds':10,'address_space_bytes':GiB,'rss_bytes':GiB,'max_output_bytes':1024}}]}
            mf.write_text(json.dumps(m));manifest_check(mf,p);wf.write_text('1\n0 20\n');worklist_check(wf,m)
            wf.write_text('1\n0 19\n')
            with self.assertRaises(ValueError):worklist_check(wf,m)
            m['scope']='ACTUAL_HH';mf.write_text(json.dumps(m))
            with self.assertRaises(ValueError):manifest_check(mf,p)

    def test_rank_guard_actual_os_readback_python_only(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);(base/'bindings').mkdir();cpu=min(os.sched_getaffinity(0))
            p={'status':'PLAN_READY','rank_count':1,'rank_os_cpus':[cpu],'host':{'affinity_os_cpus':[cpu]},'worker_bytes':GiB,'coordinator_bytes':GiB,'file_size_cap_bytes':1024**2,'run_root':d}
            pp=base/'p.json';pp.write_text(json.dumps(p))
            env={**os.environ,'OMPI_COMM_WORLD_RANK':'0','OMPI_COMM_WORLD_SIZE':'1'}
            r=subprocess.run([sys.executable,str(Path(__file__).with_name('rank_guard.py')),'--plan',str(pp),'--',sys.executable,'-I','-c','import os;print(sorted(os.sched_getaffinity(0)))'],env=env,capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout),[cpu])
            self.assertEqual(json.loads((base/'bindings/rank_0.json').read_text())['after'],[cpu])

    def test_fresh_memory_cap_replaces_stale_snapshot(self):
        old=plan(host());fresh=plan(host(memory=96*GiB))
        self.assertEqual(old['rank_count'],fresh['rank_count'])
        result=launcher.refresh_plan(old,fresh)
        self.assertEqual(result['job_memory_budget_bytes'],80*GiB)
        self.assertEqual(result['host']['memory_total_bytes'],96*GiB)

    def test_resume_requires_explicit_flag(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=root/'outputs';out.mkdir();mf=root/'m.json'
            m={'schema':'WU088_NCP64_TASK_MANIFEST_V1','scope':'SYNTHETIC_ONLY','output_root':str(out),'tasks':[{'limits':{'wall_seconds':1,'address_space_bytes':GiB,'rss_bytes':GiB,'max_output_bytes':100}}]}
            mf.write_text(json.dumps(m))
            with self.assertRaises(ValueError):manifest_check(mf,plan(host()))
            self.assertEqual(manifest_check(mf,plan(host()),resume=True),m)

    def test_collector_is_required_for_complete_status(self):
        for count,expected in [(1,'EXECUTION_COMPLETE'),(0,'COLLECTOR_INCONCLUSIVE')]:
            with self.subTest(count=count),tempfile.TemporaryDirectory() as d:
                base=Path(d);ex=base/'executor';ex.mkdir();out=base/'newrun'
                (ex/'prepare.py').write_text('print(\'{"status":"READY"}\')')
                payload={'status':'COLLECTED','declared_task_count':1,'complete_task_count':count,'canonical_payload_digest':'a'*64}
                (ex/'collect.py').write_text('print('+repr(json.dumps(payload))+')')
                p=plan(host(1),reserve_bytes=0);p.update(run_root=str(out),manifest=str(base/'manifest'),file_size_cap_bytes=1024**2,expected_task_count=1)
                # Python test double, not an actual MPI binary or native evaluation.
                script='import json,pathlib;p=json.load(open("HOST_PLAN.json"));json.dump({"rank":0,"after":[p["rank_os_cpus"][0]]},open("bindings/rank_0.json","x"))'
                with patch.object(launcher,'ROOT',base):
                    result=launcher.execute(p,[sys.executable,'-I','-c',script],3)
                self.assertEqual(result['status'],expected)

    def test_real_executor_cli_with_python_dispatch_double(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);backend=launcher.ROOT/'executor/synthetic_backend.py'
            exe=identity(sys.executable);script=identity(backend)
            task={'task_id':'exact_one_third','executable':exe,'inputs':[script],
                  'argv':[exe['path'],'-B',script['path'],'--output','OUTPUT_PATH','--numerator','1','--denominator','3','--sleep-ms','0','--mode','ok','--literal',''],
                  'env':{},'cost_hint':1,'semantic_identity':{'precision':'EXACT_FRACTION'},
                  'limits':{'wall_seconds':3,'address_space_bytes':256<<20,'rss_bytes':128<<20,'poll_ms':20,'max_output_bytes':1<<20}}
            mf=base/'manifest.json';mf.write_text(json.dumps({'schema':'WU088_NCP64_TASK_MANIFEST_V1','scope':'SYNTHETIC_ONLY','output_root':str(base/'tasks'),'tasks':[task]}))
            dispatcher=base/'python_dispatch_double.py'
            dispatcher.write_text('import json,subprocess,sys;p=json.load(open("HOST_PLAN.json"));json.dump({"rank":0,"after":[p["rank_os_cpus"][0]]},open("bindings/rank_0.json","x"));raise SystemExit(subprocess.run([sys.executable,sys.argv[1],"--manifest",sys.argv[2],"--task-index","0"]).returncode)')
            digests=[]
            for attempt in range(2):
                p=plan(host(1),reserve_bytes=0);p.update(run_root=str(base/('host_'+str(attempt))),manifest=str(mf),file_size_cap_bytes=1024**2,expected_task_count=1)
                result=launcher.execute(p,[sys.executable,'-B',str(dispatcher),str(launcher.ROOT/'executor/worker.py'),str(mf)],5)
                self.assertEqual(result['status'],'EXECUTION_COMPLETE',result)
                digests.append(result['collector']['canonical_payload_digest'])
            self.assertEqual(digests[0],digests[1])

    def test_pid_namespace_maps_live_child_and_rss(self):
        child=subprocess.Popen([sys.executable,'-I','-c','import time;x=bytearray(16*1024*1024);print("ready",flush=True);time.sleep(3)'],stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(),'ready')
            table=launcher.process_table()
            self.assertIn(os.getpid(),table)
            self.assertIn(child.pid,table)
            self.assertEqual(table[child.pid]['ppid'],os.getpid())
            self.assertGreater(table[child.pid]['rss'],16*1024*1024)
            self.assertIn(child.pid,launcher.descendants(table,os.getpid()))
        finally:
            child.terminate();child.wait(timeout=5);child.stdout.close()


if __name__=='__main__':unittest.main(verbosity=2)
