"""One new HE37 source-native model diagnostic and same-kernel measurement.

Reuses saved HE36 CCC rows, never imports or evaluates their old kernel.
Run receipts bind model, script, contract and saved comparison bytes.
"""
from pathlib import Path
import csv, datetime, hashlib, io, json, math, os, platform, resource, sys, time
import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from vendor.lc_ionization import LCModel, sigma_m2, EV_J, KB_J_K, ME_KG, I_J, I_EV

P=Path(__file__).resolve().parent
EXPECTED_PROVIDER='9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16'
EXPECTED_CCC='fcbf67248e5f51af6e3571fcf292ffbaea2ddbe70d825a4f725a1e7ac8c50b88'
CONTRACT={
 'workflow_version':'1.0.0','approval_version':'0.2',
 'source':'Le-Cambier Eq85 semiclassical isotropic ground-H1 heavy-target model',
 'new_grid':'exact saved HE36 129 temperatures,2000..200000K',
 'model_error':'not calibrated; CCC comparison includes threshold/support/kernel differences',
 'new_quadrature':{'variable':'t=(E-I)/(kB*T)','finite_t_support':[0.0,64.0],
                   'positive_GL_candidate_orders':[64,96,128],
                   'max_relative_error_gate':3e-12,'stop_at_first_passing_order':True,
                   'tail_bound':'analytic positive integral bound per moment at t=64'},
 'benchmark':{'workload':'same native source,129 temperatures,4SI Maxwell moments',
              'reference':'positive raw sigma*v*Maxwell GL integration',
              'candidate':'source-native exact analytic moments using expn2',
              'warmup_pairs':2,'alternating_paired_trials':5,'batches_per_trial':64,
              'setup_included':False,'model_runs_not_IVPs':True},
 'no_old_model_evaluations':True,'new_IVP':0,'no_fast_math':True}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,data):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    with temp.open('rb') as f:os.fsync(f.fileno())
    temp.replace(path)
def read_optional(path):
    p=Path(path)
    return p.read_text().strip() if p.exists() else None
def prepare_gl(order):
    q,w=leggauss(order)
    return 32.0*(q+1.0),32.0*w
def raw_gl(temperature,prepared):
    """Direct positive quadrature of E^j sigma(E)*v(E)*Maxwell(E)dE.

    Only GL abscissae/weights are prepared. All T-dependent energies, source
    cross sections and weights are recomputed during every timed call.
    """
    t,w=prepared
    theta=KB_J_K*np.asarray(temperature,dtype=float)
    x=I_J/theta
    energy=I_J+theta[:,None]*t[None,:]
    cross=sigma_m2(energy/EV_J)
    speed=np.sqrt(2.0*energy/ME_KG)
    probability_dt=(2.0/math.sqrt(math.pi))*np.sqrt(x[:,None]+t)*np.exp(-x[:,None]-t)
    base=cross*speed*probability_dt*w
    return np.column_stack([np.sum(base*energy**j,axis=1) for j in range(4)])
def tail_bounds(temperature,L=64.0):
    """Relative omitted-tail upper bounds, independent of GL discretization."""
    x=I_J/(KB_J_K*temperature);decay=math.exp(-L)
    p1=L+1;p2=L*L+2*L+2;p3=L**3+3*L*L+6*L+6
    return np.column_stack(((x+2)*decay,
          np.full_like(x,p1*decay),(x*p1+p2)/(x+2)*decay,
          (x*x*p1+2*x*p2+p3)/(x*x+4*x+6)*decay))

