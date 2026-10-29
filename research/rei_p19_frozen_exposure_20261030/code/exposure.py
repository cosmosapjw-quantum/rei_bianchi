"""Conditional time-sample exposure from immutable PR271 physical event source rows.

DOES NOT calculate a new IVP, physically self-consistent P19 history, observed
optical depth, recombination closure, or certified quadrature error bound.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile
import csv, io, hashlib, json, math

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT/'source_archive/PR271_SOURCE_FULL.zip'
PARENT_SHA = 'c20b7a776e407c35dff99c32595f394ce0c9426c3469358a8b5d7f2750c68165'
DATA_EVENTS = 'results/REI_FROZEN_49_EVENTS_TWO_SCENARIOS.csv'
DATA_EPOCHS = 'results/REI_FROZEN_7_EPOCH_PHYSICAL_SOURCE.csv'
SCENARIOS = ('P19_D1_fiducial','P19_D1_BB13_GLs_nominal')
RATE_KEYS = ('photoelectrons_created_per_Href_s', 'photoheat_eV_per_Href_s',
             'ionization_storage_eV_per_Href_s', 'absorbed_photon_eV_per_Href_s')
QUANTITIES = ('photoelectrons_per_Href','photoheat_eV_per_Href',
              'ionization_storage_eV_per_Href','absorbed_photon_eV_per_Href')

def source_load():
    actual=hashlib.sha256(PARENT.read_bytes()).hexdigest()
    if actual != PARENT_SHA: raise ValueError(f'PARENT_ZIP_SHA_MISMATCH:{actual}')
    with ZipFile(PARENT) as z:
        if z.testzip() is not None: raise ValueError('PARENT_ZIP_CRC_FAIL')
        parent_manifest=json.loads(z.read('MANIFEST.json'))
        for name, meta in parent_manifest['payload'].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=meta['sha256']:
                raise ValueError('PARENT_MANIFEST_MISMATCH:'+name)
        def rows(name):
            return list(csv.DictReader(io.StringIO(z.read(name).decode('utf-8'))))
        return rows(DATA_EVENTS), rows(DATA_EPOCHS)

def logmean(a,b):
    """Exact integral of a exp(log(b/a) s), 0<=s<=1, at binary64 inputs."""
    a=float(a); b=float(b)
    if not (math.isfinite(a) and math.isfinite(b) and a>0 and b>0):
        raise ValueError('BAD_POSITIVE_SOURCE')
    r=math.log(b/a)
    if abs(r)<1e-8: return a*(1+r/2+r*r/6+r*r*r/24+r**4/120)
    return a*(math.expm1(r)/r)

def compute():
    erows,epochs=source_load()
    if len(erows)!=98 or len(epochs)!=14: raise ValueError('BAD_98_EVENT_14_EPOCH_GRAIN')
    event_by=defaultdict(list); epoch_by=defaultdict(list)
    for x in erows: event_by[(x['scenario'],int(x['event_index']))].append(x)
    for x in epochs: epoch_by[x['scenario']].append(x)
    if set(epoch_by)!=set(SCENARIOS) or len(event_by)!=14: raise ValueError('BAD_SOURCE_GROUPS')
    interval_events=[];interval_sums=[];totals=[];cumulative=[];crossovers=[]
    for scenario in SCENARIOS:
        ep=sorted(epoch_by[scenario],key=lambda r:float(r['elapsed_proper_s']))
        if len(ep)!=7 or len({float(x['elapsed_proper_s']) for x in ep})!=7:raise ValueError('BAD_TIME_KNOTS')
        ts=[float(x['elapsed_proper_s']) for x in ep]
        if not all(t2>t1 for t1,t2 in zip(ts,ts[1:])):raise ValueError('NONMONOTONIC_TIME')
        ev={}
        for k in range(1,8):
            rr=sorted(event_by[(scenario,k)],key=lambda r:float(r['elapsed_proper_s']))
            if len(rr)!=7 or any(float(a['elapsed_proper_s'])!=t for a,t in zip(rr,ts)):
                raise ValueError('UNMATCHED_EVENT_TIME')
            ev[k]=rr
        cumulative_state={key:0.0 for key in QUANTITIES}
        cumulative.append(dict(scenario=scenario,time_knot_index=0,
              elapsed_proper_s=ts[0],saved_z=float(ep[0]['saved_z']),
              **{f'loglinear_{key}':0.0 for key in QUANTITIES}))
        for i in range(6):
            t0=ts[i];t1=ts[i+1]; dt=t1-t0
            lsum={key:0.0 for key in QUANTITIES}
            tsum={key:0.0 for key in QUANTITIES}
            for k in range(1,8):
                a=ev[k][i];b=ev[k][i+1]
                vals=[(float(a[key]),float(b[key])) for key in RATE_KEYS]
                lm=[dt*logmean(v0,v1) for v0,v1 in vals[:3]]
                lm.append(lm[1]+lm[2])  # energy-preserving combined source, NOT logmean(Q_abs)
                tr=[dt*(v0+v1)/2 for v0,v1 in vals]
                for j,q in enumerate(QUANTITIES):
                    lsum[q]+=lm[j];tsum[q]+=tr[j]
                # combine only source-separated contributions; avoid double counting
                if abs(lm[2]+lm[1]-lm[3])>2e-14*lm[3]:raise AssertionError('LOGLINEAR_ABS_ENERGY_LEDGER')
                if abs(tr[2]+tr[1]-tr[3])>2e-14*tr[3]:raise AssertionError('TRAPEZOID_ABS_ENERGY_LEDGER')
                interval_events.append(dict(scenario=scenario,interval_index=i,
                     from_saved_z=float(a['saved_z']),to_saved_z=float(b['saved_z']),
                     t_begin_s=t0,t_end_s=t1,dt_s=dt,
                     event_index=k,from_state=a['from_state'],to_state=a['to_state'],
                     channel=a['P19_rate_channel'],
                     **{f'loglinear_{key}':lm[j] for j,key in enumerate(QUANTITIES)},
                     **{f'trapezoid_{key}':tr[j] for j,key in enumerate(QUANTITIES)},
                     per_event_loglinear_v_trapezoid_relative=abs(lm[0]-tr[0])/tr[0]))
            cumulative_state={key:cumulative_state[key]+lsum[key] for key in QUANTITIES}
            interval_sums.append(dict(scenario=scenario,interval_index=i,t_begin_s=t0,t_end_s=t1,
                from_saved_z=float(ep[i]['saved_z']),to_saved_z=float(ep[i+1]['saved_z']),dt_s=dt,
                **{f'loglinear_{key}':lsum[key] for key in QUANTITIES},
                **{f'trapezoid_{key}':tsum[key] for key in QUANTITIES},
                electron_interpolant_sensitivity_frac=(tsum[QUANTITIES[0]]-lsum[QUANTITIES[0]])/tsum[QUANTITIES[0]],
                heating_interpolant_sensitivity_frac=(tsum[QUANTITIES[1]]-lsum[QUANTITIES[1]])/tsum[QUANTITIES[1]]))
            cumulative.append(dict(scenario=scenario,time_knot_index=i+1,elapsed_proper_s=t1,
                saved_z=float(ep[i+1]['saved_z']),
                **{f'loglinear_{key}':cumulative_state[key] for key in QUANTITIES}))
        sums=[r for r in interval_sums if r['scenario']==scenario]
        total={'scenario':scenario,'from_z':float(ep[0]['saved_z']),'to_z':float(ep[-1]['saved_z']),
               't_begin_s':ts[0],'t_end_s':ts[-1],'dt_total_s':ts[-1]-ts[0],
               'source_interpolant':'piecewise loglinear event & heat rate in proper t, hypothesis only'}
        for key in QUANTITIES:
            total['loglinear_'+key]=sum(r['loglinear_'+key] for r in sums)
            total['trapezoid_'+key]=sum(r['trapezoid_'+key] for r in sums)
        total['electron_interpolant_sensitivity_frac']=((total['trapezoid_'+QUANTITIES[0]]-total['loglinear_'+QUANTITIES[0]])/total['trapezoid_'+QUANTITIES[0]])
        total['heat_interpolant_sensitivity_frac']=((total['trapezoid_'+QUANTITIES[1]]-total['loglinear_'+QUANTITIES[1]])/total['trapezoid_'+QUANTITIES[1]])
        totals.append(total)
        # conditional rate dominance crossing: H1 event #1 versus He4 events #6 and #7.
        # note: these sums can come from two exponentials, so *only* endpoints loginterpolated as totals.
        def channel_total(idx, id_list):
            return sum(float(ev[k][idx]['photoelectrons_created_per_Href_s']) for k in id_list)
        for i in range(6):
            h0=channel_total(i,[1]);he0=channel_total(i,[6,7]);h1=channel_total(i+1,[1]);he1=channel_total(i+1,[6,7]);
            l0=math.log(h0/he0); l1=math.log(h1/he1)
            if l0==0 or l1==0 or l0*l1<0:
                frac=0.0 if l0==0 else (1.0 if l1==0 else -l0/(l1-l0))
                tstar=ts[i]+frac*(ts[i+1]-ts[i])
                zstar=float(ep[i]['saved_z'])+frac*(float(ep[i+1]['saved_z'])-float(ep[i]['saved_z']))
                crossovers.append({'scenario':scenario,'between_interval_index':i,
                    'at_mean_z_label_linear_time_proxy':zstar,'at_elapsed_proper_s_proxy':tstar,
                    'bracketed_z':[float(ep[i]['saved_z']),float(ep[i+1]['saved_z'])],
                    'bracketed_t_s':[ts[i],ts[i+1]],
                    'interpolant':'loglinear rates of H1 sum and He4 source sum, mean-z label interpolated; not physical crossover'})
    return dict(interval_events=interval_events,interval_summaries=interval_sums,totals=totals,cumulative=cumulative,crossovers=crossovers)

def savecsv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run():
    d=compute();out=ROOT/'results';out.mkdir(exist_ok=True)
    for key,name in [('interval_events','INTERVAL_84_EVENT_EXPOSURE.csv'),('interval_summaries','INTERVAL_12_SCENARIO_EXPOSURE.csv'),('totals','TOTAL_2_SCENARIO_EXPOSURE.csv'),('cumulative','CUMULATIVE_14_KNOT_EXPOSURE.csv')]:savecsv(out/name,d[key])
    r={'schema':'REI_P19_FROZEN_TIME_EXPOSURE_V1','parent_pr271_zip_sha256':PARENT_SHA,
       'scope':'non-self-consistent frozen snapshot source postprocessing with prescribed positive between-knot interpolants',
       'interval_event_rows':len(d['interval_events']),'interval_summaries':len(d['interval_summaries']),
       'scenario_totals':len(d['totals']),'cumulative_knots':len(d['cumulative']),
       'timelabels':'proper seconds as in frozen original REI saved states; mean z labels only',
       'methods':['piecewise loglinear in event rate and photoheat','piecewise trapezoid in event rate and photoheat'],
       'source_method_crossover':d['crossovers'],
       'scenario_totals':d['totals'],'new_ivps':0,'physical_tau':None,'actual_rei_p19_trajectory':None,
       'interpolant_sensitivity_is_not_error_bound':True,
       'original_DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','delta':0}}
    (out/'RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    return r
if __name__=='__main__': print(json.dumps(run(),indent=2,ensure_ascii=False))
