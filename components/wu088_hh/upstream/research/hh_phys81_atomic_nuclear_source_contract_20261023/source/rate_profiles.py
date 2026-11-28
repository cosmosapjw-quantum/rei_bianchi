"""Create-only finite-source/Bell-model comparison; no prior IVP replay."""
from pathlib import Path
import csv, datetime, hashlib, json, math, sys, traceback, warnings
import numpy as np
import scipy
from scipy.integrate import quad
from registry import load_rates
from vendor.bell_kernel_phys80 import BellParameters, maxwellian_at_order, cross_section_cm2, VELOCITY_FACTOR, KB_EV_K
ROOT=Path(__file__).resolve().parents[1]
TEMPERATURES=(255.,300.,1000.,3000.,10000.,20000.,25370.66308424773,35000.,50000.)
QUADRATURE={'epsabs':1e-32,'epsrel':3e-11,'limit':100,'maximum_reported_relative_error':1e-8,'exponential_x_cap':800.,'full_Bell_Laguerre_order':64}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_once(p,x):
    with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def binding():
    files=['source/rate_profiles.py','source/registry.py','source/finite_ci.py','source/vendor/ci_finite_c22d.py','source/vendor/CCC_TICS_1S.txt','source/vendor/bell_kernel_phys80.py','source_data/ADMITTED_FINITE_CI_REGISTRY.json','source_data/PHYS81_CI_FINITE_WINDOW_LITERAL_DATA.csv','source_data/BELL1983_VISUAL_TABLE_TRANSCRIPT.json']
    return {'files':{s:sha(ROOT/s) for s in files},'temperatures_K':list(TEMPERATURES),'quadrature':QUADRATURE,'runtime':{'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__}}

def bell_window(p,T,lo,hi):
    theta=KB_EV_K*T;y=(hi-lo)/theta
    cuts=sorted(set([0.,min(y,800.),*[v for v in (1.,4.,16.,64.,256.) if v<min(y,800.)]]))
    f=lambda x:(lo+theta*x)*cross_section_cm2(p,lo+theta*x)*math.exp(-x)
    segments=[]
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter('always')
        for a,b in zip(cuts[:-1],cuts[1:]):
            value,error=quad(f,a,b,epsabs=QUADRATURE['epsabs'],epsrel=QUADRATURE['epsrel'],limit=QUADRATURE['limit'])
            segments.append({'x_bounds':[a,b],'integral':value,'reported_absolute_error':error})
    result=math.fsum(s['integral'] for s in segments);error=math.fsum(s['reported_absolute_error'] for s in segments)
    messages=[str(w.message) for w in notices]
    detail={'segments':segments,'reported_relative_error':error/result if result>0 else None,'warnings':messages,'x_cap_active':y>800.}
    if not math.isfinite(result) or result<=0 or not math.isfinite(error) or messages or error>QUADRATURE['maximum_reported_relative_error']*result:raise ArithmeticError('BELL_WINDOW_QUADRATURE_FAILED:'+json.dumps(detail))
    return math.log(VELOCITY_FACTOR)-.5*math.log(theta)-lo/theta+math.log(result),detail

def main():
    outdir=ROOT/'results';outdir.mkdir(parents=True,exist_ok=True)
    out=outdir/'RATE_PROFILES.json';ident=binding()
    science_id=hashlib.sha256(json.dumps(ident,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if out.exists():raise FileExistsError('PROFILE_IDENTITY_ALREADY_COMPLETE')
    write_once(outdir/'RATE_PROFILE_CLAIM.json',{'science_id':science_id,'identity':ident,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    rows=[];quadrature=[];counts={'finite_profiles':0,'new_Bell64_evaluations_using_reused_kernel':0,'new_Bell_finite_window_integrals':0,'ODE':0}
    try:
        rates=load_rates();transcript=json.loads((ROOT/'source_data/BELL1983_VISUAL_TABLE_TRANSCRIPT.json').read_text());bell={}
        for r in transcript['rows']:
            if r['species'] in ('H I','He I','Li I'):
                bell[r['species']]=BellParameters(float(r['I_eV_printed']),float(r['A_mantissa_printed'])*1e-13,tuple(float(v or 0)*1e-13 for v in r['B_mantissas_printed']),transcript['source']+' original printed Table5')
        for model,key in zip(rates,('H I','He I','Li I')):
            for T in TEMPERATURES:
                finite=model.evaluate(T);counts['finite_profiles']+=1
                full=maxwellian_at_order(bell[key],T,64);counts['new_Bell64_evaluations_using_reused_kernel']+=1
                logwindow,detail=bell_window(bell[key],T,model.lower_eV,model.upper_eV);counts['new_Bell_finite_window_integrals']+=1
                row={'species':model.species,'T_K':T,'finite_log10_K':finite.log10K_cm3_s,'finite_K_cm3_s':finite.K_cm3_s,'finite_underflow':finite.float64_underflow,'finite_mean_incoming_eV':finite.mean_incoming_eV,'finite_mean_excess_over_chemical_eV':finite.mean_incoming_eV-model.Ichemical_eV,'finite_dlogK_dT_per_K':finite.dlogK_dT_per_K,'Bell_full_log10_K':full.log_rate_cm3_s/math.log(10),'Bell_same_window_log10_K':logwindow/math.log(10),'Bell_model_window_fraction':math.exp(logwindow-full.log_rate_cm3_s),'CCC_over_Bell_same_window':math.exp(finite.logK_cm3_s-logwindow)}
                if any(not math.isfinite(v) for v in row.values() if isinstance(v,float)):raise ArithmeticError('NONFINITE_PROFILE')
                rows.append(row);quadrature.append({'species':model.species,'T_K':T,**detail})
        csvpath=outdir/'RATE_PROFILES.csv'
        with csvpath.open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        rec={'schema':'PHYS81_RATE_PROFILE_V2','status':'COMPLETE_SCOPED','science_id':science_id,'identity':ident,'rows':rows,'counts':counts,'quadrature_receipts':quadrature,'CSV_SHA256':sha(csvpath),'source_registry_sha256':sha(ROOT/'source_data/ADMITTED_FINITE_CI_REGISTRY.json'),'meaning':'CCC finite-support operator vs explicit Bell analytic fit; the latter is a comparison model, not truth or physical error envelope. Window fractions are fractions within Bell model only.','quadrature':'Floating-point adaptive finite-window quadrature; reported numerical errors retained; no certified bound. x beyond800 unrepresented. Full Bell uses order64 Gauss-Laguerre; no physical fit/interpolation/tail error certificate.'}
        write_once(out,rec)
        print(json.dumps({'status':rec['status'],'science_id':science_id,'counts':counts,'selected':[r for r in rows if r['T_K'] in (255.,25370.66308424773)]}))
    except Exception as e:
        write_once(outdir/'RATE_PROFILE_FAILED_ATTEMPT.json',{'science_id':science_id,'counts_before_failure':counts,'completed_rows':rows,'completed_quadratures':quadrature,'error':repr(e),'traceback':traceback.format_exc()});raise

if __name__=='__main__':main()
