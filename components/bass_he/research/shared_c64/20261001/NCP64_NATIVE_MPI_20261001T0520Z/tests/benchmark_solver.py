"""Fresh-process solver benchmark; same fixed workload and strict arithmetic."""
import argparse,json,os,resource,subprocess,sys,time,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def child(backend):
    sys.path[:0]=[str(ROOT/'code'),str(ROOT/'reference')]
    if backend=='reference':
        from partialwave_centered import solve
        extra={}
    else:
        from optimized_solver import solve
        extra={'backend':backend}
    t=time.perf_counter();s=solve(2.,m=0,lmax=40,elements=56,degree=4,quadrature=14,rmax=24.,nroots=2,**extra)
    print(json.dumps({'backend':backend,'seconds':time.perf_counter()-t,'energy':s.energy,'residual':s.residual,'rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'stages':s.metadata.get('stage_seconds')}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--child',choices=['reference','native','numpy']);a=ap.parse_args()
    if a.child:return child(a.child)
    records=[];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    for i in range(3):
        for backend in (['reference','native','numpy'] if i%2==0 else ['numpy','native','reference']):
            r=subprocess.run([sys.executable,__file__,'--child',backend],env=env,check=True,capture_output=True,text=True)
            x=json.loads(r.stdout);x['repeat']=i;records.append(x)
    ref=[x for x in records if x['backend']=='reference'];nat=[x for x in records if x['backend']=='native']
    assert max(abs(x['energy']-ref[0]['energy']) for x in records)<2e-10
    assert max(x['residual'] for x in records)<1e-9
    med=lambda xs,k:statistics.median(x[k] for x in xs)
    result={'scope':'fresh-process R2 m0 l40 h56 p4 q14 full solve; 3 alternating repeats; BLAS1 OMP1','records':records,'new_eigenstates':9,'reference_median_seconds':med(ref,'seconds'),'native_median_seconds':med(nat,'seconds'),'speedup':med(ref,'seconds')/med(nat,'seconds'),'reference_median_rss_kib':med(ref,'rss_kib'),'native_median_rss_kib':med(nat,'rss_kib'),'rss_ratio':med(ref,'rss_kib')/med(nat,'rss_kib'),'accuracy_gate':'PASS','performance_gate':'MEASURED_GAIN' if med(ref,'seconds')>med(nat,'seconds') else 'NO_GAIN_NATIVE_OPT_IN_ONLY'}
    result['numpy_median_seconds']=med([x for x in records if x['backend']=='numpy'],'seconds')
    result['numpy_median_rss_kib']=med([x for x in records if x['backend']=='numpy'],'rss_kib')
    result['selected_backend_by_local_median']=min(['reference','native','numpy'],key=lambda b:med([x for x in records if x['backend']==b],'seconds'))
    (ROOT/'evidence/SOLVER_BENCHMARK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
