"""Exact inequality oracle for upward quantization; synthetic values only."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,hashlib,json,random,sys
path=Path('/workspace/scratch/6cf5f59cd2d1/recovery/repo/research/r31ao_unequal_ladder/production_solver_20261001_v1/endpoint_tasks/planner.py')
spec=importlib.util.spec_from_file_location('review_endpoint_quantizer',path)
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
rng=random.Random(590016)
checks=0
for bits in (16,31,64,128,512):
    relative=Q(1,1<<(bits-1))
    factors=[Q(rng.randrange(1,100000),rng.randrange(1,100000)) for _ in range(24)]
    factors += [Q(1), Q((1<<bits)-1,1<<bits), Q((1<<bits)+1,1<<bits), Q(1,3)]
    for exponent in (-10000,-1074,-200,-1,0,1,200,1024,10000):
        scale=Q(2)**exponent
        for factor in factors:
            q=factor*scale; upper=p.upward_dyadic(q,bits)
            assert q <= upper < q*(1+relative)
            assert upper.denominator & (upper.denominator-1)==0
            assert p.upward_dyadic(upper,bits)==upper
            checks+=1
assert p.upward_dyadic(Q(0),128)==0
refusals=0
for value,bits in ((-1,128),(True,128),(0.5,128),(Q(1),15),(Q(1),513),(Q(1<<65536),128),(Q(1,1<<65536),128)):
    try:p.upward_dyadic(value,bits)
    except (p.EndpointError,p.LimitReached):refusals+=1
    else:raise AssertionError('invalid input accepted')
# Demonstrate that rounding tiny positives does not impose an absolute floor.
a=p.upward_dyadic(Q(1,3)*Q(2)**-10000,128)
b=p.upward_dyadic(Q(1,3),128)*Q(2)**-10000
assert a==b and a>0
out={'status':'PASS','scope':'SYNTHETIC_EXACT_INEQUALITY_ORACLE','planner_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
     'positive_inequality_and_idempotence_cases':checks,'refusal_cases':refusals,'zero_exact':True,
     'tiny_positive_no_absolute_floor':True,'native_or_actual_HH_runs':0,
     'inequality':'q <= U < q * (1 + 2^(1-bits)) for q > 0','seed':590016}
print(json.dumps(out,indent=2))
