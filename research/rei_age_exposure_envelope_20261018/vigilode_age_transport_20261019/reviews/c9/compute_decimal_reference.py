"""Independent Decimal-100 numerical reference for the frozen exported node model."""
import csv, hashlib, json, time
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
ROOT=Path('/workspace/scratch/36ed695112a9')
LANE=ROOT/'rei_bianchi/research/rei_age_exposure_envelope_20261018/vigilode_age_transport_20261019'
OUT=ROOT/'vigilode_intake_20261019/c9_review'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def D(x): return Decimal.from_float(x)
model=json.loads((LANE/'inputs/model.json').read_text())
with (LANE/'inputs/nodes.csv').open(newline='') as f:
    rows=[{k:(int(v) if k in ('cohort','cell','node') else float(v)) for k,v in r.items()} for r in csv.DictReader(f)]
started=time.monotonic()
with localcontext() as ctx:
    ctx.prec=100
    rates={}
    for r in rows:
        key=tuple(r[f'lambda{j}'] for j in range(3))
        if key not in rates:
            rat=sum((Fraction.from_float(x) for x in key),Fraction(0))
            lam=Decimal(rat.numerator)/Decimal(rat.denominator)
            shares=[D(x)/lam if lam else Decimal(0) for x in key]
            rates[key]=(lam,shares)
        r['rate_key']=key
    cache={}
    def attenuation(key,birth):
        loc=(key,birth)
        if loc not in cache:
            age=D(model['observe_time_s'])-D(birth)
            cache[loc]=(-rates[key][0]*age).exp()
        return cache[loc]
    fields=['N','U_ev','age_first_number_s','age_second_number_s2','photo0','photo1','photo2']
    cases=[]
    raw_cases={}
    for n in [8,16,32,64]:
        totals=[Decimal(0) for _ in range(7)]
        source=Decimal(0)
        for r in rows:
            m=D(r['mass']);source+=m
            birth=model['clocks'][str(n)][r['cohort']*n//64]
            age=D(model['observe_time_s'])-D(birth)
            s=attenuation(r['rate_key'],birth)
            number=m*s
            absorbed=m*(1-s)
            shares=rates[r['rate_key']][1]
            values=[number,number*D(r['energy']),number*age,number*age*age]+[absorbed*q for q in shares]
            for j,v in enumerate(values):totals[j]+=v
        raw_cases[n]=totals
        ledger=totals[0]+sum(totals[4:])-source
        cases.append({'birth_groups':n,'values_decimal100':dict(zip(fields,map(str,totals))),
                      'source_mass_decimal100':str(source),'ledger_roundoff_decimal100':str(ledger)})
    pairs=[]
    for n in [8,16,32,64]:
        sharp=Decimal(0)
        for r in rows:
            a=model['clocks'][str(n)][r['cohort']*n//64]
            b=r['birth_time_s']
            sharp+=D(r['mass'])*abs(attenuation(r['rate_key'],a)-attenuation(r['rate_key'],b))
        pairs.append({'coarse':n,'fine':64,'signed_N_difference_decimal100':str(raw_cases[n][0]-raw_cases[64][0]),
                      'nodewise_absolute_difference_sum_decimal100':str(sharp)})
result={'status':'INDEPENDENT_NUMERICAL_REFERENCE_COMPUTED','precision':100,'method':'Python Decimal.exp with exact binary64 input conversion and Fraction total hazard; no Rust solver or native evolution',
        'model_sha256':sha(LANE/'inputs/model.json'),'nodes_sha256':sha(LANE/'inputs/nodes.csv'),
        'cases':cases,'pairs':pairs,'nodes':len(rows),'unique_rate_tuples':len(rates),
        'cached_exponentials':len(cache),'native_reexecutions':0,
        'wall_seconds':time.monotonic()-started,'production_scientific_admission':'NOT_ISSUED'}
(OUT/'DECIMAL_ACTUAL_DATA_REFERENCE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'cases':len(cases),'nodes':len(rows),'unique_rates':len(rates),'cached_exp':len(cache),'wall_seconds':result['wall_seconds'],'pairs':pairs},indent=2))