def run():
    output=P/'outputs/DIAGNOSTIC.json'
    if output.exists():raise RuntimeError('Existing completed diagnostic: reuse its receipt; do not replay unchanged work')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    attempt=P/'attempts'/('attempt_'+stamp);attempt.mkdir(parents=True)
    start=time.perf_counter();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    assert sha(P/'vendor/lc_ionization.py')==EXPECTED_PROVIDER
    assert sha(P/'reused/ccc_moments.csv')==EXPECTED_CCC
    save(P/'CONTRACT.json',CONTRACT)
    source=np.genfromtxt(P/'reused/ccc_moments.csv',names=True,delimiter=',')
    temp=source['temperature_K'];assert len(temp)==129 and len(np.unique(temp))==129
    assert temp[0]==2000 and temp[-1]==200000 and temp[64]==20000
    model=LCModel();native=model.evaluate(temp);theta=KB_J_K*temp
    alpha,beta,gamma,delta=native.moments_SI.T
    kappa=native.kappa2_m3_s;lower=4*I_J*beta/(15*theta**2);upper=2*(3*gamma-I_J*beta)/(15*theta**2)
    assert np.all(lower<=kappa) and np.all(kappa<=upper)
    mean=native.conditional_mean_energy_J/EV_J
    assert np.all(mean>=I_EV+theta/EV_J) and np.all(mean<=I_EV+2*theta/EV_J)
    resolution=[];prepared=None;selected_order=None
    for order in CONTRACT['new_quadrature']['positive_GL_candidate_orders']:
        setupstart=time.perf_counter();candidate=prepare_gl(order);setup=time.perf_counter()-setupstart
        values=raw_gl(temp,candidate);rel=np.abs(values/native.moments_SI-1.0)
        row={'order':order,'setup_seconds':setup,'max_relative':float(rel.max()),
             'max_relative_by_moment':rel.max(axis=0).tolist(),'status':'pass' if rel.max()<3e-12 else 'refine'}
        resolution.append(row)
        if row['status']=='pass':prepared=candidate;selected_order=order;break
    save(attempt/'RESOLUTION.json',{'rows':resolution,'gate':3e-12})
    if prepared is None:raise ArithmeticError('No planned GL order attained same-kernel tolerance; preserve and diagnose')
    tails=tail_bounds(temp);assert float(tails.max())<3e-12
    # Both lanes return four SI moments for the same129 temperatures. Native
    # evaluation also creates its documented diagnostics; this overhead stays.
    def analytic():return model.evaluate(temp).moments_SI
    def quadrature():return raw_gl(temp,prepared)
    for unused in range(2):analytic();quadrature()
    pairs=[]
    for trial in range(5):
        order=('analytic','quadrature') if trial%2==0 else ('quadrature','analytic')
        times={}
        for lane in order:
            function=analytic if lane=='analytic' else quadrature
            tick=time.perf_counter_ns()
            for repeat in range(64):last=function()
            seconds=(time.perf_counter_ns()-tick)*1e-9/64
            times[lane]=seconds
            assert np.all(np.isfinite(last)) and last.shape==(129,4)
        pairs.append({'trial':trial+1,'order':list(order),'seconds_per_129T_batch':times,
                      'quadrature_over_analytic':times['quadrature']/times['analytic']})
    ratios=np.array([p['quadrature_over_analytic'] for p in pairs])
    amed=float(np.median([p['seconds_per_129T_batch']['analytic'] for p in pairs]));qmed=float(np.median([p['seconds_per_129T_batch']['quadrature'] for p in pairs]))
    benchmark={'scope':'same native source; analytic moment evaluation vs raw positive GL; local reference measurement',
        'accuracy_gate':3e-12,'chosen_GL_order':selected_order,'setup_costs_separate':resolution,
        'warmup_pairs':2,'paired_trials':5,'batches_per_lane_per_trial':64,'pairs':pairs,
        'median_paired_ratio':float(np.median(ratios)),'paired_ratio_range':[float(ratios.min()),float(ratios.max())],
        'median_analytic_seconds_per_batch':amed,'median_GL_seconds_per_batch':qmed,'ratio_of_medians':qmed/amed,
        'interpretation':'This is not an IVP, network, Fortran, or production throughput claim. Shared-host timing variability is preserved.'}
    save(P/'outputs/BENCHMARK.json',benchmark)
    fields=['temperature_K','alpha_native_m3_s','beta_native_J_m3_s','gamma_native_J2_m3_s','delta_native_J3_m3_s',
        'kappa2_native_m3_s','nu_lower_per_nH_m3_s','nu_upper_per_nH_m3_s','kappa2_over_alpha',
        'nu_lower_over_nH_alpha','nu_upper_over_nH_alpha','incoming_mean_energy_eV','outgoing_returned_energy_eV',
        'net_cooling_energy_eV','alpha_CCC_reused_finite_m3_s','native_over_CCC_rate','CCC_reused_mean_energy_eV',
        'CCC_reused_kappa2_over_alpha','GL_selected_relative_alpha_error','GL_selected_relative_gamma_error']
    rows=[]
    for i,T in enumerate(temp):
        row=[T,alpha[i],beta[i],gamma[i],delta[i],kappa[i],lower[i],upper[i],kappa[i]/alpha[i],
             lower[i]/alpha[i],upper[i]/alpha[i],mean[i],mean[i]-I_EV,I_EV,
             source['alpha_partial_m3_s'][i],alpha[i]/source['alpha_partial_m3_s'][i],
             source['reaction_weighted_mean_energy_eV'][i],source['kappa2_over_alpha'][i],rel[i,0],rel[i,2]]
        rows.append(dict(zip(fields,map(float,row))))
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    writer.writerows([{k:format(v,'.17g') for k,v in row.items()} for row in rows])
    csvpath=P/'outputs/h1_gain_moments.csv';tmppath=csvpath.with_suffix('.csv.tmp');tmppath.write_text(stream.getvalue())
    with tmppath.open('rb') as f:os.fsync(f.fileno())
    tmppath.replace(csvpath)
    save(P/'outputs/h1_gain_moments.json',{'columns':fields,'rows':rows,'model_identity':native.identity})
    cpu=read_optional('/proc/cpuinfo');cpumodel=next((s.split(':',1)[1].strip() for s in cpu.splitlines() if s.startswith('model name')),None) if cpu else None
    env={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,
         'platform':platform.platform(),'cpu_model':cpumodel,'affinity_count':len(os.sched_getaffinity(0)),
         'cpu_max':read_optional('/sys/fs/cgroup/cpu.max'),'memory_max':read_optional('/sys/fs/cgroup/memory.max'),
         'thread_env':{k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')}}
    identity={'script_sha256':sha(__file__),'provider_sha256':EXPECTED_PROVIDER,'provider_identity':native.identity,
              'CCC_saved_csv_sha256':EXPECTED_CCC,'CCC_parent_publication':'6403055c3d574ec0bd1ece80147f9711315902e7',
              'CCC_TICS_sha256':'7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae',
              'contract_sha256':sha(P/'CONTRACT.json')}
    result={'schema':'he37.native_gain_diagnostic.v1','status':'PASS_SCOPED','started_utc':started,
        'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_diagnostic.py',
        'exit_code':0,'identity':identity,'environment':env,'grid_rows':129,'native_threshold_eV':I_EV,
        'CCC_reused_scope':'positive PL finite13.6058..968.61eV; incoming moments only; saved129rows read; no model reevaluation',
        'resolution':resolution,'selected_GL_order':selected_order,'max_GL_relative_error':float(rel.max()),
        'tail_relative_bound_max':float(tails.max()),'tail_bound_by_moment_max':tails.max(axis=0).tolist(),
        'sanity_bounds':{'mean_energy_I_plus_theta_to_I_plus_2theta':True,'positive_angular_bounds_contain_isotropic':True},
        'endpoint_and_center_rows':[rows[i] for i in (0,64,128)],
        'native_over_CCC_rate_range':[float(min(row['native_over_CCC_rate'] for row in rows)),float(max(row['native_over_CCC_rate'] for row in rows))],
        'benchmark_summary':{k:benchmark[k] for k in ('median_paired_ratio','paired_ratio_range','median_analytic_seconds_per_batch','median_GL_seconds_per_batch','ratio_of_medians')},
        'execution_counts':{'new_diagnostic_runs':1,'native_analytic_primary_batches':1,'raw_GL_resolution_batches':len(resolution),
            'native_analytic_warmup_batches':2,'raw_GL_warmup_batches':2,'native_analytic_timed_batches':320,'raw_GL_timed_batches':320,
            'old_CCC_model_evaluations':0,'new_IVP':0,'old_IVP_or_suite_replay':0,'new_benchmark_experiments':1,'render_calls_here':0},
        'elapsed_seconds':time.perf_counter()-start,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'payloads':[{'path':str(q.relative_to(P)),'sha256':sha(q),'bytes':q.stat().st_size} for q in (csvpath,P/'outputs/h1_gain_moments.json',P/'outputs/BENCHMARK.json')]}
    save(output,result);save(attempt/'RESULT.json',result)
    print(json.dumps({'status':result['status'],'selected_GL_order':selected_order,'max_GL_relative_error':float(rel.max()),
        'tail_relative_bound_max':float(tails.max()),'benchmark':result['benchmark_summary'],
        'center':rows[64],'elapsed_seconds':result['elapsed_seconds']}))

if __name__=='__main__':
    try:run()
    except Exception as exc:
        fail={'type':type(exc).__name__,'message':str(exc),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        path=P/'attempts'/('FAILURE_'+str(time.time_ns())+'.json');save(path,fail)
        raise
