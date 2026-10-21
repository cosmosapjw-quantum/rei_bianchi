"""Stored-output diagnostics only. No native solver or frozen-study execution."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import sys
from fractions import Fraction as F
from decimal import Decimal, localcontext

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(TASK/'src'))
from compare_results import endpoint_metrics, match_observations, relative
from photon_ledger_diagnosis import budget, residual_fraction, fraction_record, display_fraction, finite, diagnose


def read(p):
    return json.loads(Path(p).read_text())


def exact(v):
    return F.from_float(finite(v))


def rec(v):
    return dict(exact_fraction=fraction_record(v), decimal80=display_fraction(v))


def initial_contract(data, setup):
    """Bind initial zeros to an executed source receipt, never arbitrary data."""
    receipt_path = data.parent/'RECEIPT.json'
    if not receipt_path.is_file():
        raise ValueError('INCOMPLETE_INITIAL_SOURCE_RECEIPT')
    receipt = read(receipt_path)
    candidates = [data.parent/'reference_solver_diagnostics.py', TASK/'donors/pr171/positive_solver.py']
    identity = receipt.get('identity', {})
    for path in candidates:
        if not path.is_file():
            continue
        content = path.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        if sha not in [identity.get('solver_sha'), identity.get('computational_base_solver_sha')]:
            continue
        text = content.decode()
        if ("y=np.zeros(size);y[:4]=setup['initial'];active=0;start=setup['x0']" in text
                and len(setup.get('initial', [])) == 4 and setup.get('extra', 0) >= 7):
            return dict(status='VERIFIED', N_initial=0, photo_initial=[0,0,0],
                        source=str(path), source_sha256=sha, receipt=str(receipt_path),
                        basis='Executed/base source hash matches receipt; zero-initialized full state, only four gas coordinates set; active=0.')
    raise ValueError('INCOMPLETE_INITIAL_ZERO_PROVENANCE')


def photon_history(data, provenance=None):
    data = Path(data)
    if not (data/'source_jumps.json').is_file():
        return dict(status='INCOMPLETE', reason='MISSING_EXPLICIT_SOURCE_EVENTS',
                    legacy_observation_diagnosis=diagnose(data), telescope=None)
    try:
        setup, endpoint = read(data/'setup.json'), read(data/'endpoint.json')
        initial = provenance or initial_contract(data, setup)
        if initial.get('status') != 'VERIFIED' or initial.get('N_initial') != 0 or initial.get('photo_initial') != [0,0,0]:
            raise ValueError('INVALID_INITIAL_ZERO_CONTRACT')
        births, sources = setup['births'], setup['source_inventory']
        B = setup['birth_count']
        if not isinstance(B,int) or B != len(births) or B != len(sources):
            raise ValueError('INVALID_BIRTH_INVENTORY')
        for x in births:
            finite(x)
        if any(a >= b for a,b in zip(births,births[1:])):
            raise ValueError('INVALID_BIRTH_CLOCK_ORDER')
        source_values = [finite(row[0]) for row in sources]
        events = read(data/'source_jumps.json')
        rows = events.get('records', [])
        if len(rows) != B:
            raise ValueError('INCOMPLETE_SOURCE_EVENT_COUNT')
        if len(set(r.get('event') for r in rows)) != B:
            raise ValueError('INVALID_DUPLICATE_SOURCE_EVENT')
        if [r.get('event') for r in rows] != list(range(B)):
            raise ValueError('INVALID_SOURCE_EVENT_ORDER')
        intervals_path = data/'solver_return.json'
        intervals = read(intervals_path).get('intervals', []) if intervals_path.is_file() else []
        by_event = {}
        for row in intervals:
            event = row.get('event')
            if event in by_event:
                raise ValueError('INVALID_DUPLICATE_INTERVAL_EVENT')
            by_event[event] = row
        previous = F(0)
        continuous, jumps, history = [], [], []
        cum_c, cum_j = F(0), F(0)
        crosschecks = []
        for j, row in enumerate(rows):
            if row.get('status') != 'AVAILABLE' or row.get('active_before') != j or row.get('active_after') != j+1:
                raise ValueError('INVALID_SOURCE_EVENT_ACTIVE_OR_STATUS')
            if finite(row['x']) != finite(births[j]):
                raise ValueError('INVALID_SOURCE_EVENT_CLOCK')
            if row.get('source_inventory') != sources[j]:
                raise ValueError('INVALID_SOURCE_EVENT_INVENTORY')
            pre, post = row['pre'], row['post']
            im = residual_fraction(budget(pre['N'], pre['ledgers'][4:7], source_values[:j]))
            ip = residual_fraction(budget(post['N'], post['ledgers'][4:7], source_values[:j+1]))
            c, jump = im-previous, ip-im
            continuous.append(c);jumps.append(jump)
            cum_c += c;cum_j += jump
            check = dict(event=j, status='MISSING_CROSSCHECK', missing=[])
            interval = by_event.get(j)
            coordinates = data/f'accepted_coordinates_event{j}.npy'
            if interval is None:
                check['missing'].append('interval')
            else:
                if interval.get('active') != j or finite(interval['x']) != finite(births[j]) or exact(interval['N']) != exact(pre['N']):
                    raise ValueError('INVALID_PRE_INTERVAL_CROSSCHECK')
                check['interval_N_clock_active']='EXACT_MATCH'
            if not coordinates.is_file():
                check['missing'].append(coordinates.name)
            else:
                import numpy as np
                a = np.load(coordinates, allow_pickle=False)
                extra = setup['extra']
                if a.ndim != 1 or a.size < extra or not np.isfinite(a).all():
                    raise ValueError('INVALID_ACCEPTED_STATE')
                if [exact(v) for v in a[-extra:][4:7].tolist()] != [exact(v) for v in pre['ledgers'][4:7]]:
                    raise ValueError('INVALID_PRE_PHOTO_CROSSCHECK')
                check['accepted_photo']='EXACT_MATCH'
            if not check['missing']:
                check['status']='VERIFIED'
            crosschecks.append(check)
            history.append(dict(event=j, x=row['x'], I_pre=rec(im), I_post=rec(ip),
                                continuous=rec(c), jump=rec(jump), cumulative_continuous=rec(cum_c), cumulative_jump=rec(cum_j)))
            previous = ip
        tail_check = dict(event=B, kind='TAIL_ENDPOINT', status='MISSING_CROSSCHECK', missing=[])
        interval = by_event.get(B)
        coordinates = data/f'accepted_coordinates_event{B}.npy'
        if interval is None:
            tail_check['missing'].append('tail_interval')
        else:
            if (interval.get('active') != B or finite(interval['x']) != finite(setup['x1'])
                    or exact(interval['N']) != exact(endpoint['N'])):
                raise ValueError('INVALID_TAIL_INTERVAL_ENDPOINT_CROSSCHECK')
            tail_check['interval_N_clock_active']='EXACT_MATCH'
        if not coordinates.is_file():
            tail_check['missing'].append(coordinates.name)
        else:
            import numpy as np
            a = np.load(coordinates, allow_pickle=False)
            extra = setup['extra']
            if a.ndim != 1 or a.size < extra or not np.isfinite(a).all():
                raise ValueError('INVALID_TAIL_ACCEPTED_STATE')
            if [exact(v) for v in a[-extra:][4:7].tolist()] != [exact(v) for v in endpoint['ledgers'][4:7]]:
                raise ValueError('INVALID_TAIL_PHOTO_ENDPOINT_CROSSCHECK')
            tail_check['accepted_photo']='EXACT_MATCH'
        if not tail_check['missing']:
            tail_check['status']='VERIFIED'
        crosschecks.append(tail_check)
        end_budget = budget(endpoint['N'], endpoint['ledgers'][4:7], source_values)
        end = residual_fraction(end_budget)
        tail = end-previous
        continuous.append(tail);cum_c += tail
        history.append(dict(event=B, x=setup['x1'], continuous=rec(tail), jump=rec(F(0)),
                            cumulative_continuous=rec(cum_c), cumulative_jump=rec(cum_j), I_end=rec(end)))
        def summary(values):
            return dict(signed_sum=rec(sum(values,F(0))), L1=rec(sum(map(abs,values),F(0))),
                        maximum_absolute=rec(max(map(abs,values),default=F(0))))
        return dict(status='AVAILABLE', initial=initial, birth_count=B, crosschecks=crosschecks,
                    history=history, continuous=summary(continuous), jumps=summary(jumps), endpoint=rec(end),
                    telescope=rec(end-cum_c-cum_j), exact_zero_telescope_residual=end-cum_c-cum_j == 0,
                    same_target_exact_endpoint_gate=end_budget, original_gate=diagnose(data).get('original_gate'),
                    arithmetic='Exact Fraction from stored binary64 inputs; Decimal80 display only',
                    scope='Stored-history decomposition; not an integration or native continuum certificate')
    except (ValueError, KeyError, TypeError, IndexError) as e:
        reason = str(e)
        return dict(status='INCOMPLETE' if 'INCOMPLETE' in reason else 'INVALID', reason=reason, telescope=None)


def survivor_moments(endpoint, births):
    t = exact(endpoint['proper_time_s'])
    if len(births) != len(endpoint['cohorts']):
        raise ValueError('INVALID_COHORT_SHAPE')
    ages = [t-exact(b) for b in births]
    if any(a<0 for a in ages):
        raise ValueError('INVALID_PROPER_TIME_DOMAIN')
    out = dict(population='NATIVE_ALL_SURVIVORS', scope='Descriptive stored binary64 moments; not outward certificate', support_count=len(ages))
    for k,index in [('N',0),('U',1)]:
        weights = [exact(c[index]) for c in endpoint['cohorts']]
        if any(w<0 for w in weights):
            raise ValueError('INVALID_NEGATIVE_SURVIVOR_WEIGHT')
        total = sum(weights,F(0)); ep=exact(endpoint[k]); diff=abs(total-ep)
        # Existing comparison clock scale is 2e-14; retain that numerical scale and expose exact difference.
        tolerance = max(F.from_float(2e-14)*max(total,abs(ep)), F.from_float(8*math.ulp(float(ep))))
        if diff>tolerance:
            raise ValueError('INVALID_COHORT_ENDPOINT_SUM_'+k)
        r=dict(total=rec(total), endpoint_sum_difference=rec(total-ep), population_sum_tolerance=rec(tolerance))
        if total == 0:
            r.update(status='UNDEFINED', reason='ZERO_SURVIVOR_MASS', mean_age_s=None, variance_age_s2=None)
        else:
            mean=sum((a*w for a,w in zip(ages,weights)),F(0))/total
            var=sum((w*(a-mean)**2 for a,w in zip(ages,weights)),F(0))/total
            quantiles={}
            ordered=sorted(zip(ages,weights))
            for p in [F(1,10),F(1,2),F(9,10),F(99,100)]:
                accum=F(0)
                for a,w in ordered:
                    accum+=w
                    if accum>=p*total:
                        quantiles[str(float(p))]=float(a);break
            newest=sorted(zip(births,weights),reverse=True)
            r.update(status='AVAILABLE',mean_age_s=float(mean),variance_age_s2=float(var),
                     mean_exact=rec(mean),variance_exact=rec(var), age_quantiles_s=quantiles,
                     newest_cohort_mass_fractions={str(n):float(sum((w for _,w in newest[:n]),F(0))/total) for n in [1,2,4]})
        out[k]=r
    return out


def exposure(x):
    x=finite(x)
    if x<0: raise ValueError('NEGATIVE_EXPOSURE')
    return x


def midpoint_ratio(x):
    x=exposure(x)
    if x==0: return 1.
    if x<1e-3:
        z=x*x
        return 1-z/24+7*z*z/5760-31*z*z*z/967680
    if x/2>700:
        return math.exp(math.log(x)-x/2)/(-math.expm1(-x))
    return x*math.exp(-x/2)/(-math.expm1(-x))


def continuum_defect(x):
    x=exposure(x)
    if x<1e-3:
        z=x*x
        return z/24-7*z*z/5760+31*z*z*z/967680
    return 1-midpoint_ratio(x)


def paired_ratio(x):
    x=exposure(x);a=math.exp(-x/4)
    return 2*a/(1+a*a)


def paired_defect(x):
    x=exposure(x)
    a=-math.expm1(-x/4)
    return a*a/(1+(1-a)**2)


def exposure_limits(epsilon, hazard=None):
    epsilon=finite(epsilon)
    if not 0<epsilon<1: raise ValueError('EPSILON_DOMAIN')
    # Classify the actual binary64 endpoints with Decimal100, rather than
    # treating the rounded binary64 defect as a mathematical sign oracle.
    with localcontext() as ctx:
        ctx.prec=100
        target=Decimal.from_float(epsilon)
        def sign(value):
            x=Decimal.from_float(value)
            if x==0:
                defect=Decimal(0)
            elif x<1:
                # sinh(x/2)/(x/2) = 1+d; defect=d/(1+d).
                # This positive series avoids loss of tiny defects by 1-R.
                term=x*x/24;d=term;k=1
                while True:
                    term*=x*x/(4*(2*k+2)*(2*k+3))
                    updated=d+term
                    if updated==d: break
                    d=updated;k+=1
                defect=d/(1+d)
            else:
                defect=1-x/((x/2).exp()-(-x/2).exp())
            return defect-target
        lo,hi=0.,1.
        while sign(hi)<0: hi*=2
        for _ in range(1200):
            mid=(lo+hi)/2
            if mid in (lo,hi): break
            if sign(mid)<=0: lo=mid
            else: hi=mid
        bracket_signs=[str(sign(lo)),str(sign(hi))]
    # acosh(1/(1-eps)), evaluated through log1p to retain tiny eps.
    y=epsilon/(1-epsilon)
    pair=4*math.log1p(y+math.sqrt(y*(y+2)))
    out=dict(epsilon=epsilon, continuum_bracket=[lo,hi], paired_limit=pair,
             continuum_bracket_signs_decimal100=bracket_signs,
             continuum_bracket_target='Exact binary64 epsilon input; Decimal100 sign classification',
             continuum_defect_at_paired_boundary=continuum_defect(pair),
             refined_continuum_defect_at_paired_boundary=continuum_defect(pair/2),
             model='dn/dt=q-lambda*n; constant q>=0, lambda>=0, initially zero; T=m*h; uniform midpoint births q*h',
             scope='Conditional scalar diagnostic; no effective native hazard or continuum-error inference')
    if hazard is not None:
        hazard=finite(hazard)
        if hazard<0: raise ValueError('NEGATIVE_HAZARD')
        out['recommendation']=dict(lambda_per_s=hazard,h_continuum_max_s=lo/hazard if hazard else None,
                                   h_pair_max_s=pair/hazard if hazard else None,status='UNRESTRICTED_AT_LAMBDA_ZERO' if hazard==0 else 'CONDITIONAL_CONSTANT_SCALAR_MODEL')
    return out


def source_step(n0,q,h,lam):
    vals=[finite(v) for v in [n0,q,h,lam]]
    if min(vals)<0: raise ValueError('NEGATIVE_SOURCE_STEP_INPUT')
    n0,q,h,lam=vals;x=lam*h
    if not math.isfinite(x): raise ValueError('NONFINITE_EXPOSURE')
    emitted=q*h
    if not math.isfinite(emitted): raise ValueError('NONFINITE_EMISSION')
    if x==0: return dict(n1=n0+emitted, absorbed=0.)
    loss=-math.expm1(-x); phi=loss/x
    # 1-phi has a positive series at tiny x; do not subtract near-unity values.
    loss_source=(x/2-x*x/6+x**3/24-x**4/120+x**5/720) if x<1e-3 else 1-phi
    surviving_initial=(math.exp(math.log(n0)-x) if x>700 and n0>0 else n0*math.exp(-x))
    return dict(n1=surviving_initial+emitted*phi,absorbed=n0*loss+emitted*loss_source)


def paired_budget(a,b,sa,sb):
    dn=exact(a['N'])-exact(b['N'])
    ds=sum(map(exact,sa),F(0))-sum(map(exact,sb),F(0))
    dp=[exact(x)-exact(y) for x,y in zip(a['ledgers'][4:7],b['ledgers'][4:7])]
    ra=residual_fraction(budget(a['N'],a['ledgers'][4:7],sa));rb=residual_fraction(budget(b['N'],b['ledgers'][4:7],sb))
    dr=ra-rb; rhs=ds-sum(dp,F(0))+dr
    denominator=exact(b['N'])
    return dict(convention='Delta = native32 - native64; DeltaN=DeltaS-sum_species(DeltaPhoto)+DeltaR',
                delta_N=rec(dn),delta_source=rec(ds),delta_photo_by_species=[rec(v) for v in dp],delta_R=rec(dr),rhs=rec(rhs),
                exact_identity_residual=rec(dn-rhs),denominator_native64_N=rec(denominator),
                delta_photo_by_species_over_native64_N=[rec(v/denominator) if denominator else None for v in dp],
                endpoint32=dict(N=rec(exact(a['N'])),source_sum=rec(sum(map(exact,sa),F(0))),photo=[rec(exact(v)) for v in a['ledgers'][4:7]],residual=rec(ra)),
                endpoint64=dict(N=rec(exact(b['N'])),source_sum=rec(sum(map(exact,sb),F(0))),photo=[rec(exact(v)) for v in b['ledgers'][4:7]],residual=rec(rb)),
                signed_terms_over_native64_N={k:rec(v/denominator) if denominator else None for k,v in [('delta_N',dn),('delta_source',ds),('minus_delta_photo',-sum(dp,F(0))),('delta_R',dr)]})


def run(data32,data64,out,hazard=None):
    out=Path(out)
    if out.exists() and any(out.iterdir()): raise ValueError('NONEMPTY_OUTPUT_ATTEMPT_REFUSED')
    out.mkdir(parents=True,exist_ok=True)
    roots=[Path(data32),Path(data64)]
    setups=[read(p/'setup.json') for p in roots]
    endpoints=[read(p/'endpoint.json') for p in roots]
    for e,s in zip(endpoints,setups): e.setdefault('birth_times_s',s['birth_times_s'])
    metrics=endpoint_metrics(*endpoints)
    selected=[metrics['N'],metrics['U'],*metrics['photo_events'],*metrics['Gamma_s'],*metrics['heat_erg_per_absorber_s'],metrics['temperature_K']]
    matches,missing=match_observations(*[read(p/'observations.json') for p in roots])
    trajectory=[dict(x=b['x'],side=b['side'],N_relative=relative(a['physical']['N'],b['physical']['N']),U_relative=relative(a['physical']['U'],b['physical']['U'])) for a,b in matches]
    histories=[photon_history(p) for p in roots]
    study_path=TASK/'observable_certificates_20261020/results/STUDY.json'
    study=read(study_path)
    case={r['clock']:r for r in study['cases']}
    pair=next(r for r in study['pairs'] if r['coarse']==32 and r['reference']==64)
    empirical={}
    for i,k in enumerate(['N','U']):
        interval=pair['populations']['sensitive']['signed_difference'][i]
        delta=float(exact(endpoints[0][k])-exact(endpoints[1][k]));center=sum(interval)/2
        empirical[k]=dict(native_all_signed_pair=delta,fixed_sensitive_signed_pair_interval=interval,
                          native_all_minus_fixed_sensitive_pair_center=delta-center,
                          native64_all_denominator=endpoints[1][k],fixed64_sensitive_denominator_interval=case[64]['populations']['sensitive']['observables'][i])
    report=dict(schema='rei.native_age32.stored_analysis.v1',data32=str(roots[0].resolve()),data64=str(roots[1].resolve()),
                PRODUCTION_SCIENTIFIC_ADMISSION='NOT_ISSUED',native_age='HOLD',native_time='HOLD',nonlinear_response_bound='NOT_ESTABLISHED',
                finite_pair=dict(endpoint=metrics,finite_neighbor_target=.005,selected_endpoint_target_met=all(v is not None and v<=.005 for v in selected),common_observations=trajectory,missing_or_ambiguous=missing),
                native_survivors={str(n):survivor_moments(e,s['birth_times_s']) for n,e,s in zip([32,64],endpoints,setups)},
                photon_histories=dict(zip(['32','64'],histories)),paired_photon_budget=paired_budget(*endpoints,*[[row[0] for row in s['source_inventory']] for s in setups]),
                fixed_export_reuse=dict(source=str(study_path),source_sha256=hashlib.sha256(study_path.read_bytes()).hexdigest(),
                                       population_labels='FIXED_EXPORT_ALL / FIXED_EXPORT_SENSITIVE / FIXED_EXPORT_PASSIVE',
                                       cases=[case[32],case[64]],pair=pair,empirical_pair_discrepancy=empirical,
                                       assumption_gap='Native32 rebuilds midpoint source templates; fixed export coarsens fixed64 weights. Passive labels refer to endpoint frozen nodes, not persistent native paths; thresholds may cross/reconstruct. No native-to-frozen response bridge or certification.'),
                scalar_diagnostic=dict(limits=[exposure_limits(e,hazard) for e in [.005,.01,.1]], samples=[dict(x=x,R=midpoint_ratio(x),continuum_defect=continuum_defect(x),pair_ratio=paired_ratio(x),pair_defect=paired_defect(x)) for x in [0,1e-8,.1,1,10,100,1000]]))
    (out/'ANALYSIS.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with (out/'COMMON_TIME.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['x','side','N_relative','U_relative']);w.writeheader();w.writerows(trajectory)
    with (out/'PHOTON_HISTORY.csv').open('w',newline='') as f:
        fields=['age','event','x','continuous_decimal80','jump_decimal80','cumulative_continuous_decimal80','cumulative_jump_decimal80'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for n,h in zip([32,64],histories):
            for row in h.get('history',[]):
                w.writerow(dict(age=n,event=row['event'],x=row['x'],**{k+'_decimal80':row[k]['decimal80'] for k in ['continuous','jump','cumulative_continuous','cumulative_jump']}))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,1,figsize=(8,6),constrained_layout=True)
    for k in ['N','U']:
        rows=[r for r in trajectory if r['side']=='post' and r[k+'_relative'] is not None]
        axes[0].plot([r['x'] for r in rows],[r[k+'_relative'] for r in rows],marker='o',label=k)
    axes[0].axhline(.005,color='black',linestyle='--',label='original 0.005 target');axes[0].set_ylabel('|32-64| / |64|');axes[0].legend();axes[0].set_title('Native common-time finite pair')
    for n,h in zip([32,64],histories):
        rows=h.get('history',[])
        for kind,style in [('continuous','-'),('jump','--')]:
            if rows: axes[1].plot([r['x'] for r in rows],[float(r['cumulative_'+kind]['decimal80']) for r in rows],style,label=f'age{n} {kind}')
    axes[1].set_xlabel('x (native logarithmic clock)');axes[1].set_ylabel('Signed cumulative photon residual');axes[1].legend();axes[1].set_title('Exact stored history (missing age64 explicit events stays missing)')
    fig.savefig(out/'DIAGNOSTICS.png',dpi=160);plt.close(fig)
    print(json.dumps(dict(status='ANALYSIS_WRITTEN',output=str(out),history_status=[h['status'] for h in histories],finite_target_met=report['finite_pair']['selected_endpoint_target_met'])))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data32',type=Path,required=True);p.add_argument('--data64',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--lambda-per-s',type=float)
    a=p.parse_args();run(a.data32,a.data64,a.out,a.lambda_per_s)

if __name__=='__main__': main()
