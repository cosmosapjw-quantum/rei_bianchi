#!/usr/bin/env python3
"""BR05 independent Decimal90 panel composition audit, with actual BR04 nodes.

This bounded audit reuses the exported original Rust node lists. It does not run
native dynamics or regenerate/alter a rule. Panel boundaries are replayed from
the published recurrence; the W1 reference uses quantile integration, independent
of Rust's positive CDF-plateau integration. Exact source/input bytes are hashed.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

D = Decimal
Z = D(0)
O = D(1)
CUT = D(1800)
PRECISION = 90

def exact64(s):
    return D.from_float(float(s))

def exn(v):
    return Z if v > CUT else (-v).exp()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Reference:
    def __init__(self, tau):
        self.tau = tau
        self.den = O - exn(tau)
        self.phi = O if tau == 0 else self.den / tau

    def cdf(self, x):
        return x if self.tau == 0 else (O-exn(self.tau*x))/self.den

    def qint(self, p):
        if self.tau == 0:
            return p*p/2
        v = O-self.den*p
        term = Z if v == 0 else v*v.ln()
        return (term+self.den*p)/(self.tau*self.den)

    def area(self, p0, p1, x):
        split = min(p1,max(p0,self.cdf(x)))
        return (x*(split-p0) - (self.qint(split)-self.qint(p0))
                + self.qint(p1)-self.qint(split)-x*(p1-split))

def cert(tau,nodes):
    ref=Reference(tau)
    nodes=sorted((x,w) for x,w in nodes if w>0)
    assert nodes and all(0<=x<=1 and w>0 for x,w in nodes)
    logs=[w.ln()-tau*x for x,w in nodes]
    shift=max(logs)
    ws=[exn(shift-v) for v in logs]
    total=sum(ws,Z)
    probs=[w/total for w in ws]
    logmass=shift+total.ln()
    mass=exn(-logmass) if logmass<=0 else logmass.exp()
    p0=Z
    w1=Z
    ks=Z
    mean=Z
    second=Z
    positive=[(x,p) for (x,_),p in zip(nodes,probs) if p>0]
    for ix,(x,p) in enumerate(positive):
        p1=O if ix==len(positive)-1 else min(O,p0+p)
        ks=max(ks,abs(ref.cdf(x)-p0),abs(ref.cdf(x)-p1))
        area=ref.area(p0,p1,x)
        assert area>=-D("1e-70"),("area roundoff",tau,x,area)
        w1+=max(Z,area)
        mean+=p*x
        second+=p*x*x
        p0=p1
    return {"mass":mass,"exact_mass":ref.phi,"w1":w1,"ks":ks,
            "mean":mean,"second":second,"logmass":logmass,
            "normalized_tail_cut_count":len(nodes)-len(positive)}

def boundaries(tau,r):
    left=0.0
    out=[]
    while left<1.0:
        target=1.0/r if tau<=1.0 else min(1.0,1.0/tau+left)/r
        right=min(1.0,left+target)
        assert right>left
        out.append((left,right,right-left))
        left=right
    return out

def atomic_w1(nodes_a,nodes_b):
    sa=sum((w for _,w in nodes_a),Z)
    sb=sum((w for _,w in nodes_b),Z)
    assert sa>0 and sb>0
    a={}
    b={}
    for x,w in nodes_a:a[x]=a.get(x,Z)+w/sa
    for x,w in nodes_b:b[x]=b.get(x,Z)+w/sb
    points=sorted(set(a)|set(b))
    ca=cb=total=Z
    for left,right in zip(points,points[1:]):
        ca+=a.get(left,Z); cb+=b.get(left,Z)
        total+=abs(ca-cb)*(right-left)
    return total

def write_csv(path,rows):
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def run(nodes_path,outdir):
    input_hash=sha(nodes_path)
    rows=list(csv.DictReader(nodes_path.open(newline="")))
    groups={}
    for row in rows:
        if row["family"]=="AP" and int(row["nsteps"])==1:
            groups.setdefault((row["tau"],int(row["resolution"])),[]).append(row)
    assert len(groups)==30,len(groups)
    panels_out=[]
    summary=[]
    failures=[]
    with localcontext() as ctx:
        ctx.prec=PRECISION
        for (tau_s,r),nodes_rows in groups.items():
            tau=exact64(tau_s)
            nodes_rows.sort(key=lambda v:int(v["node"]))
            nodes=[(exact64(v["age"]),exact64(v["emitted_weight"])) for v in nodes_rows]
            bs=boundaries(float(tau_s),r)
            assert len(nodes)==2*len(bs)
            global_cert=cert(tau,nodes)
            exacttotal=global_cert["exact_mass"]
            parts=[]
            for p,(lf,rf,df) in enumerate(bs):
                left,right=exact64(lf),exact64(rf)
                width=right-left
                theta=tau*width
                pair=nodes[2*p:2*p+2]
                local=[((x-left)/width,w/width) for x,w in pair]
                assert all(0<x<1 for x,w in local)
                assert local[0][0]<local[1][0] and pair[0][1]==pair[1][1]
                c=cert(theta,local)
                em=cert(Z,local)
                exactmass=exn(tau*left)*width*c["exact_mass"]
                discrete=exn(tau*left)*width*c["mass"]
                f=local[0][0]
                symmetric_w1=f*f+(D(".5")-f)**2
                symmetry=local[1][0]-(1-f)
                # A one-atom shift from the symmetric rule proves this bound.
                assert abs(em["w1"]-symmetric_w1)<=abs(symmetry)/2+D("1e-68")
                assert abs((em["second"]-D(1)/3)-(f*f-f+D(1)/6))<=abs(symmetry)+D("1e-68")
                width_excess=max(Z,width-O/r)
                optical_excess=max(Z,theta-(1+tau*left)/r)
                assert width_excess<=D("3e-16")
                assert optical_excess<=D("3e-15")*max(O,theta)
                relmass=c["mass"]/c["exact_mass"]-1
                out={"tau":tau_s,"refinement":r,"panel":p,"left":str(left),
                     "right":str(right),"width":str(width),"theta":str(theta),
                     "node0":str(pair[0][0]),"node1":str(pair[1][0]),
                     "weight_each":str(pair[0][1]),
                     "exact_survival_mass":str(exactmass),
                     "discrete_survival_mass":str(discrete),
                     "relative_local_survival_mass_defect":str(relmass),
                     "local_frozen_w1":str(c["w1"]),"local_frozen_cdfsup":str(c["ks"]),
                     "local_emitted_w1":str(em["w1"]),
                     "symmetric_emitted_w1":str(symmetric_w1),
                     "represented_node_symmetry_defect":str(symmetry),
                     "width_bound_roundoff_excess":str(width_excess),
                     "optical_width_bound_roundoff_excess":str(optical_excess),
                     "normalized_tail_cut_count":c["normalized_tail_cut_count"]}
                panels_out.append(out)
                parts.append((exactmass,discrete,width,c,relmass))
            discrete_total=sum((v[1] for v in parts),Z)
            assert discrete_total>0
            exact_partition_total=sum((v[0] for v in parts),Z)
            assert abs(exact_partition_total-exacttotal)<D("1e-65")
            assert abs(discrete_total-global_cert["mass"])<D("1e-65")
            pqs=[(em/exacttotal,dm/discrete_total,h,c,rel) for em,dm,h,c,rel in parts]
            tv=sum((abs(p-q) for p,q,_,_,_ in pqs),Z)/2
            matched_w1=sum((p*h*c["w1"] for p,q,h,c,rel in pqs),Z)
            min_bound=sum((min(p,q)*h*c["w1"] for p,q,h,c,rel in pqs),Z)+tv
            cdf_bound=max((p*c["ks"] for p,q,h,c,rel in pqs),default=Z)+tv
            width_bound=sum((p*h for p,q,h,c,rel in pqs),Z)
            assert global_cert["w1"]<=min_bound+D("1e-65")
            assert abs(global_cert["w1"]-matched_w1)<=tv+D("1e-65")
            assert global_cert["ks"]<=cdf_bound+D("1e-65")
            assert matched_w1<=width_bound+D("1e-65")
            assert width_bound<=O/r+D("3e-16")
            rel_total=global_cert["mass"]/exacttotal-1
            assert abs(rel_total)<D("3e-14")
            mat=[abs(rel) for p,q,h,c,rel in pqs if p>D("1e-20")]
            summary.append({"tau":tau_s,"refinement":r,"panels":len(bs),"nodes":len(nodes),
                "whole_relative_survival_mass_defect":str(rel_total),
                "global_w1":str(global_cert["w1"]),"global_cdfsup":str(global_cert["ks"]),
                "panel_matched_w1":str(matched_w1),"panel_mass_TV":str(tv),
                "minmass_plus_TV_w1_bound":str(min_bound),
                "panel_cdf_plus_TV_bound":str(cdf_bound),
                "mass_weighted_width_bound":str(width_bound),
                "largest_any_panel_relative_mass_defect":str(max(abs(v[-1]) for v in pqs)),
                "largest_material_panel_relative_mass_defect":str(max(mat,default=Z)),
                "material_panel_probability_cutoff":"1e-20",
                "pass":True})
        epsilon=D("1e-12")
        unequal=atomic_w1([(D(".005"),D(".9")),(D(".995"),D(".1"))],
                          [(D(".005"),D(".1")),(D(".995"),D(".9"))])
        assert unequal==D(".792")
        clock=atomic_w1([(D(".5"),O)],[(D(".5")+epsilon,O)])
        assert clock==epsilon
        examples={
            "unequal_panel_mass":{"panel_width_each":"0.01","mass_weighted_width":"0.01",
              "panel_probabilities_P":["0.9","0.1"],"panel_probabilities_Q":["0.1","0.9"],
              "age_atoms":["0.005","0.995"],"actual_W1":str(unequal),"TV":"0.8",
              "conclusion":"A retained weighted width alone is not a bound without matching panel masses."},
            "clock_shift":{"delta":str(epsilon),"same_weight_W1":str(clock),"CDFsup":"1",
              "conclusion":"A small atom-clock shift controls W1 but not atomic CDFsup."},
            "label_swap":{"label_L_ages":["0","1"],"label_R_ages":["1","0"],
              "unlabelled_mixture_W1":"0","equal_weight_label_constrained_W1":"1",
              "conclusion":"The age-only mixture loses label discrepancies."}}
    assert sha(nodes_path)==input_hash
    outdir.mkdir(parents=True,exist_ok=True)
    write_csv(outdir/"PANEL_REFERENCE_DECIMAL90.csv",panels_out)
    write_csv(outdir/"PANEL_COMPOSITION_DECIMAL90.csv",summary)
    receipt={"schema":"BR05_PANEL_MATH_DECIMAL90_V1","status":"PASS",
      "created_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,
      "script_sha256":sha(Path(__file__)),"input":{"path":str(nodes_path.resolve()),"sha256":input_hash},
      "precision_decimal_digits":PRECISION,"rules":len(groups),"panels":len(panels_out),
      "actual_nodes":sum(int(v["nodes"]) for v in summary),
      "scope":"Actual prior BR04 Rust scalar node lists only. New independent panel/clock/composition audit; no native dynamics rerun.",
      "tail_policy":"Decimal exp tails below exp(-1800) are cut. For the declared <=1e12 optical-depth domain and bounded positive rule weights, conservative omitted normalized mass <1e-768.",
      "checks":["all actual paired nodes interior and positive","both width bounds with separately reported binary64 excess",
       "global/partition masses agree in Decimal90","actual emitted W1 agrees with symmetric closed formula up to measured node-symmetry coupling bound",
       "emitted second defect formula has measured rounding bound","matched panel W1 vs actual global W1 differs by at most panel-mass TV",
       "unequal mass W1 bound","panel CDFplusTV bound","normalized mass-weighted width bound",
       "whole fitted survivor mass defect below 3e-14","three explicit finite counterexamples/limitations"],
      "largest_whole_relative_mass_defect":str(max(abs(D(v["whole_relative_survival_mass_defect"])) for v in summary)),
      "largest_panel_mass_TV":str(max(D(v["panel_mass_TV"]) for v in summary)),
      "examples":examples,"failures":failures}
    (outdir/"PANEL_MATH_VERIFICATION.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({k:receipt[k] for k in ["status","rules","panels","actual_nodes","largest_whole_relative_mass_defect","largest_panel_mass_TV"]}))
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--nodes",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    run(args.nodes,args.out_dir)

