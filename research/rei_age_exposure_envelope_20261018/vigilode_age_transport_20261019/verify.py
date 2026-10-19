"""Independent Decimal and source-identity checks; never runs native dynamics."""
from pathlib import Path
from decimal import Decimal, localcontext
import hashlib
import csv
import json
import math
import sys

HERE=Path(__file__).resolve().parent


def main():
    fixtures=json.loads((HERE/'results/EXP_FIXTURES.json').read_text())
    checks=[]
    with localcontext() as ctx:
        ctx.prec=100
        for row in fixtures:
            tau=Decimal.from_float(row['tau'])
            expected=(-tau).exp()
            lo,hi=map(Decimal.from_float,row['interval'])
            assert lo<=expected<=hi, row
            checks.append({'tau':row['tau'],'decimal100':str(expected),'enclosed':True})
    study=json.loads((HERE/'results/STUDY.json').read_text())
    assert study['nodes']==57344 and study['passive_nodes']==4096
    for case in study['cases']:
        assert case['ledger_contains_zero']
        assert case['photon_ledger_residual'][0]<=0<=case['photon_ledger_residual'][1]
        assert case['passive_surviving_mass']==study['cases'][0]['passive_surviving_mass']
        assert case['N'][0]>=0
        assert all(x[0]>=0 for x in case['species_photoevents'])
    for pair in study['paired_bounds']:
        assert pair['thread_byte_parity']
        assert pair['all_prefixes_bound_exact_rational_leaf_recurrence']
        assert pair['affine_prefix_final_upper']>=pair['sharp_per_node_final_upper']
        if 'grouped_affine' in pair:
            grouped=pair['grouped_affine']
            assert grouped['thread_byte_parity']
            assert grouped['all_group_prefixes_bound_exact_rational_leaf_recurrence']
            assert grouped['final_upper']>=abs(pair['central_N_difference'])
    # The unlabelled birth and hazard marginals agree, but their correlation differs.
    # w=(1,1), lambda=(0,1), T=1, bA=(0,1), bB=(1,0).
    # N_A=2 and N_B=1+exp(-1); label-preserving D=1-exp(-1).
    kernel = next(row['interval'] for row in fixtures if row['tau']==1.0)
    with localcontext() as ctx:
        ctx.prec=100
        n_a=Decimal(2)
        n_b=Decimal(1)+(-Decimal(1)).exp()
        difference=n_a-n_b
        delta_lower=Decimal(1)-Decimal.from_float(kernel[1])
        delta_upper=Decimal(1)-Decimal.from_float(kernel[0])
        assert delta_lower <= difference <= delta_upper
    counterexample={'weights':[1,1], 'lambda_labels':[0,1], 'observe_time':1,
                    'birth_A':[0,1], 'birth_B':[1,0],
                    'ordinary_birth_marginal_W1':0, 'ordinary_lambda_marginals_equal':True,
                    'surviving_N_A':str(n_a), 'surviving_N_B_decimal100':str(n_b),
                    'actual_difference_decimal100':str(difference),
                    'label_preserving_D_interval':[str(delta_lower),str(delta_upper)],
                    'conclusion':'Equal unlabelled marginals do not preserve age-rate correlation.'}
    def check_finite(value):
        if isinstance(value,dict):
            for child in value.values(): check_finite(child)
        elif isinstance(value,list):
            for child in value: check_finite(child)
        elif isinstance(value,float):
            assert math.isfinite(value)
    check_finite(study)
    # Independent high-precision labelled final-D check on the complete immutable CSV.
    decimal_direct=[]
    model=json.loads((HERE/'inputs/model.json').read_text())
    rows=list(csv.DictReader((HERE/'inputs/nodes.csv').open()))
    with localcontext() as ctx:
        ctx.prec=100
        prepared=[]
        for row in rows:
            rates=tuple(float(row['lambda'+str(k)]) for k in range(3))
            prepared.append((int(row['cohort']),Decimal.from_float(float(row['mass'])),
                             sum((Decimal.from_float(v) for v in rates),Decimal(0)),rates,
                             float(row['birth_time_s'])))
        observe=Decimal.from_float(model['observe_time_s'])
        exp_cache={}
        def decay(rates,hazard,later,earlier):
            key=(rates,later,earlier)
            if key not in exp_cache:
                age=Decimal.from_float(later)-Decimal.from_float(earlier)
                exp_cache[key]=(-hazard*age).exp()
            return exp_cache[key]
        for pair in study['paired_bounds']:
            n=pair['coarse']
            total=Decimal(0)
            for cohort,weight,hazard,rates,birth in prepared:
                if not hazard: continue
                coarse=model['clocks'][str(n)][cohort*n//64]
                later=max(coarse,birth)
                earlier=min(coarse,birth)
                if later==earlier: continue
                local=weight*(Decimal(1)-decay(rates,hazard,later,earlier))
                total+=local*decay(rates,hazard,model['observe_time_s'],later)
            assert total<=Decimal.from_float(pair['sharp_per_node_final_upper'])
            assert total<=Decimal.from_float(pair['affine_prefix_final_upper'])
            if 'grouped_affine' in pair:
                assert total<=Decimal.from_float(pair['grouped_affine']['final_upper'])
            decimal_direct.append({'coarse':n,'fine':64,'D_decimal100':str(total),
                                   'all_reported_upper_bounds_enclose':True})
    sys.path.insert(0,str(HERE.parent/'src'))
    from native_inputs import load_manifest
    manifest=load_manifest(HERE.parent)
    original=HERE.parent/'intake/native_original_35d9747'
    source_checks=[]
    if original.is_dir():
        for name,identity in manifest['files'].items():
            actual=hashlib.sha256((original/name).read_bytes()).hexdigest()
            assert actual==identity['sha256'],name
            source_checks.append(name)
    vendor=json.loads((HERE/'rust/VENDOR_PROVENANCE.json').read_text())
    for name,identity in vendor['files'].items():
        assert hashlib.sha256((HERE/'rust'/name).read_bytes()).hexdigest()==identity
    result={'status':'PASS','decimal_precision':100,'exp_cases':checks,
            'rate_counterexample':counterexample,'full_labelled_D_decimal100':decimal_direct,
            'original_native_manifest_count':len(manifest['files']),
            'original_native_files_independently_rehashed':len(source_checks),
            'native_rhs_executed':False,'source_identity':manifest['native_sha'],
            'vendored_modules_unmodified':True}
    (HERE/'results/VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','decimal_exp_cases':len(checks),
                      'original_native_files_rehashed':len(source_checks)}))


if __name__=='__main__':
    main()
