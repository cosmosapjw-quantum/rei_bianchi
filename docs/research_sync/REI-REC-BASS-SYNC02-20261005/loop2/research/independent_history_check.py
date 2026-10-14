"""Independent expanding Peebles source+ODE and BASS measure validation."""
from pathlib import Path
import argparse, json, math, hashlib, subprocess, time, csv
import numpy as np
from scipy.integrate import solve_ivp
from decimal import Decimal as D, getcontext
getcontext().prec=60
C=299792458.0; SIGMA=6.6524587e-29; NH0=.2; T0=2.7255; HREF=5e-14; W0=1201.; K=HREF/W0**1.5; TAIL=.2
def physics(z,x):
    w=1+z;h=K*w**1.5;n=NH0*w**3;t=T0*w;tev=8.617343e-5*t
    alpha=4.309e-19*(t/1e4)**(-.6166)/(1+.6703*(t/1e4)**.5300)
    beta=alpha*3.016103031869581e27*tev**1.5*math.exp(-13.598286071938324/4/tev)
    b=math.exp(-10.198714553953742/tev);ra=4.662899067555897e21*h/n/(1-x)
    cf=(8.2206+3*ra)/(8.2206+3*ra+beta)
    return -cf*(n*alpha*x*x-beta*(1-x)*b), h, n
