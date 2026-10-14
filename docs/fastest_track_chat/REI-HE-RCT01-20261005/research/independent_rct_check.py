"""RCT-E2: Decimal70 oracle, independent of the Rust algebra and provider bodies.

Run this against the actual native line-protocol executable. The source nominal
tokens are frozen published inputs, not a physical atomic accuracy oracle.
"""
from __future__ import annotations
import argparse, csv, hashlib, itertools, json, subprocess, time
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 70
D = Decimal
Q = D('54.41776') - D('13.598434599702')
EV = D('1.602176634e-12')
KS = {'KF96': D('1e-14'), 'GM25': D('1.70e-13')}
DOMAINS = {'KF96': (D('1000'), D('10000000')), 'GM25': (D('200'), D('10000'))}
TOL = D('2e-12')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--native', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([args.native], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    calls = 0; checks = 0; failures = []; maxima = {}; rows = []; ratios = {}

    def call(parts):
        nonlocal calls
        line = ' '.join(map(str, parts))
        proc.stdin.write(line + '\n'); proc.stdin.flush()
        response = proc.stdout.readline()
        if not response:
            raise RuntimeError('Native probe terminated: ' + proc.stderr.read())
        calls += 1
        return json.loads(response, parse_float=D), line

    def truth(value, name, context=None):
        nonlocal checks
        checks += 1
        if not value:
            failures.append({'check': name, 'context': context})

    def close(actual, expected, gross, name, context=None):
        actual, expected, gross = D(str(actual)), D(str(expected)), abs(D(str(gross)))
        if gross == 0:
            err = D(0) if actual == expected else D('Infinity')
        else:
            err = abs(actual - expected) / gross
        maxima[name] = max(maxima.get(name, D(0)), err)
        truth(err <= TOL, name, context)
        return err

    # Exact coefficient endpoints are tested directly, without EOS round-trip.
    rate_points = {'KF96': [1000,5000,10000,100000,10000000],
                   'GM25': [200,1000,5000,10000]}
    for src, temperatures in rate_points.items():
        for t in temperatures:
            z,line = call(['rate',src,t]); truth(z.get('ok') is True,'rate accepted',line)
            close(z['k_cm3_s'],KS[src],KS[src],'nominal coefficient',line)
            truth(z['physical_admission'] is False,'rate physical admission false',line)
    invalid_rate_count = 0
    for src,(lo,hi) in DOMAINS.items():
        for t in [lo-D('0.001'),hi+D('0.001'),'NaN','inf']:
            z,line=call(['rate',src,t]);truth(z.get('ok') is False,'rate reject invalid T',line)
            invalid_rate_count += 1
    z,line=call(['rate','AUTO',5000]);truth(z.get('ok') is False,'no automatic source',line)

    fractions = [(D('.2'),D('.1'),D('.4')), (D(0),D(0),D(1)),
                 (D(1),D('.1'),D('.4')), (D('.2'),D('.1'),D(0))]
    state_points = 0; closed_points = 0; count_points = 0
    modes = [('COUNT',None),('Qminus1',Q-1),('Q',Q),('Qplus1',Q+1)]
    for src,t,nh,ratio,fr in itertools.product(KS,[1001,5000,9999],
                    [D('1e-4'),D('.01')],[D('.083'),D('.3')],fractions):
        state_points += 1; nhe=nh*ratio; x,y,zhe=fr
        k=KS[src]; nhi=nh*(1-x); he3=nhe*zhe; r=k*nhi*he3
        expected_species=[-r,r,D(0),r,-r,D(0)]
        expected_fraction=[r/nh,r/nhe,-r/nhe]
        # Gross chemical scale remains nonzero even when Ebar=Q or R=0.
        rate_scale=max(abs(r),k*nh*nhe*D('1e-30'))
        energy_scale=Q*EV*rate_scale
        for mode,mean in modes:
            q,line=call(['event',src,nh,nhe,x,y,zhe,t,'COUNT' if mean is None else mean])
            truth(q.get('ok') is True,'event accepted',line)
            if not q.get('ok'): continue
            truth(q['physical_admission'] is False,'event physical admission false',line)
            lo,hi=DOMAINS[src];truth(lo<=q['temperature_k']<=hi,'actual EOS T supported',line)
            close(q['k_cm3_s'],k,k,'event coefficient',line)
            close(q['n_hi_cm3'],nhi,nh,'HI density',line)
            close(q['n_heiii_cm3'],he3,nhe,'HeIII density',line)
            er=close(q['event_rate_cm3_s'],r,rate_scale,'event rate',line)
            for i in range(6): close(q['species_rate_cm3_s'][i],expected_species[i],rate_scale,'species rate',line)
            for i,scale in enumerate([rate_scale/nh,rate_scale/nhe,rate_scale/nhe]):
                close(q['fraction_rate_s'][i],expected_fraction[i],scale,'fraction rate',line)
            close(q['free_electron_rate_cm3_s'],0,rate_scale,'explicit free electron',line)
            close(nh*q['fraction_rate_s'][0]+nhe*(q['fraction_rate_s'][1]+2*q['fraction_rate_s'][2]),0,
                  4*rate_scale,'charge inferred free electron',line)
            close(q['emitted_photon_count_cm3_s'],r,rate_scale,'primary photon count',line)
            close(q['q_ev'],Q,Q,'chemical Q',line)
            close(q['chemical_energy_rate_erg_cm3_s'],-Q*EV*r,energy_scale,'chemical energy',line)
            if mean is None:
                count_points += 1
                for field in ['mean_escaped_photon_energy_ev','thermal_energy_rate_erg_cm3_s',
                              'escaped_energy_rate_erg_cm3_s','combined_derivative','combined_escaped_energy_rate']:
                    truth(q[field] is None,'missing moment is null: '+field,line)
                truth(q['closure_complete'] is False,'count cannot close thermal RHS',line)
                ratios[(src,t,str(nh),str(ratio),str(fr))]=q['event_rate_cm3_s']
            else:
                closed_points += 1
                heat=(Q-mean)*EV*r; escape=mean*EV*r
                close(q['mean_escaped_photon_energy_ev'],mean,mean,'supplied mean energy',line)
                close(q['thermal_energy_rate_erg_cm3_s'],heat,energy_scale,'heat energy',line)
                close(q['escaped_energy_rate_erg_cm3_s'],escape,energy_scale,'escape energy',line)
                close(q['chemical_energy_rate_erg_cm3_s']+q['thermal_energy_rate_erg_cm3_s']+
                      q['escaped_energy_rate_erg_cm3_s'],0,2*energy_scale,'closed energy residual',line)
                truth(q['closure_complete'] is True,'explicit closure complete',line)
                truth(q['closure_input_origin']=='CALLER_SUPPLIED_NO_ATOMIC_MOMENT','closure origin class',line)
                delta=expected_fraction+[heat,D(0),D(0),D(0)]
                for i in range(7):
                    base=q['baseline_derivative'][i]
                    gross=abs(base)+abs(delta[i])
                    close(q['combined_derivative'][i],base+delta[i],gross,'composed RHS',line)
                base_escape=q['baseline_escaped_energy_rate']
                close(q['combined_escaped_energy_rate'],base_escape+escape,
                      abs(base_escape)+abs(escape),'composed escape',line)
            rows.append({'source':src,'T_requested':t,'T_actual':str(q['temperature_k']),
                         'nH':str(nh),'nHe':str(nhe),'xHII':str(x),'xHeII':str(y),'xHeIII':str(zhe),
                         'closure':mode,'mean_input_eV':'' if mean is None else str(mean),
                         'input_origin':'COUNT_NONE' if mean is None else 'RCT-E2_SYNTHETIC_Q_OFFSET',
                         'R_expected':str(r),'R_native':str(q['event_rate_cm3_s']),
                         'event_scaled_error':str(er)})

    ratio_checks=0
    for key,value in ratios.items():
        if key[0]=='KF96' and value>0:
            other=ratios[('GM25',)+key[1:]]
            close(other,17*value,17*value,'17x source spread',str(key));ratio_checks+=1

    off_count=0
    for nh,ratio,fr in itertools.product([D('1e-4'),D('.01')],[D('.083'),D('.3')],fractions):
        z,line=call(['off',nh,nh*ratio,*fr,5000]);truth(z.get('ok') is True,'OFF valid',line)
        truth(z['baseline_derivative']==z['combined_derivative'],'OFF identical RHS',line)
        truth(z['baseline_escaped_energy_rate']==z['combined_escaped_energy_rate'],'OFF identical escape',line)
        off_count += 1
    invalid_closure_count=0
    for mean in ['0','-1','NaN','inf']:
        z,line=call(['event','KF96','.01','.00083','.2','.1','.4',5000,mean])
        truth(z.get('ok') is False,'invalid mean rejected',line);invalid_closure_count += 1

    # Independent falsifiers, deliberately wrong equations on a nonzero fixture.
    nh=D('.01');nhe=D('.00083');r=KS['KF96']*nh*D('.8')*nhe*D('.4')
    negative={
      'free_electron_minus_R':abs(-r)/r,
      'HeIII_wrong_sign':abs(nh*(r/nh)+nhe*(r/nhe+2*r/nhe))/(4*r),
      'missing_nHe_prefactor':abs(KS['KF96']*nh*D('.8')*D('.4')-r)/r,
      'Q_into_heat_plus_Q_photon':abs(-Q*EV*r+Q*EV*r+Q*EV*r)/(2*Q*EV*r),
    }
    for name,err in negative.items():truth(err>TOL,'negative control rejects '+name)
    proc.stdin.close(); code=proc.wait(timeout=10);stderr=proc.stderr.read()
    truth(code==0,'native exit0',stderr)
    with (out/'independent_rct_points.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    result={'schema_version':'1.0','experiment_id':'RCT-E2','classification':'confirmatory',
            'status':'PASS' if not failures else 'FAIL','precision_digits':70,'checks':checks,
            'native_calls':calls,'state_points':state_points,'event_mode_calls':len(rows),
            'count_only_points':count_points,'closed_points':closed_points,'coefficient_points':sum(map(len,rate_points.values())),
            'invalid_rate_temperatures':invalid_rate_count,'invalid_closure_points':invalid_closure_count,
            'off_points':off_count,'source_ratio_checks':ratio_checks,'tolerance':str(TOL),
            'max_scaled_errors':{k:str(v) for k,v in maxima.items()},
            'negative_controls':{k:str(v) for k,v in negative.items()},'failures':failures,
            'native_exit_code':code,'native_binary_sha256':hashlib.sha256(Path(args.native).read_bytes()).hexdigest(),
            'oracle_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'closure_provenance':'Each Q-offset value is a synthetic caller-supplied test input recorded in CSV, not an atomic prediction.',
            'scope':'finite point native source selection, event, and conditional RHS composition; no source accuracy, spectrum or integrated solver admission',
            'timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    (out/'INDEPENDENT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if not failures else 1)

if __name__=='__main__': main()
