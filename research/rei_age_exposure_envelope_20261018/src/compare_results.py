"""Observable errors and strict source-jump matching, not an accuracy certificate."""
from pathlib import Path
import argparse,json,math
from run_refinement import read_json,save

def relative(a: float,b: float):
    if not math.isfinite(a) or not math.isfinite(b): raise ValueError('NONFINITE_COMPARISON')
    return abs(a-b)/abs(b) if b!=0 else (0. if a==0 else None)

def w1(xa,wa,xb,wb) -> float:
    """Exact discrete normalized W1 = integral |CDFa-CDFb| dt, units of age."""
    def measure(x,w):
        if len(x)!=len(w) or not x: raise ValueError('INVALID_AGE_MEASURE')
        if not all(math.isfinite(v) for v in [*x,*w]) or min(w)<0: raise ValueError('INVALID_AGE_MEASURE')
        total=math.fsum(w)
        if total<=0: raise ValueError('ZERO_SURVIVOR_MEASURE')
        d={}
        for a,b in zip(x,w): d[a]=d.get(a,0.)+b/total
        return d
    a=measure(xa,wa);b=measure(xb,wb);knots=sorted(set(a)|set(b))
    accum=0.;pieces=[]
    for lo,hi in zip(knots,knots[1:]):
        accum+=a.get(lo,0.)-b.get(lo,0.)
        pieces.append(abs(accum)*(hi-lo))
    return math.fsum(pieces)

def match_observations(left: list,right: list,clock_atol: float=2e-15):
    if not math.isfinite(clock_atol) or clock_atol<0: raise ValueError('INVALID_CLOCK_TOLERANCE')
    matches=[];missing=[]
    for b in right:
        a=[x for x in left if x['side']==b['side'] and abs(x['x']-b['x'])<=clock_atol]
        if len(a)!=1: missing.append({'x':b['x'],'side':b['side'],'candidates':len(a)})
        else: matches.append((a[0],b))
    return matches,missing

def validate_endpoint(e: dict) -> None:
    """Check the native observable contract before species-wise zipping.

    An absent channel is missing data, not a zero event or agreement.
    Future structural-zero cohorts are allowed; occupied unborn cohorts are not.
    """
    def vector(key, exact=None, minimum=None):
        v=e.get(key)
        if (not isinstance(v,list) or (exact is not None and len(v)!=exact)
                or (minimum is not None and len(v)<minimum)):
            raise ValueError('ENDPOINT_SHAPE_'+key)
        if not all(isinstance(x,(float,int)) and math.isfinite(x) for x in v):
            raise ValueError('NONFINITE_ENDPOINT_'+key)
        return v
    for key in ('proper_time_s','N','U','temperature_K','quadrupole_U_mu2_minus_third'):
        v=e.get(key)
        if not isinstance(v,(int,float)) or not math.isfinite(v):
            raise ValueError('NONFINITE_ENDPOINT_'+key)
    if min(e['N'],e['U'],e['temperature_K'])<0:
        raise ValueError('NEGATIVE_PHYSICAL_ENDPOINT')
    vector('Gamma_s',exact=3);vector('heat_erg_per_absorber_s',exact=3)
    vector('ledgers',exact=14);vector('flat',minimum=4)
    birth=vector('birth_times_s')
    cohorts=e.get('cohorts')
    if not isinstance(cohorts,list) or len(cohorts)!=len(birth):
        raise ValueError('ENDPOINT_SHAPE_cohorts')
    for t,v in zip(birth,cohorts):
        if not isinstance(v,list) or len(v)<2:
            raise ValueError('ENDPOINT_SHAPE_cohort_moments')
        if not all(isinstance(x,(float,int)) and math.isfinite(x) and x>=0 for x in v[:2]):
            raise ValueError('INVALID_COHORT_MOMENTS')
        if t>e['proper_time_s'] and (v[0]>0 or v[1]>0):
            raise ValueError('OCCUPIED_COHORT_BEFORE_BIRTH')