def rhs(z,v):
    dxdt,h,n=physics(z,v[0]);return [-dxdt/((1+z)*h),-C*SIGMA*n*v[0]/((1+z)*h)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(exist_ok=True,parents=True)
    root=Path(__file__).resolve().parents[2]
    sync=json.loads((root/'state/LOOP1_SYNC.json').read_text());assert sync['second_loop_ready'] is True
    con=json.loads((Path(__file__).parent/'PREREGISTRATION.json').read_text());g=con['gates']
    ref=solve_ivp(rhs,(1200.,1000.),[.8,0.],method='DOP853',rtol=2e-12,atol=2e-14,dense_output=True)
    check_count=0;fail=[];runs=[];arrays={};maxima={};negative_controls=[]
    def check(ok,label,detail=None):
        nonlocal check_count
        check_count+=1
        if not bool(ok):fail.append(dict(check=label,detail=detail))
    def bound(value,limit,label):
        maxima[label]=max(maxima.get(label,0.),float(value));check(value<=limit,label,dict(value=float(value),limit=float(limit)))
    check(ref.success,'reference_solver_success',ref.message)
    for n in con['native_integration']['intervals']:
        start=time.monotonic();cmd=[a.native,str(n)];run=subprocess.run(cmd,capture_output=True,text=True,timeout=60);wall=time.monotonic()-start
        (out/f'peebles_{n}.json').write_text(run.stdout);(out/f'peebles_{n}.stderr').write_text(run.stderr)
        check(run.returncode==0,'native_exit',n);d=json.loads(run.stdout);check(d['ok'],'native_ok',n);arrays[n]=d
        z=np.asarray(d['z_edges']);x=np.asarray(d['x_edges']);te=np.asarray(d['time_edges_seconds']);ee=np.asarray(d['eta_edges_seconds']);ce=np.asarray(d['chi_edges_meters']);dt=np.diff(te);de=np.diff(ee)
        check(len(z)==n+1 and len(x)==n+1,'edge_dimensions',n);check(np.all(np.diff(z)<0) and np.all(dt>0) and np.all(de>0),'edge_monotonicity',n)
        check(np.all((x>=0)&(x<1)),'unclipped_state_domain',n)
        w=1+z;exactt=2/(3*K)*(w**(-1.5)-W0**(-1.5));exacte=2/K*(w**(-.5)-W0**(-.5))
        bound(np.max(np.abs(te-exactt))/max(exactt[-1],1.),2e-13,'analytic_normal_time_relative')
        bound(np.max(np.abs(ee-exacte))/max(exacte[-1],1.),2e-13,'analytic_conformal_time_relative')
        bound(np.max(np.abs(ce-C*ee))/max(C*ee[-1],1.),2e-15,'analytic_conformal_length_relative')
        amid=np.asarray(d['a_effective']);bound(np.max(np.abs(amid-dt/de)/(dt/de)),2e-13,'effective_scale_factor')
        zm=np.asarray(d['midpoint_z']);xm=np.asarray(d['midpoint_x']);nm=NH0*(1+zm)**3;nem=nm*xm;q=C*SIGMA*nem
        bound(np.max(np.abs(np.asarray(d['midpoint_nH_m3'])-nm)/nm),3e-12,'proper_nH')
        bound(np.max(np.abs(np.asarray(d['midpoint_ne_m3'])-nem)/nem),3e-12,'electron_density')
        bound(np.max(np.abs(np.asarray(d['interval_rates_s_inverse'])-q)/q),3e-12,'native_density_to_rate')
        if n==con['native_integration']['intervals'][0]:
            correct=float(np.dot(q,dt))
            for label,bad in [('missing_cm3_to_m3',float(np.dot(q*1e-6,dt))),('double_expansion_dilution',float(np.dot(q*(1+zm)**3,dt))),('clock_a_omission',float(np.dot(q,de)))]:
                discrepancy=abs(bad-correct)/correct
                check(discrepancy>g['max_final_tau_error_relative'],'negative_control_detected',label)
                negative_controls.append(dict(name=label,scope='oracle sensitivity to explicit wrong density/clock mapping; production source not mutated',correct_tau=correct,wrong_tau=bad,relative_error=discrepancy,detected=discrepancy>g['max_final_tau_error_relative']))
        # Direct high-precision integration of the same discrete q samples.
        dq=[D(str(v)) for v in d['interval_rates_s_inverse']];edges=[D(str(v)) for v in d['time_edges_seconds']];tau=[D(str(TAIL))]*(n+1)
        for i in range(n-1,-1,-1):tau[i]=tau[i+1]+dq[i]*(edges[i+1]-edges[i])
        st=[(-v).exp() for v in tau];pp=[st[i+1]*(1-(-dq[i]*(edges[i+1]-edges[i])).exp()) for i in range(n)]
        ta=np.asarray(d['optical_depth']);su=np.asarray(d['survival']);pr=np.asarray(d['interval_probability'])
        bound(max(float(abs(D(str(v))-t)) for v,t in zip(ta,tau)),g['normal_eta_chi_max_tau_absolute'],'decimal_discrete_tau_absolute')
        bound(max(float(abs(D(str(v))-t)) for v,t in zip(su,st)),2e-13,'decimal_survival_absolute')
        bound(max(float(abs(D(str(v))-t)) for v,t in zip(pr,pp)),2e-13,'decimal_cell_probability_absolute')
        for prefix in ['eta','chi']:
            bound(np.max(np.abs(np.asarray(d[prefix+'_optical_depth'])-ta)),g['normal_eta_chi_max_tau_absolute'],prefix+'_tau_absolute')
            bound(np.max(np.abs(np.asarray(d[prefix+'_survival'])-su)),2e-13,prefix+'_survival_absolute')
            bound(np.max(np.abs(np.asarray(d[prefix+'_interval_probability'])-pr)),2e-13,prefix+'_probability_absolute')
        mass=abs(math.fsum(d['interval_probability'])+d['survival'][0]-math.exp(-TAIL));bound(mass,g['probability_absolute_mass'],'boundary_mass')
        rx,rt=ref.sol(z);rxerr=float(np.max(np.abs(x-rx)));qt=float(ref.y[1,-1]);tauerr=abs(float(ta[0])-TAIL-qt)/qt
        rta=TAIL+qt-rt;rs=np.exp(-rta);rp=np.diff(rs);p_l1=float(np.sum(np.abs(pr-rp)))
        bound(rxerr,g['max_x_absolute_to_oracle'],'x_max_absolute_to_independent')
        # Finest acceptance is global target; all levels retained for convergence.
        if n==con['native_integration']['intervals'][-1]:
            bound(tauerr,g['max_final_tau_error_relative'],'finest_tau_relative_to_independent');bound(p_l1,g['finest_interval_probability_L1_to_oracle'],'finest_probability_L1')
        check(d['physical_admission'] is False,'physical_claim_ceiling',n)
        runs.append(dict(n=n,wall_seconds=wall,x_final=float(x[-1]),tau_added=float(ta[0]-TAIL),x_max_absolute_error=rxerr,tau_relative_error=tauerr,probability_L1_error=p_l1,mass_residual=mass))
        with (out/f'peebles_{n}.csv').open('w',newline='') as f:
            wr=csv.writer(f);wr.writerow(['z','x_HII','x_reference','t_seconds','eta_seconds','tau','tau_reference','survival','cell_probability'])
            for i in range(n+1):wr.writerow([z[i],x[i],rx[i],te[i],ee[i],ta[i],rta[i],su[i],pr[i] if i<n else ''])
    for l,r in zip(runs,runs[1:]):
        check(r['x_max_absolute_error']<l['x_max_absolute_error'],'x_error_decreases',[l['n'],r['n']])
        ratio=l['tau_relative_error']/r['tau_relative_error'];check(g['observed_tau_error_ratio_range'][0]<=ratio<=g['observed_tau_error_ratio_range'][1],'observed_midpoint_tau_refinement_ratio',ratio)
    constants=[]
    exact_const=2*C*SIGMA*NH0*.8/(3*K)*(W0**1.5-1001.**1.5)
    for n in con['native_integration']['intervals']:
        run=subprocess.run([a.native,str(n),'constant'],capture_output=True,text=True,timeout=30);(out/f'constant_{n}.json').write_text(run.stdout);(out/f'constant_{n}.stderr').write_text(run.stderr);check(run.returncode==0,'constant_native_exit',n);d=json.loads(run.stdout)
        er=abs(d['optical_depth'][0]-TAIL-exact_const)/exact_const;constants.append(dict(n=n,tau_added=d['optical_depth'][0]-TAIL,analytic_tau=exact_const,relative_error=er))
        check(all(v==.8 for v in d['x_edges']),'constant_fixture_not_chemistry',n)
    for l,r in zip(constants,constants[1:]):check(2.5<=l['relative_error']/r['relative_error']<=5.5,'constant_dilution_midpoint_refinement',[l['n'],r['n']])
    bound(constants[-1]['relative_error'],2e-7,'constant_dilution_finest_relative')
    result=dict(status='PASS' if not fail else 'FAIL',checks=check_count,preregistration_sha256=hashlib.sha256((Path(__file__).parent/'PREREGISTRATION.json').read_bytes()).hexdigest(),native_binary_sha256=hashlib.sha256(Path(a.native).read_bytes()).hexdigest(),oracle_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),reference=dict(method='DOP853',nfev=ref.nfev,x_final=float(ref.y[0,-1]),tau_added=float(ref.y[1,-1]),rtol=2e-12,atol=2e-14),histories=runs,constant_x_fixtures=constants,negative_controls=negative_controls,maxima=maxima,failures=fail,claim_ceiling='finite source-bound Peebles expanding benchmark and discrete cold-Thomson mapping; no continuum enclosure or EoR prediction')
    (out/'INDEPENDENT_HISTORY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(bool(fail))
if __name__=='__main__':main()
