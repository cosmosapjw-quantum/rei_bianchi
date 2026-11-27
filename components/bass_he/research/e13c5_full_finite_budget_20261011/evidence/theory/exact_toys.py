#!/usr/bin/env python3
"""Exact Fraction theory controls; no coefficient, ODE, native or NCP imports."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import platform
import resource
import time

HERE=Path(__file__).resolve().parent

def iv(a,b=None):
    lo,hi=F(a),F(a if b is None else b)
    assert lo<=hi
    return lo,hi
def plus(a,b):return a[0]+b[0],a[1]+b[1]
def minus(a,b):return a[0]-b[1],a[1]-b[0]
def width(a):return a[1]-a[0]
def contains(a,x):return a[0]<=x<=a[1]
def scale(a,w):
    w=F(w)
    assert w>0
    return w*a[0],w*a[1]
def intersect(a,b):
    lo,hi=max(a[0],b[0]),min(a[1],b[1])
    return None if lo>hi else (lo,hi)
def sign(a):
    lo,hi=a
    if lo>0:return "STRICTLY_POSITIVE"
    if hi<0:return "STRICTLY_NEGATIVE"
    if lo==hi==0:return "EXACT_ZERO"
    if lo==0:return "NONNEGATIVE_NOT_STRICT"
    if hi==0:return "NONPOSITIVE_NOT_STRICT"
    return "UNDETERMINED"
def enc(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,(tuple,list)):return [enc(v) for v in x]
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    return x

def main():
    start=time.monotonic();tests=[]
    def check(name,ok,**evidence):
        tests.append({"id":name,"status":"PASS" if ok else "FAIL","evidence":enc(evidence)})
        assert ok,name
    selected,remainder=iv(1,3),iv(10,14)
    full=plus(selected,remainder);new=iv(2,F(5,2))
    naive_remainder=minus(full,selected);direct=plus(new,remainder)
    naive=plus(naive_remainder,new)
    check("DIRECT_COMPLEMENT",remainder==iv(10,14),full=full,remainder=remainder)
    check("DEPENDENCY_WIDTH",width(naive_remainder)==width(remainder)+2*width(selected),naive=naive_remainder)
    check("DIRECT_REPLACEMENT",direct==iv(12,F(33,2)),direct=direct)
    check("SUBTRACTIVE_REPLACEMENT_INFLATES",naive==iv(10,F(37,2)) and width(naive)==width(direct)+2*width(selected),naive=naive)
    wider=iv(0,4);bad=(full[0]-wider[0],full[1]-wider[1])
    check("ENDPOINT_SUBTRACTION_REQUIRES_CANONICAL_EQUALITY",not contains(bad,F(10)) and not contains(bad,F(14)),bad=bad,valid_remainder=remainder)
    gain=width(selected)-width(new);floor=width(remainder)
    check("GAIN_IDENTITY",width(direct)==width(full)-gain,gain=gain)
    check("GAIN_CEILING_AND_FLOOR",0<=gain<=width(selected) and width(direct)>=floor and width(full)/width(direct)<=width(full)/floor,floor=floor,ratio_ceiling=width(full)/floor)
    a,b=iv(1,3),iv(2,4);same=intersect(a,b);target=F(5,2)
    check("SAME_TARGET_INTERSECTION",same==iv(2,3) and contains(a,target) and contains(b,target) and contains(same,target),intersection=same)
    a,b=iv(1,2),iv(F(9,5),F(11,5));mix=intersect(a,b)
    check("OVERLAP_DIFFERENT_TARGET_NOT_ADMISSION",contains(a,F(3,2)) and contains(b,F(2)) and not contains(mix,F(3,2)),overlap=mix,target_a=F(3,2),target_b=F(2))
    check("DISJOINT_IS_DETECTABLE",intersect(iv(0,1),iv(2,3)) is None)
    arbitrary=F(300);sel=F(0);missing=arbitrary;total=(sel+missing)/2
    check("SELECTED_ZERO_DOES_NOT_BOUND_COMPLEMENT",sel==0 and total==150,arbitrary_K=arbitrary,full_correction=total)
    check("ABSOLUTE_POSITIVITY_DOES_NOT_FIX_CORRECTION_SIGN",F(3)>0 and F(3)-F(4)<0,absolute=F(3),captured=F(4),correction=F(-1))
    signs=[(iv(1,2),"STRICTLY_POSITIVE"),(iv(-2,-1),"STRICTLY_NEGATIVE"),(iv(0),"EXACT_ZERO"),(iv(0,1),"NONNEGATIVE_NOT_STRICT"),(iv(-1,0),"NONPOSITIVE_NOT_STRICT"),(iv(-1,1),"UNDETERMINED")]
    for case,(box,expected) in enumerate(signs):check("SIGN_CLASS_"+str(case),sign(box)==expected,interval=box,classification=sign(box))
    coefficients=[F(0),F(0),F(1),F(-2),F(1)]
    evaluate=lambda x:sum(c*x**k for k,c in enumerate(coefficients))
    integral=sum(c/F(k+1) for k,c in enumerate(coefficients))
    quadrature=(evaluate(F(0))+evaluate(F(1)))/2
    check("CONTINUUM_ALIASING",quadrature==0 and integral==F(1,30),finite_sum=quadrature,continuum_per_A=integral)
    midpoint_error=F(1,3)-F(1,4);bound=F(2)/24
    check("CONDITIONAL_MIDPOINT_REMAINDER",midpoint_error==bound==F(1,12),error=midpoint_error,bound=bound)
    true,cseg,cnode,cnative=F(14,10),F(1),F(11,10),F(12,10)
    delta=true-cseg;rseg=cseg-cnode;rnode=cnode-cnative
    check("NATIVE_BASELINE_TELESCOPE",delta+rseg+rnode==true-cnative==F(1,5),continuous_minus_segments=delta,segments_minus_nodes=rseg,nodes_minus_aggregate=rnode)
    weights=(F(2),F(3));intervals=(iv(1,3),iv(5,7))
    weighted=plus(scale(intervals[0],weights[0]),scale(intervals[1],weights[1]))
    check("POSITIVE_WEIGHT_WIDTH_ADDITIVITY",width(weighted)==sum(w*width(v) for w,v in zip(weights,intervals)),weighted_sum=weighted)
    off=F(2)*F(2)+F(3)*F(5);kf=F(2)*F(11)+F(3)*F(17)
    check("MODE_MIXING_CHANGES_TARGET",off==19 and kf==73 and off+kf not in (off,kf),off=off,kf=kf,mixed=off+kf)
    species_sum=plus(iv(0,1),iv(0,1));total_direct=iv(1);joint=intersect(species_sum,total_direct)
    check("FLOOR_IS_ROUTE_CONDITIONAL",width(species_sum)==2 and joint==iv(1) and width(joint)==0,species_sum=species_sum,direct_total=total_direct)
    raw=(F(1),F(10));weighted_width=(F(100)*raw[0],F(1)*raw[1])
    check("WEIGHTED_RANK_CAN_REVERSE_RAW_RANK",raw[0]<raw[1] and weighted_width[0]>weighted_width[1],raw=raw,weighted=weighted_width)
    result={"schema":"bass-he-e13c5b-exact-theory-toys-v1","status":"PASS_THEORY_TOYS_ONLY","checks":len(tests),"failures":0,"tests":tests,"execution":{"scope":"exact Fraction identities and counterexamples","actual_coefficient_evaluations":0,"actual_ODE_runs":0,"actual_native_runs":0,"actual_NCP_scientific_runs":0,"wall_seconds":time.monotonic()-start,"max_rss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"python":platform.python_version()},"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    destination=HERE/"EXACT_TOY_RESULTS.json"
    with destination.open("x") as stream:
        json.dump(enc(result),stream,ensure_ascii=False,indent=2);stream.write("\n")
    print(json.dumps({"status":result["status"],"checks":len(tests),"wall_seconds":result["execution"]["wall_seconds"],"result":str(destination)},ensure_ascii=False))
if __name__=="__main__":main()

