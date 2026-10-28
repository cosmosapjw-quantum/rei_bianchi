"""Prepared single selected worker; NOT_RUN. Root must freeze allowance first."""
import hashlib,json,os,platform,resource,signal,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def metadata(p):
    r=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)),'bytes':len(r),'sha256':hashlib.sha256(r).hexdigest()}


def worker():
    import importlib.util,unittest
    sys.path.insert(0,str(ROOT/'code'))
    import dr_enclosure_cached
    sys.modules['code_dr']=dr_enclosure_cached
    spec=importlib.util.spec_from_file_location('selected_dr_tests',ROOT/'tests/test_dr_enclosure.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(module.SelectedControls))
    print(json.dumps({'scope':'actual three signed DR rows; represented real parameters; conditional loss only',
        'success':result.wasSuccessful(),'methods':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'results':module.SelectedControls.output,
        'arithmetic':{'library':'Python decimal/libmpdec','python':sys.version,
                      'decimal_version':__import__('decimal').__libmpdec_version__,
                      'nominal_precision':60,'oracle_precision':90,'Emin':-999999,'Emax':999999},
        'source':metadata(ROOT/'source/atomic_coefficients.json'),
        'old_suite_IVP_CAS_source_replays':0,'physical_fit_uncertainty':None,
        'actual_recipient_T':None,'L4_ready':False,'stage_admission':'ROOT_REVIEW_REQUIRED'},indent=2))
    return 0 if result.wasSuccessful() else 1



def proc_identity(path='/proc/self/stat'):
    raw=Path(path).read_text(); head,tail=raw.rsplit(') ',1); fields=tail.split()
    return {'host_pid':int(head.split(' (',1)[0]),'host_sid':int(fields[3]),
            'start_ticks':int(fields[19]),'namespace_pid':os.getpid()}


def send_identity(fd):
    info=proc_identity()
    os.write(fd,(json.dumps(info)+'\n').encode());os.close(fd)


def receive_identity(fd,namespace_pid,expected_host_sid=None):
    import select
    ready,_,_=select.select([fd],[],[],2)
    if not ready:
        os.close(fd);return None,'identity_handshake_timeout'
    raw=os.read(fd,4096);os.close(fd)
    try:
        info=json.loads(raw)
        if info['namespace_pid']!=namespace_pid or info['host_pid']<=0 or info['start_ticks']<=0:
            raise ValueError('invalid child identity')
        if expected_host_sid is not None and info['host_sid']!=expected_host_sid:
            raise ValueError('unexpected host session')
        return info,None
    except (ValueError,KeyError,TypeError):
        return None,'identity_handshake_invalid'


def matched_stat(info):
    try:
        raw=Path(f"/proc/{info['host_pid']}/stat").read_text()
    except FileNotFoundError:
        return None
    head,tail=raw.rsplit(') ',1);fields=tail.split()
    if (int(head.split(' (',1)[0])!=info['host_pid'] or int(fields[3])!=info['host_sid']
            or int(fields[19])!=info['start_ticks']):
        raise ValueError('host PID/session/start-time identity mismatch')
    return fields


def main():
    if sys.argv[1:]==['--worker']:
        return worker()
    if sys.argv[1:]!=['--execute-authorized']:
        raise SystemExit('Prepared only; explicit frozen allowance required')
    attempt=ROOT/'execution/attempt_03';attempt.mkdir(parents=True,exist_ok=False)
    files=[ROOT/'THEORY_AND_CONTRACT.md',ROOT/'source/atomic_coefficients.json',
           ROOT/'code/dr_enclosure_cached.py',ROOT/'tests/test_dr_enclosure.py',Path(__file__).resolve()]
    sources=[metadata(p) for p in files]
    argv=[sys.executable,'-B','-S',str(Path(__file__).resolve()),'--worker']
    read_fd,write_fd=os.pipe();expected_sid=proc_identity()['host_sid']
    prefix=time.process_time();start=time.perf_counter();pid=os.fork()
    if pid==0:
        os.close(read_fd)
        send_identity(write_fd)
        os.chdir(ROOT)  # Leaf remains in the outer supervisor's monitored session.
        resource.setrlimit(resource.RLIMIT_CPU,(1,1))
        resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
        for fd,name in [(1,'STDOUT.json'),(2,'STDERR.txt')]:
            f=os.open(attempt/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(f,fd);os.close(f)
        os.execv(argv[0],argv)
    os.close(write_fd)
    host_identity,reason=receive_identity(read_fd,pid,expected_sid)
    ticks=os.sysconf('SC_CLK_TCK')
    while True:
        waited,status,usage=os.wait4(pid,os.WNOHANG)
        if waited:break
        cpu=0
        if reason is None:
            try:
                fields=matched_stat(host_identity)
                if fields is not None:cpu=(int(fields[11])+int(fields[12]))/ticks
            except ValueError:
                reason='host_identity_mismatch'
        if reason is not None or cpu>=.18 or time.perf_counter()-start>=10:
            reason=reason or ('CPU_watchdog' if cpu>=.18 else 'wall_watchdog')
            os.kill(pid,signal.SIGKILL);waited,status,usage=os.wait4(pid,0);break
        time.sleep(.005)
    receipt={'host_identity_handshake':host_identity,'argv':argv,'sources':sources,'exit_code':os.waitstatus_to_exitcode(status),
        'raw_wait_status':status,'watchdog_stop':reason,'CPU_s':usage.ru_utime+usage.ru_stime,
        'user_CPU_s':usage.ru_utime,'system_CPU_s':usage.ru_stime,'wall_s':time.perf_counter()-start,
        'maxrss_KiB_Linux':usage.ru_maxrss,'supervisor_prefix_CPU_s':time.process_time()-prefix,
        'limits':{'CPU_target_s':.2,'CPU_watchdog_threshold_s':.18,'hard_CPU_s':1,'wall_s':10,'memory_bytes':268435456},
        'environment':{'python':sys.version,'platform':platform.platform()},
        'accounting':'wait4 whole worker; supervisor prefix separate; do not add nested counters again',
        'current_budget':'Read root frozen current authority; no old reservation reuse or inferred grant',
        'exclusions':'parent startup/imports/preparation/final receipt/tail/model/network UNKNOWN_NOT_ZERO',
        'stage_admission':'NOT_ISSUED'}
    (attempt/'PROCESS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return 0 if receipt['exit_code']==0 and reason is None else 1


if __name__=='__main__':
    raise SystemExit(main())
