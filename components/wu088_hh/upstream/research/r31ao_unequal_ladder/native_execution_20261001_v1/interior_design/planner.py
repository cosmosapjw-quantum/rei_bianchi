"""Exact compact-domain/tile diagnosis. No callback, integral or tail evaluation."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
LADDER=HERE.parents[1]
DRIVER_PATH=HERE.parent/'native_driver/driver.py'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;spec.loader.exec_module(obj);return obj


driver=module('_wu088_interior_domain_driver',DRIVER_PATH)


def exact(token):
    if type(token) is not str or len(token)>320:raise ValueError('bounded exact token required')
    q=Q(token)
    if str(q)!=token or max(q.numerator.bit_length(),q.denominator.bit_length())>512:
        raise ValueError('canonical bounded exact token required')
    return q


def geometric_axis(lower,upper,max_intervals=512):
    lower,upper=exact(lower),exact(upper)
    if not 0<lower<upper:raise ValueError('positive ordered axis required')
    if type(max_intervals) is not int or not 1<=max_intervals<=1024:raise ValueError('axis cap')
    if any(q.denominator&(q.denominator-1) for q in (lower,upper)):raise ValueError('dyadic axis required')
    out=[];left=lower
    while left<upper:
        if len(out)==max_intervals:raise ValueError('geometric axis interval cap')
        right=min(2*left,upper);out.append((left,right));left=right
    return out


def inverse_real_lower(a,lo,hi,imaginary_bound):
    a,lo,hi,y=map(Q,(a,lo,hi,imaginary_bound))
    if a<=0 or not 0<lo<=hi or y<0:raise ValueError('positive shifted-domain premises')
    x0,x1=a+lo,a+hi
    # For fixed |y|<=Y, x/(x*x+Y*Y) has an interior maximum only.
    return min(x0/(x0*x0+y*y),x1/(x1*x1+y*y))


def complex_domain(a,b,window):
    lt,Tt,lu,Tu=(exact(window[k]) for k in ('l_t','T_t','l_u','T_u'))
    if not 0<lt<Tt or not 0<lu<Tu:raise ValueError('positive ordered window')
    pt=min(lt/4,(Tt-lt)/4);pu=min(lu/4,(Tu-lu)/4)
    sigma=(inverse_real_lower(a,lt-pt,Tt+pt,pt)+inverse_real_lower(b,lu-pu,Tu+pu,pu))/2
    margin=driver.real_domain_margin(Q(a),Q(b),window)
    return {'t_complex_rectangle':[str(lt-pt),str(Tt+pt),str(-pt),str(pt)],
        'u_complex_rectangle':[str(lu-pu),str(Tu+pu),str(-pu),str(pu)],
        'sigma_real_lower_on_padded_product':str(sigma),'worker_margin':str(margin),
        'proved_domain_margin_sufficient_for_this_product':margin<min(lt-pt,lu-pu,sigma),
        'computed_Arb_balls_still_must_pass_callback_guards':True}


def window(a,b):return {'l_t':a,'T_t':b,'l_u':a,'T_u':b}


PILOTS=(('CENTRAL',window('1','2')),
        ('TINY_CENTRAL',window('1','257/256')))


def describe(source_plan,index=0):
    if type(index) is not int or not 0<=index<2592:raise ValueError('primitive index')
    task=source_plan['tasks'][index];a,b=(exact(task['parameters'][k]) for k in ('a','b'))
    w=source_plan['window'];xt=geometric_axis(w['l_t'],w['T_t']);xu=geometric_axis(w['l_u'],w['T_u'])
    if len(xt)*len(xu)>262144:raise ValueError('tile product cap')
    for axis,lo,hi in ((xt,w['l_t'],w['T_t']),(xu,w['l_u'],w['T_u'])):
        assert axis[0][0]==Q(lo) and axis[-1][1]==Q(hi)
        assert all(axis[k][1]==axis[k+1][0] for k in range(len(axis)-1))
    old_margin=min(Q(1),Q(w['l_t']),Q(w['l_u']))/(1<<20)
    sigma_corner=(1/(a+Q(w['T_t']))+1/(b+Q(w['T_u'])))/2
    limits=dict(driver.DEFAULT_LIMITS)
    pilots=[]
    for name,pw in PILOTS:
        if any(Q(pw[l])<Q(w[l]) or Q(pw[t])>Q(w[t]) for l,t in (('l_t','T_t'),('l_u','T_u'))):continue
        pilots.append({'name':name,'window':pw,'limits':limits,'domain':complex_domain(a,b,pw),
            'purpose':'actual compact subdomain diagnostic only; no full-window completion',
            'dispatch':'CENTRAL first; TINY_CENTRAL after observed broad-box/width refusal; no endpoint evaluation for these diagnostic boxes'})
    return {'schema':'WU088_EXACT_INTERIOR_DOMAIN_PLAN_V1','source_plan_sha256':source_plan['plan_sha256'],
        'source_task_sha256':task['task_sha256'],'input_record_sha256':source_plan['input_record_sha256'],
        'archive_sha256':source_plan['archive_sha256'],'index':index,'parameters':task['parameters'],
        'window':w,'old_worker_margin':str(old_margin),'real_sigma_at_upper_corner':str(sigma_corner),
        'old_margin_rejects_real_upper_corner':old_margin>=sigma_corner,
        'new_domain':complex_domain(a,b,w),
        'tile_grid':{'representation':'Cartesian product of listed contiguous exact axes; interiors disjoint',
            't_axis':[[str(l),str(r)] for l,r in xt],'u_axis':[[str(l),str(r)] for l,r in xu],
            'tile_count':len(xt)*len(xu),'execute_full_grid':False,
            'assembly_rule':'Sum all accepted tile rectangles outward once; add the original global endpoint disk once after complete coverage.'},
        'pilots':pilots,'driver_source_identity':driver.source_identity(),
        'native_executions':0,'source_callback_evaluations':0,'endpoint_evaluations':0,
        'scientific_admission':False,'full_domain_integral':False}


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--endpoint-plan',required=True);cli.add_argument('--npz',required=True)
    cli.add_argument('--output-dir',required=True);cli.add_argument('--task-index',type=int,default=0)
    args=cli.parse_args();out=Path(args.output_dir).resolve()
    if out.exists():raise ValueError('create-only design directory')
    driver.verify_sources();p=module('_wu088_interior_design_endpoint',driver.PLAN_MODULE)
    archive=p.archive_bytes(args.npz);source=p.read_json(args.endpoint_plan)
    p.validate_plan(source,source_archive_bytes=archive)
    record=describe(source,args.task_index)
    out.mkdir(parents=True,exist_ok=False)
    for pilot in record['pilots']:
        plan=p.build_plan(source['input_record'],pilot['window'],precision_bits=source['precision_bits'],
            panels=source['panels'],caps=source['caps'],source_archive_bytes=archive)
        # This is a native worker window/identity plan. No endpoint result is made.
        p.write_new(out/(pilot['name']+'_PLAN.json'),plan)
        p.write_new(out/(pilot['name']+'_LIMITS.json'),pilot['limits'])
        pilot['native_window_plan_sha256']=plan['plan_sha256']
    p.write_new(out/'DOMAIN_AND_TILE_PLAN.json',record)
    print(json.dumps({'status':'EXACT_DOMAIN_PLAN_ONLY','tile_count':record['tile_grid']['tile_count'],
        'old_margin_rejects_real_upper_corner':record['old_margin_rejects_real_upper_corner'],
        'pilots':[x['name'] for x in record['pilots']],'native_executions':0}))


if __name__=='__main__':main()
