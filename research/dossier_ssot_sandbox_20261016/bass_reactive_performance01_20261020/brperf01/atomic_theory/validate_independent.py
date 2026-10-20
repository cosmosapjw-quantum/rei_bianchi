"""Independent 60-digit direct-power formulas, source parsing, interpolation theory.

This evaluator does not import Rust/generated coefficients; it reads the pinned
original ASCII files again. It compares all emitted Rust values to decimal.Decimal direct
algebra rather than duplicating the log-domain implementation.
"""
from pathlib import Path
import csv
import hashlib
import json
import statistics
import sys
from decimal import Decimal, getcontext

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'evidence'
getcontext().prec=60

def sqrt(x): return x.sqrt()
def exp(x): return x.exp()
def log(x): return x.ln()

def read_original():
    pi={}
    for line in (DATA/'photo.dat').read_text().splitlines():
        values=line.split()
        pi[int(values[0]),int(values[1])]=list(map(Decimal,values[2:]))
    ci={}
    for line in (DATA/'cfit.dat').read_text().splitlines():
        key=int(line[6:8]),int(line[9:11])
        ci[key]=[Decimal(line[a:b]) for a,b in [(12,19),(20,21),(22,31),(32,38),(39,43),(44,48),(49,53)]]
    rr={}
    for line in (DATA/'rec_table1.dat').read_text().splitlines():
        key=int(line[9:11]),int(line[12:14])
        if key[0] in (3,6,7,8):
            rr[key]=[Decimal(line[a:b]) for a,b in [(16,25),(27,33),(35,44),(46,55)]]
    return pi,ci,rr

def ci_formula(coeff,t):
    de,p,a,x,k,lo,hi=coeff
    u=de/(Decimal('8.617385e-5')*t)
    return a*(1+p*sqrt(u))/(x+u)*u**k*exp(-u)*Decimal('1e-6')

def pi_formula(coeff,e):
    eth,emax,e0,s0,ya,p,yw,y0,y1=coeff
    if e<eth: return Decimal(0)
    x=e/e0-y0
    y=sqrt(x*x+y1*y1)
    return s0*((x-1)**2+yw*yw)*y**(p/2-Decimal('5.5'))*(1+sqrt(y/ya))**(-p)*Decimal('1e-22')

def rr_formula(coeff,t):
    a,b,t0,t1=coeff
    return a/(sqrt(t/t0)*(1+sqrt(t/t0))**(1-b)*(1+sqrt(t/t1))**(1+b))*Decimal('1e-6')

def independent_oracle():
    pi,ci,rr=read_original()
    records={p:{'count':0,'max_relative_error':0.0,'worst_case':None} for p in ('pi','ci','rr')}
    for row in csv.DictReader((OUT/'ATOMIC_VALUES.csv').open()):
        p=row['process']; key=int(row['z']),int(row['electrons'])
        arg=Decimal(row['input']); actual=Decimal(row['value_si'])
        exact={'pi':pi_formula,'ci':ci_formula,'rr':rr_formula}[p]({'pi':pi,'ci':ci,'rr':rr}[p][key],arg)
        # Binary64 endpoint Eth may lie an ulp below the decimal source literal;
        # this oracle evaluates the formula at the rounded published Rust endpoint
        # when it matches that same rounded threshold, preserving the gate contract.
        if p=='pi' and exact==0 and float(arg)==float(pi[key][0]):
            exact=pi_formula(pi[key],pi[key][0])
        assert exact>0 and actual>0,(p,key,arg,exact,actual)
        error=float(abs(actual/exact-1))
        rec=records[p]; rec['count']+=1
        if error>rec['max_relative_error']:
            rec['max_relative_error']=error
            rec['worst_case']={'z':key[0],'electrons':key[1],'input':str(arg),'rust_si':str(actual),'decimal_60digit_si':str(exact)}
        assert error<5e-13,(p,key,error)
    return records

