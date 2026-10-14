"""Independent Decimal/SymPy oracle, plus adversarial data regression fixtures."""
from decimal import Decimal as D, localcontext
from fractions import Fraction
from pathlib import Path
import argparse, csv, gzip, hashlib, importlib.util, json, struct, tempfile
import sympy as s

HERE=Path(__file__).resolve().parent

def exact(v):
    q=Fraction(v['exact'])
    return D(q.numerator)/D(q.denominator)

def close(a,b):
    if abs(a-b)>D('1e-65'):
        raise AssertionError((str(a),str(b)))

def validate(repo, result):
    r=json.loads(result.read_text());root=repo/'runs/rei_fastest_v1/paired'
    assert r['scientific_admission']=='HOLD' and r['continuum_time_error_certificate']=='NOT_ESTABLISHED'
    assert r['new_campaign_executions']==0
    for path,digest in r['input_sha256'].items():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest
    curves={}
    for label in ('T0','T1','T2'):
        for g in ('BI','FLRW'):
            with gzip.open(root/'curves'/(label+'_'+g+'.csv.gz'),'rt') as f:
                curves[label+'_'+g]={D.from_float(float(v['time_s'])):v for v in csv.DictReader(f)}
    checks=0
    with localcontext() as ctx:
        ctx.prec=90
        ts=list(curves['T0_FLRW']);assert len(ts)==8000
        for field,out in r['measured'].items():
            c=[]
            for label in ('T0','T1','T2'):
                c.append([D.from_float(float(curves[label+'_BI'][t][field]))-D.from_float(float(curves[label+'_FLRW'][t][field])) for t in ts])
            a=[y-x for x,y in zip(c[0],c[1])];b=[y-x for x,y in zip(c[1],c[2])]
            for k in range(3):close(exact(out['final_contrasts'][k]),c[k][-1]);checks+=1
            close(exact(out['max_abs_change_01']),max(map(abs,a)))
            close(exact(out['max_abs_change_12']),max(map(abs,b)));checks+=2
            close(exact(out['richardson_quadratic_final']),c[0][-1]/3-2*c[1][-1]+D(8)*c[2][-1]/3);checks+=1
            assert out['richardson_authority']=='CONDITIONAL_POINT_ESTIMATE_ONLY'
        boxes={}
        def value(h):return D.from_float(struct.unpack('>d',bytes.fromhex(h))[0])
        for label in ('T0','T1','T2'):
            endpoints={}
            for g in ('BI','FLRW'):
                lines=(root/'receipts'/(label+'_'+g+'-checkpoint.dat')).read_text().splitlines()
                lo,hi=map(value,lines[3].split()[:2]);endpoints[g]=(lo,hi)
            boxes[label]=(endpoints['BI'][0]-endpoints['FLRW'][1],endpoints['BI'][1]-endpoints['FLRW'][0])
            for i in range(2):close(exact(r['independent_endpoint_xHII_contrasts'][label][i]),boxes[label][i]);checks+=1
        delta=(boxes['T2'][0]-boxes['T1'][1],boxes['T2'][1]-boxes['T1'][0])
        bound=max(map(abs,delta));budget=boxes['T2'][0]/10
        close(exact(r['delta2_bound']),bound);checks+=1
        close(exact(r['conditional_tail']['target_absolute_error']),budget);checks+=1
        close(exact(r['conditional_tail']['q_strict_upper_for_target']),budget/(budget+bound));checks+=1
        close(exact(r['conditional_tail']['q_strict_upper_for_sign']),boxes['T2'][0]/(boxes['T2'][0]+bound));checks+=1
    helper=json.loads((HERE/'helper_coefficients.json').read_text())
    z,A=s.symbols('z A');nodes=[s.Rational(1),s.Rational(1,2),s.Rational(1,4)]
    w=list(map(s.Rational,helper['richardson_weights']));p=sum(s.Rational(c)*z**i for i,c in enumerate(helper['invisible_shift_coefficients']))
    assert all(s.simplify(sum(w[i]*nodes[i]**k for i in range(3))-(1 if k==0 else 0))==0 for k in range(3))
    assert p.subs(z,0)==1 and all(p.subs(z,n)==0 for n in nodes)
    # Adding A*P retains arbitrary samples; the limit moves by arbitrary A.
    c0,c1,c2=s.symbols('c0 c1 c2');f=c0+c1*z+c2*z*z
    assert all(s.expand((f+A*p-f).subs(z,n))==0 for n in nodes)
    assert s.expand((f+A*p-f).subs(z,0))==A
    # Independent tail sum and strict target inequality, for exact rational q.
    for q in (s.Rational(0),s.Rational(1,3),s.Rational(1,2),s.Rational(3,4)):
        assert s.summation(q**s.Symbol('j',integer=True,positive=True),(s.Symbol('j',integer=True,positive=True),1,s.oo))==q/(1-q)
    checks+=15
    spec=importlib.util.spec_from_file_location('candidate_analyzer',HERE/'analyze_contrast.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    negatives=0
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'bad.csv.gz'
        for content in ('time_s,x_HII,temperature_K,photon_n,photon_u_ev_per_h\n1,NaN,1,1,1\n',
                        'time_s,x_HII,temperature_K,photon_n,photon_u_ev_per_h\n1,1,1,1,1\n1,1,1,1,1\n',
                        'time_s,x_HII,temperature_K,photon_n,photon_u_ev_per_h\n1,1,1,1,1\n'):
            with gzip.open(p,'wt') as f:f.write(content)
            try:m.rows(p)
            except ValueError:negatives+=1
            else:raise AssertionError('bad input accepted')
        p=Path(d)/'bad-checkpoint.dat';lines=(root/'receipts/T2_BI-checkpoint.dat').read_text().splitlines();h=lines[0].split();h[1]='4';lines[0]=' '.join(h);p.write_text('\n'.join(lines))
        try:m.checkpoint(p,'T2')
        except ValueError:negatives+=1
        else:raise AssertionError('mismatched grid accepted')
        bad=json.loads(json.dumps(helper));bad['richardson_weights']=['4','-6','3']
        try:m.analyze(root,bad)
        except ValueError:negatives+=1
        else:raise AssertionError('failed local coefficients accepted')
    return {'status':'SCOPED_DIAGNOSTIC_VALIDATION_PASS','decimal_and_symbolic_checks':checks,'negative_fixtures':negatives,
        'compared_common_grid_points_per_observable':8000,'engines':['Decimal90','SymPy '+s.__version__],
        'result_sha256':hashlib.sha256(result.read_bytes()).hexdigest(),'scientific_admission':'HOLD','continuum_certificate':'NOT_ESTABLISHED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,default=HERE.parents[2]);p.add_argument('--result',type=Path,default=HERE/'RESULTS.json');p.add_argument('--out',type=Path);a=p.parse_args();v=validate(a.repo_root,a.result)
    if a.out:a.out.write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps(v))
