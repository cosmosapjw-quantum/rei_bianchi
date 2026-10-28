#!/usr/bin/env python3
"""One authorized raster-only attempt. Never regenerate scientific vectors."""
import hashlib, json, os, resource, signal, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
INHERITED = 64.980312494
RESERVATION = 1.0
OBSERVED_GUARD = 0.85
TAIL = 0.15
PDF_SHA256 = 'c91b3a8adcb115a103eb37d99e56d2a12466d06198803df1322ff7bab0ca4fa1'

def usage():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'self_user_s': a.ru_utime, 'self_system_s': a.ru_stime,
            'children_user_s': b.ru_utime, 'children_system_s': b.ru_stime}

def seconds(u):
    return sum(u.values())

def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (512*1024**2,512*1024**2))
    signal.signal(signal.SIGPROF, signal.SIG_DFL)
    signal.setitimer(signal.ITIMER_PROF, 0.80)

def main():
    started = time.monotonic()
    initial = usage()
    pdf = ROOT/'figures/scientific_figure_set.pdf'
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == PDF_SHA256
    assert not (OUT/'VISUAL_COMPLETION_STARTED.json').exists(), 'No automatic retry'
    assert not any((ROOT/'figures'/f'preview-{i:02d}.png').exists() for i in range(4,11))
    auth = json.loads((OUT/'VISUAL_COMPLETION_AUTHORIZATION.json').read_text())
    assert auth['status'] == 'OWNER_APPROVED_ROOT_GO'
    cmd = ['/usr/bin/pdftocairo','-f','4','-l','10','-r','72','-png',str(pdf),str(ROOT/'figures/preview')]
    (OUT/'VISUAL_COMPLETION_STARTED.json').write_text(json.dumps({'status':'RUNNING','command':cmd,'initial_usage':initial,'automatic_retry':False},indent=2)+'\n')
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    try:
        p = subprocess.run(cmd, env=env, preexec_fn=child_limits, timeout=30, capture_output=True)
        rc, stdout, stderr = p.returncode, p.stdout.decode(errors='replace'), p.stderr.decode(errors='replace')
    except subprocess.TimeoutExpired as e:
        rc, stdout, stderr = -999, str(e.stdout), str(e.stderr)
    measured = usage()
    # Full process usage includes Python startup; historical costs are never reset.
    observed = seconds(measured)
    outputs = [{'path':str(ROOT/'figures'/f'preview-{i:02d}.png'),'bytes':(ROOT/'figures'/f'preview-{i:02d}.png').stat().st_size} for i in range(4,11) if (ROOT/'figures'/f'preview-{i:02d}.png').exists()]
    status = 'COMPLETED' if rc == 0 and len(outputs)==7 and observed<=OBSERVED_GUARD else 'FAILED_BOUNDED_ATTEMPT'
    receipt = {'schema':'REI_VISUAL_COMPLETION_V1','status':status,'returncode':rc,'command':cmd,'source_pdf_sha256':PDF_SHA256,'usage':measured,'observed_combined_cpu_s':observed,'inherited_charged_known_plus_reserves_cpu_s':INHERITED,'new_total_reservation_cpu_s':RESERVATION,'retained_tail_reserve_cpu_s':TAIL,'unspent_observed_guard_retained_cpu_s':max(0.0,OBSERVED_GUARD-observed),'cumulative_charged_known_plus_reserves_cpu_s':INHERITED+RESERVATION,'approved_consumed_unit_ceiling_cpu_s':66,'original_presentation_policy_cap_restored_cpu_s':30,'temporary_authorization_status':'EXPIRED_AFTER_CONSUMED_UNIT','wall_s':time.monotonic()-started,'outputs':outputs,'stdout':stdout,'stderr':stderr,'new_IVPs':0,'new_physical_samples':0,'automatic_retry':False,'ledger_transfer':False,'ledger_reset':False,'transport_recovery_host_costs':'UNKNOWN_NOT_ZERO','main_cumulative_unchanged_cpu_s':608.750604,'planning_cumulative_unchanged_cpu_s':20.819461885,'visual_admission':'PENDING_PARENT_REVIEW'}
    (OUT/'VISUAL_COMPLETION_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    return 0 if status=='COMPLETED' else 1

if __name__ == '__main__':
    raise SystemExit(main())