def table_checks():
    rows=list(csv.DictReader((OUT/'TABLE_SCANS.csv').open()))
    aggregate=[]
    for process in ('ci','rr'):
        for tol in (1e-4,1e-5,1e-6):
            selected=[r for r in rows if r['process']==process and float(r['tolerance'])==tol]
            assert len(selected)==(24 if process=='ci' else 12)
            for r in selected:
                assert float(r['max_relative_error'])<=float(r['bound'])+2e-13
                assert float(r['bound'])<=tol*(1+1e-12)
            aggregate.append({'process':process,'target':tol,'ion_count':len(selected),
                'max_sampled_relative_error':max(float(r['max_relative_error']) for r in selected),
                'payload_bytes':sum(int(r['storage_bytes']) for r in selected),
                'sample_points':sum(int(r['scan_points']) for r in selected)})
    return aggregate

def detailed_balance_control():
    def pair(t):
        t=Decimal(t)
        kf=Decimal('2.00e-10')*t**Decimal('.402')*exp(-Decimal('37.1')/t)-Decimal('3.31e-17')*t**Decimal('1.48')
        kr=Decimal('2.06e-10')*t**Decimal('.396')*exp(-Decimal('33')/t)+Decimal('2.03e-9')*t**Decimal('-.332')
        return kf,kr
    # Common-grid logarithmic interpolation commutes with taking a rate ratio.
    # This is a representation identity, not a proof of thermal detailed balance.
    cases=[]
    for a,b,theta in [('2.7','3','0.37'),('10','20','0.61'),('1000','2000','0.2'),('100000','200000','0.8')]:
        a,b,theta=map(Decimal,(a,b,theta))
        fa,ra=pair(a); fb,rb=pair(b)
        independent=exp((1-theta)*log(ra)+theta*log(rb))/exp((1-theta)*log(fa)+theta*log(fb))
        ratio_table=exp((1-theta)*log(ra/fa)+theta*log(rb/fb))
        identity_error=abs(independent/ratio_table-1)
        assert identity_error<Decimal('1e-55')
        t=exp((1-theta)*log(a)+theta*log(b));f,r=pair(t)
        cases.append({'t_k':float(t),'ratio_identity_error':float(identity_error),
            'loglinear_ratio_relative_error':float(abs(ratio_table/(r/f)-1)),
            'owner_forward_over_reverse':float(f/r),
            'manufactured_0037ev_boltzmann_ratio':float(exp(-Decimal('.0037')/(Decimal('8.617333262145e-5')*t)))})
    return {'scope':'SAVIN_EMPIRICAL_PAIR_REPRESENTATION_ONLY_CX_OWNER_UNCHANGED','cases':cases,
        'conclusion':'A shared ratio table has the same exact-arithmetic interpolation error as two log tables on the same grid; do not replace Savin ratio by a manufactured energy-defect Boltzmann factor.'}

def summarize_bench(path):
    rows=list(csv.DictReader(path.open()))
    modes=sorted({r['backend'] for r in rows})
    result={}
    for mode in modes:
        vals=[float(r['seconds']) for r in rows if r['backend']==mode]
        result[mode]={'repeats':len(vals),'median_seconds':statistics.median(vals),'min_seconds':min(vals),'max_seconds':max(vals)}
    baseline=result['direct']['median_seconds']
    for mode in modes:
        result[mode]['ratio_of_medians_speedup_vs_direct']=baseline/result[mode]['median_seconds']
        pairs=[]
        for repeat in sorted({r['repeat'] for r in rows}):
            d=next(float(r['seconds']) for r in rows if r['repeat']==repeat and r['backend']=='direct')
            v=next(float(r['seconds']) for r in rows if r['repeat']==repeat and r['backend']==mode)
            pairs.append(d/v)
        result[mode]['median_paired_speedup']=statistics.median(pairs)
    return result

def main():
    result={'status':'PASS','independent_precision_decimal_digits':60,
        'oracle':independent_oracle(),'temperature_tables':table_checks(),
        'cx_ratio_control':detailed_balance_control(),
        'single_coefficient_benchmark':summarize_bench(OUT/'CATALOG_BENCHMARK.csv'),
        'common_temperature_bundle_benchmark':summarize_bench(OUT/'CATALOG_BUNDLE_BENCHMARK.csv'),
        'admission':'COEFFICIENT_AND_T_TABLE_ONLY_NO_NETWORK_ADMISSION',
        'timing_scope':'single sandbox process, release Rust, 12 alternating-order repeats; coefficient kernels only, no full-trajectory speedup inferred',
        'new_fit_parameters':False,'new_atomic_uncertainty_claim':False,
        'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('*.dat')}}
    (OUT/'INDEPENDENT_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