def endpoint_metrics(a: dict,b: dict) -> dict:
    if not math.isclose(a['proper_time_s'],b['proper_time_s'],rel_tol=2e-14,abs_tol=0.):
        raise ValueError('PHYSICAL_CLOCK_MISMATCH')
    validate_endpoint(a);validate_endpoint(b)
    out={k:relative(a[k],b[k]) for k in ('N','U','temperature_K')}
    for k in ('Gamma_s','heat_erg_per_absorber_s'):
        out[k]=[relative(x,y) for x,y in zip(a[k],b[k])]
    for name,i,j in [('photo_events',4,7),('RR_events',7,10),('CI_events',10,13),('DR_events',13,14)]:
        out[name]=[relative(x,y) for x,y in zip(a['ledgers'][i:j],b['ledgers'][i:j])]
    out['fraction_abs']=[abs(x-y) for x,y in zip(a['flat'][:3],b['flat'][:3])]
    out['thermal_abs_eV_H']=abs(a['flat'][3]-b['flat'][3])
    for k in ('N','U'):out[k+'_abs']=abs(a[k]-b[k])
    dp=abs(a['quadrupole_U_mu2_minus_third']-b['quadrupole_U_mu2_minus_third'])
    out['quadrupole_difference_over_U']=dp/b['U'] if b['U']>0 else (0. if dp==0 else None)
    if a['N']>0 and b['N']>0:
        ages_a=[a['proper_time_s']-t for t in a['birth_times_s']]
        ages_b=[b['proper_time_s']-t for t in b['birth_times_s']]
        out['age_W1_s']=w1(ages_a,[c[0] for c in a['cohorts']],ages_b,[c[0] for c in b['cohorts']])
    else:out['age_W1_s']=None
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('left',type=Path);p.add_argument('right',type=Path)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--target',type=float,default=.005)
    a=p.parse_args()
    if not math.isfinite(a.target) or a.target<0: p.error('finite nonnegative accuracy target required')
    left=read_json(a.left/'endpoint.json');right=read_json(a.right/'endpoint.json')
    # A frozen reference setup may keep birth times outside the endpoint object.
    for root,obj in ((a.left,left),(a.right,right)):
        if 'birth_times_s' not in obj and (root/'setup.json').exists():obj['birth_times_s']=read_json(root/'setup.json')['birth_times_s']
    metrics=endpoint_metrics(left,right)
    matches,missing=match_observations(read_json(a.left/'observations.json'),read_json(a.right/'observations.json'))
    trajectory=[]
    for x,y in matches:
        r=endpoint_metrics(x['physical'],y['physical']) if 'birth_times_s' in x['physical'] and 'birth_times_s' in y['physical'] else {k:relative(x['physical'][k],y['physical'][k]) for k in ('N','U','temperature_K')}
        trajectory.append({'x':y['x'],'side':y['side'],'errors':r})
    selected=[metrics['N'],metrics['U'],*metrics['photo_events'],*metrics['Gamma_s'],*metrics['heat_erg_per_absorber_s'],metrics['temperature_K']]
    result={'schema':'rei.age-refinement.comparison.v1','left':str(a.left),'right':str(a.right),
            'endpoint':metrics,'common_observations':trajectory,'missing_or_ambiguous':missing,
            'finite_neighbor_target':a.target,
            'selected_endpoint_target_met':all(x is not None and x<=a.target for x in selected),
            'observation_coverage':'COMPLETE' if not missing else 'HOLD_MISSING_SIDE_OR_CLOCK',
            'source_equivalence':'MUST_BE_BOUND_BY_INPUT_AND_OWNER_IDENTITIES',
            'admission':'FINITE_DIFFERENCE_ONLY_NO_CONTINUUM_OR_PRODUCTION_ADMISSION'}
    save(a.out,result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
