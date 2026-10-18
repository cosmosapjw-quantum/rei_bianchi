"""Bounded synthetic scaling check; no physical files, plotting or solver."""
import array
import json
import platform
import resource
import time
import tracemalloc
from fixtures import case
from pair_diagnostics import diagnose_pair


def main():
    records=[]
    for size in (2000,20000):
        xs=array.array('d',(i/(size-1) for i in range(size)))
        ys=array.array('d',(2*x for x in xs))
        r={'id':'synthetic_reference','series':{'L':xs,'xe':array.array('d',[0])*size}}
        c={'id':'synthetic_candidate','series':{'L':xs,'xe':ys}}
        tracemalloc.start()
        wall,cpu=time.perf_counter(),time.process_time()
        first=diagnose_pair(r,c)
        elapsed,cpu_elapsed=time.perf_counter()-wall,time.process_time()-cpu
        _,peak=tracemalloc.get_traced_memory()
        tracemalloc.stop()
        # Exact replay compares deterministic arithmetic on the same inputs.
        second=diagnose_pair(r,c)
        assert first==second
        row=first['summary'][0]
        assert first['union_knots']==size and first['segments']==size-1
        assert abs(row['l1_integral']-1)<1e-14
        assert abs(row['l2_squared_integral']-4/3)<1e-14
        records.append(dict(knots_per_history=size,observables=1,wall_seconds=elapsed,
                            cpu_seconds=cpu_elapsed,traced_auxiliary_peak_bytes=peak,
                            result=row,deterministic_replay_equal=True))
    # A union/contribution list would grow with these 10x-sized inputs. The
    # bounded slack accounts for interpreter allocation, not scientific error.
    assert records[1]['traced_auxiliary_peak_bytes'] < records[0]['traced_auxiliary_peak_bytes']+32768
    print(json.dumps(dict(scope='BOUNDED_SYNTHETIC_ONLY',python=platform.python_version(),
        records=records,peak_rss_kib_linux=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        physical_history_reads=0,native_solver_runs=0,complexity='O(k*(n+m)) time, O(k) auxiliary memory',
        timing_claim='Observed costs only; no universal timing or rounding guarantee'),indent=2,allow_nan=False))


if __name__=='__main__':main()
