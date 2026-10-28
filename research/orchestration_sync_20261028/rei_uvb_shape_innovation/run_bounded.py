from pathlib import Path
import argparse,importlib.util,json,resource,sys,time
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--cpu-limit',type=int,required=True);p.add_argument('--wall-limit',type=int,required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
if a.cpu_limit!=10 or a.wall_limit!=30:raise SystemExit('Frozen budgets required')
argv=a.command[1:] if a.command and a.command[0]=='--' else a.command
if not argv or Path(argv[0]).resolve()!=Path(sys.executable).resolve():raise SystemExit('Actual sys.executable required')
spec=importlib.util.spec_from_file_location('bounded_child',U.parents[3]/'helpers/bounded_child.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
config={'argv':argv,'cwd':str(U),'timeout_seconds':a.wall_limit,'cpu_seconds':a.cpu_limit,'address_space_bytes':512*1024**2,'output_prefix':str(U/'outputs/attempt001_RUN')}
(U/'outputs').mkdir(exist_ok=True);ip=U/'outputs/attempt001_RUN_INPUT.json'
if ip.exists():raise SystemExit('Initial run already recorded; no automatic replay')
ip.write_text(json.dumps(config,indent=2)+'\n');start=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF);rc=runner.run(ip);after=resource.getrusage(resource.RUSAGE_SELF)
r=json.loads((U/'outputs/attempt001_RUN.receipt.json').read_text());r['ledger']='NEW_OCT28_ORCHESTRATION_DIAGNOSTIC_NO_OWNER_DEBIT_TRANSFER';r['runner_parent_overhead']={'user_seconds':after.ru_utime-before.ru_utime,'system_seconds':after.ru_stime-before.ru_stime,'wall_minus_child_seconds':time.monotonic()-start-r['wall_seconds'],'reserve_cpu_seconds':1,'reserve_wall_seconds':5,'host_global_overhead':'UNKNOWN_NOT_ZERO'}
(U/'outputs/RUN_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
raise SystemExit(rc)
