"""Exploratory RCT-E2X after the concrete concurrent FT03 source update."""
import argparse,hashlib,json,subprocess,time
from decimal import Decimal as D,getcontext
from pathlib import Path
getcontext().prec=70
Q=D('54.41776')-D('13.598434599702')
EV=D('1.602176634e-12')
TOL=D('2e-12')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--native',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    commands=[];cases=[]
    for t in [30001,50000,109999]:
        for offset in [-1,0,1]:
            mean=Q+offset;commands.append(f'ft03 KF96 {t} {mean}');cases.append((t,mean))
    for t in [30001,50000,109999]:commands.append(f'ft03 GM25 {t} {Q}')
    run=subprocess.run([a.native],input='\n'.join(commands)+'\n',capture_output=True,text=True)
    lines=run.stdout.splitlines();checks=0;failures=[];maximum=D(0);evidence=[]
    def truth(ok,name,command):
        nonlocal checks
        checks+=1
        if not ok:failures.append({'check':name,'command':command})
    def close(got,want,scale,name,command):
        nonlocal maximum
        got=D(str(got));want=D(str(want));scale=abs(D(str(scale)))
        err=abs(got-want)/scale if scale else (D(0) if got==want else D('Infinity'))
        maximum=max(maximum,err);truth(err<=TOL,name,command)
    truth(run.returncode==0,'native exit0','batch')
    truth(len(lines)==len(commands),'one JSON line per request','batch')
    nh=D('1e-4');nhe=D('8.3e-6');k=D('1e-14')
    r=k*nh*D('.1')*nhe*D('.6')
    delta_fraction=[r/nh,r/nhe,-r/nhe];energy_scale=Q*EV*r
    for i,(t,mean) in enumerate(cases):
        c=commands[i];z=json.loads(lines[i],parse_float=D);truth(z.get('ok') is True,'FT03 RCT accepted',c)
        if not z.get('ok'):continue
        close(z['n_h_cm3'],nh,nh,'nH identity',c);close(z['n_he_cm3'],nhe,nhe,'nHe identity',c)
        for got,want in zip(z['fractions'],[D('.9'),D('.3'),D('.6')]):close(got,want,1,'fixture fractions',c)
        close(z['event_rate_cm3_s'],r,r,'FT03 event',c)
        close(z['k_cm3_s'],k,k,'KF96 nominal at active FT03 T',c)
        heat=(Q-mean)*EV*r;escape=mean*EV*r
        close(z['chemical_energy_rate_erg_cm3_s'],-Q*EV*r,energy_scale,'chemical',c)
        close(z['thermal_energy_rate_erg_cm3_s'],heat,energy_scale,'heat',c)
        close(z['escaped_energy_rate_erg_cm3_s'],escape,energy_scale,'escape',c)
        close(z['chemical_energy_rate_erg_cm3_s']+z['thermal_energy_rate_erg_cm3_s']+z['escaped_energy_rate_erg_cm3_s'],0,2*energy_scale,'energy cancellation',c)
        close(nh*z['fraction_rate_s'][0]+nhe*(z['fraction_rate_s'][1]+2*z['fraction_rate_s'][2]),0,4*r,'electron cancellation',c)
        for j,delta in enumerate(delta_fraction+[heat,D(0),D(0),D(0)]):
            b=z['baseline_derivative'][j];close(z['combined_derivative'][j],b+delta,abs(b)+abs(delta),'actual FT03 composed RHS',c)
        b=z['baseline_escaped_energy_rate']
        close(z['combined_escaped_energy_rate'],b+escape,abs(b)+abs(escape),'actual FT03 composed escape',c)
        truth(z['closure_input_origin']=='CALLER_SUPPLIED_NO_ATOMIC_MOMENT','closure origin',c)
        truth(z['physical_admission'] is False,'no physical admission',c)
        evidence.append({'command':c,'actual_temperature_K':str(z['temperature_k']),'source':'KF96','mean_origin':'RCT-E2X_SYNTHETIC_Q_OFFSET','native':json.loads(lines[i])})
    for i in range(len(cases),len(commands)):
        z=json.loads(lines[i]);truth(z.get('ok') is False,'GM25 rejected in active FT03 temperature domain',commands[i])
    result={'schema_version':'1.0','experiment_id':'RCT-E2X-FT03','classification':'exploratory','status':'PASS' if not failures else 'FAIL','checks':checks,'native_calls':len(commands),'closed_points':len(cases),'GM25_domain_rejections':3,'max_gross_scaled_error':str(maximum),'tolerance':str(TOL),'failures':failures,'native_exit_code':run.returncode,'native_binary_sha256':hashlib.sha256(Path(a.native).read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'actual ft03_rhs baseline plus RCT derivative delta; no FT03 implicit stepper integration, no source or physical moment accuracy claim','timestamp_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    (out/'FT03_INDEPENDENT_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'FT03_INDEPENDENT_CASES.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(result,indent=2));raise SystemExit(0 if not failures else 1)
if __name__=='__main__':main()
