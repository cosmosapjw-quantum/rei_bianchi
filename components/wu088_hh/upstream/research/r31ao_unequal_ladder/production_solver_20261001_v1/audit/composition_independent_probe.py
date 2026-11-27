"""Independent rational PSD norm-containment oracle; synthetic data only."""
import sys, random, json, hashlib
from pathlib import Path
from fractions import Fraction as F
ROOT = Path('/workspace/scratch/6cf5f59cd2d1/recovery/repo/research/r31ao_unequal_ladder')
sys.path.insert(0,str(ROOT/'production_solver_20261001_v1/composition'))
import adapter
rng = random.Random(8127)
def mat(n,m):
    return [[(F(rng.randrange(-8,9),16), F(rng.randrange(-8,9),16)) for j in range(m)] for i in range(n)]
def enc(a): return [[[str(x),str(y)] for x,y in row] for row in a]
def sub(a,b): return [[(x[0]-y[0],x[1]-y[1]) for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def adj(a): return [[(a[i][j][0],-a[i][j][1]) for i in range(len(a))] for j in range(len(a[0]))]
def kval(c,r): return [[(x/2,y/2) for x,y in row] for row in sub(c,adj(r))]
def gram_values(a):
    if len(a[0])!=2: a=adj(a)
    aa=dd=br=bi=F(0)
    for (x,y),(z,w) in a:
        aa+=x*x+y*y; dd+=z*z+w*w; br+=x*z+y*w; bi+=x*w-y*z
    return aa,dd,br*br+bi*bi

def check_norm(a,interval):
    # Upper endpoint >= operator norm iff u^2 I - A†A is positive semidefinite.
    # Lower bound follows from max diagonal or sign of characteristic polynomial.
    aa,dd,b2=gram_values(a); l,u=F(interval['lo']),F(interval['hi']); ll,uu=l*l,u*u
    assert 0<=l<=u
    assert uu>=aa and uu>=dd and (uu-aa)*(uu-dd)>=b2
    assert ll<=max(aa,dd) or (ll-aa)*(ll-dd)<=b2

raw={'D_col':mat(47,2),'D_row':mat(2,47)}
centers={'D_col':mat(47,2),'D_row':mat(2,47)}
models={name:{'D_col':mat(47,2),'D_row':mat(2,47),'K':mat(47,2)} for name in adapter.MODELS}
radius=F(1,16)
disks={key:[[{'center':[str(x),str(y)],'radius':str(radius)} for x,y in row] for row in a] for key,a in centers.items()}
req={'schema':'WU088_T5_COMPOSITION_REQUEST_V1','precision':96,'inputs':{
    'raw':adapter.bind({k:enc(v) for k,v in raw.items()}),
    'models':adapter.bind({name:{k:enc(v) for k,v in model.items()} for name,model in models.items()}),
    'target_disks':adapter.bind(disks)}}
result=adapter.compose(req)
raw['K']=kval(raw['D_col'],raw['D_row'])
checks=0
for name,model in models.items():
    for key,a in model.items():
        check_norm(sub(a,raw[key]),result['represented_model_errors'][name][key]); checks+=1
for sample in range(4):
    target={}
    for key,a in centers.items():
        target[key]=[[(x+rng.choice([-1,1])*3*radius/5,y+rng.choice([-1,1])*4*radius/5) for x,y in row] for row in a]
    target['K']=kval(target['D_col'],target['D_row'])
    for key,a in raw.items():
        check_norm(sub(a,target[key]),result['source_residuals'][key]['interval']); checks+=1
    for name,model in models.items():
        for key,a in model.items():
            check_norm(sub(a,target[key]),result['target_model_errors'][name][key]); checks+=1
out={'scope':'SYNTHETIC_COMPONENT_REVIEW_ONLY','oracle':'Exact rational 2x2 Hermitian PSD/principal-minor inequalities; no shared radical algorithm',
     'exact_norm_containment_checks':checks,'dense_complex_matrices':True,'samples_on_entry_disk_boundaries':4,'seed':8127,
     'adapter_sha256':hashlib.sha256((ROOT/'production_solver_20261001_v1/composition/adapter.py').read_bytes()).hexdigest(),
     'gram_sha256':hashlib.sha256((ROOT/adapter.GRAM_RELATIVE).read_bytes()).hexdigest(),
     'scientific_decision_admission':False,'actual_HH_computations':0,'status':'PASS'}
print(json.dumps(out,indent=2))
