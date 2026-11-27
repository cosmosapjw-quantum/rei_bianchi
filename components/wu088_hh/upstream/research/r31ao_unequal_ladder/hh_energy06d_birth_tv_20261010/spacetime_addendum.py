#!/usr/bin/env python3
"""Read-only post-seal addendum: joint spacetime-vs-angular birth total variation."""
import json, pathlib, sys
from fractions import Fraction as Q
if len(sys.argv)!=2: raise SystemExit('usage: python script.py /path/to/extracted/HH_ENERGY06D_20261010_v1')
r=pathlib.Path(sys.argv[1]);lines=(r/'inputs/OWNER_PREBE_FINAL_BINARY.jsonl').read_text().splitlines()
rows=[json.loads(s) for s in lines if s.strip()]
out=[]
for member in range(4):
    a=next(x for x in rows if x['member']==member and x['label']=='full_preBE')
    b=next(x for x in rows if x['member']==member and x['label']=='half1_preBE')
    w1=list(map(Q.from_float,b['source_weights']));w2=list(map(Q.from_float,a['source_weights']))
    p1=[v/sum(w1,Q(0)) for v in w1];p2=[v/sum(w2,Q(0)) for v in w2]
    H=Q.from_float(b['source_n']);W=Q.from_float(a['source_n']);assert W==2*H
    t1=Q.from_float(b['endpoint_time']);t2=Q.from_float(a['endpoint_time']);assert t1<t2
    # Signed spacetime difference: t1 positive and t2 negative, both mass H.
    joint=(sum([abs(H*v) for v in p1],Q(0))+sum([abs(-H*v) for v in p2],Q(0)))/2
    assert joint==H and joint/W==Q(1,2)
    ang=H/2*sum((abs(x-y) for x,y in zip(p1,p2)),Q(0))
    p2_kernel=[(3*(Q(-1)+2*(Q(i//16)+Q(1,2))/8)**2-1)/2 for i in range(128)]
    kernels={
        'constant':([Q(1)]*128,[Q(1)]*128),
        'centered_birth_time':([t1-t2]*128,[Q(0)]*128),
        'grid_P2':(p2_kernel,p2_kernel),
    }
    checks={}
    for name,(k1,k2) in kernels.items():
        diff=(H*sum([u*k for u,k in zip(p1,k1)],Q(0))+H*sum([u*k for u,k in zip(p2,k2)],Q(0)))-W*sum([u*k for u,k in zip(p2,k2)],Q(0))
        timing=H*sum([u*(a-b) for u,a,b in zip(p1,k1,k2)],Q(0))
        angular=H*sum([(u-v)*k for u,v,k in zip(p1,p2,k2)],Q(0))
        assert diff==timing+angular
        bound=H*max((abs(a-b) for a,b in zip(k1,k2)))+(max(k2)-min(k2))*ang
        if abs(diff)>bound:
            print("BOUND_FAIL",member,name,"diff",float(diff),"bound",float(bound),"timing",float(timing),"angular",float(angular),"K-range",float(max(k2)-min(k2)),file=sys.stderr)
        assert abs(diff)<=bound
        checks[name]={'defect_fraction':str(diff),'timing_fraction':str(timing),'angular_fraction':str(angular),'bound_fraction':str(bound),'identity_pass':True}
    out.append({'member':member,'spacetime_TV_normalized':'1/2','joint_TV_photons_per_H_fraction':str(H),'angular_TV_normalized':float(ang/W),'kernels':checks})
print(json.dumps({'scope':'POSTSEAL_AUXILIARY_MATHEMATICAL_FACT_FOR_NORMALIZED_STORED_BIRTH_WEIGHTS','source_changed':False,'science_dispatch':0,'members':out},indent=2,ensure_ascii=False))
