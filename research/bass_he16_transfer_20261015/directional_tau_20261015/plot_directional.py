"""Generate a dependency-light white-background SVG and sky CSV from provenance caches.

All x,y coordinates in plotted panels are derived from saved source outputs.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import sys
from xml.etree import ElementTree

import numpy as np

from directional_tau import read_caches, read_geometry, tau_between_source_and_observer

def plot(base_cache, geo_cache, actual, frozen, analytic, output_dir):
    data, man, elapsed=read_caches(base_cache)
    b=read_geometry(geo_cache,base_cache,man)
    output_dir.mkdir(parents=True,exist_ok=True)
    obs={}
    mus=np.linspace(-1,1,201)
    for case in ("SHEAR_MINUS","ZERO","SHEAR_PLUS"):
        tau,info=tau_between_source_and_observer(data[case],b[case],.5,mus)
        obs[case]=np.asarray(tau,dtype=float)
    with (output_dir/"DIRECTIONAL_SKY_zrel_0p5.csv").open("w",newline="") as f:
        writer=csv.writer(f,lineterminator="\n")
        writer.writerow(["mu_observer","tau_MINUS","tau_ZERO","tau_PLUS",
                         "delta_tau_MINUS_minus_ZERO","delta_tau_PLUS_minus_ZERO"])
        for i,m in enumerate(mus):
            writer.writerow([format(float(m),".17g"),*[format(obs[c][i],".17g")
                  for c in ("SHEAR_MINUS","ZERO","SHEAR_PLUS")],
                format(obs["SHEAR_MINUS"][i]-obs["ZERO"][i],".17g"),
                format(obs["SHEAR_PLUS"][i]-obs["ZERO"][i],".17g")])
    full=actual["signed_summary"]
    frozen_z=frozen["directional"]
    pred=analytic["cases"]
    rels=[x["z_rel"] for x in full]
    shape={"width":1050,"height":825}
    result=[
      '<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="825" viewBox="0 0 1050 825">',
      '<rect width="1050" height="825" fill="white"/>',
      '<text x="52" y="38" font-size="19" font-family="sans-serif" font-weight="600" fill="#181818">Directional Thomson depth in cold LRS Bianchi I</text>',
      '<text x="52" y="60" font-size="12" font-family="sans-serif" fill="#595959">Observer at mean z̄≈10.2693; relative directional z is NOT the present-day CMB redshift</text>',
      '<text x="52" y="85" font-size="14" font-weight="600" font-family="sans-serif">A. Sky contrast at z_rel=0.5 (signed q vs ZERO), in units of 10⁻⁵</text>',
    ]
    left,right,top,bottom=92,995,109,352
    def pt(x,y,xlo,xhi,ylo,yhi,l,r,t,bot):
        return l+(x-xlo)/(xhi-xlo)*(r-l),bot-(y-ylo)/(yhi-ylo)*(bot-t)
    def axes(l,r,t,bot,xmin,xmax,ymin,ymax,xticks,yticks, xlabel):
        items=[f'<path d="M{l},{t} V{bot} H{r}" fill="none" stroke="#555" stroke-width="1"/>']
        for xt in xticks:
            p=l+(xt-xmin)/(xmax-xmin)*(r-l)
            items += [f'<line x1="{p:.2f}" y1="{t}" x2="{p:.2f}" y2="{bot}" stroke="#ededed"/>',
                      f'<text x="{p:.2f}" y="{bot+18}" font-size="11" fill="#555" text-anchor="middle" font-family="sans-serif">{xt:g}</text>']
        for yt in yticks:
            p=bot-(yt-ymin)/(ymax-ymin)*(bot-t)
            items += [f'<line x1="{l}" y1="{p:.2f}" x2="{r}" y2="{p:.2f}" stroke="#ededed"/>',
                      f'<text x="{l-8}" y="{p+4:.2f}" font-size="10" text-anchor="end" fill="#555" font-family="sans-serif">{yt:g}</text>']
        items.append(f'<text x="{(l+r)/2:.2f}" y="{bot+36}" text-anchor="middle" font-size="12" font-family="sans-serif">{xlabel}</text>')
        return items
    neg=(obs["SHEAR_MINUS"]-obs["ZERO"])*1e5
    pos=(obs["SHEAR_PLUS"]-obs["ZERO"])*1e5
    ybound=max(np.max(abs(neg)),np.max(abs(pos)))*1.13
    result+=axes(left,right,top,bottom,-1,1,-ybound,ybound,[-1,-.5,0,.5,1],[-1,-.5,0,.5,1],
                 "Observer-local direction cosine μ_o")
    for vals,col,label in ((neg,"#b35238","q=−0.01"),(pos,"#286c95","q=+0.01")):
        points=" ".join(f"{pt(float(x),float(y),-1,1,-ybound,ybound,left,right,top,bottom)[0]:.2f},{pt(float(x),float(y),-1,1,-ybound,ybound,left,right,top,bottom)[1]:.2f}" for x,y in zip(mus,vals))
        result.append(f'<polyline points="{points}" fill="none" stroke="{col}" stroke-width="2.1"/>')
        idx=0 if label.startswith("q=−") else 1
        x=772+idx*114
        result.append(f'<line x1="{x}" y1="91" x2="{x+20}" y2="91" stroke="{col}" stroke-width="3"/>')
        result.append(f'<text x="{x+23}" y="95" font-size="11" fill="#333" font-family="sans-serif">{label}</text>')
    result += [
      '<text x="52" y="421" font-size="14" font-weight="600" font-family="sans-serif">B. Odd Legendre quadrupole a₂ [10⁻⁵]</text>',
      '<text x="557" y="421" font-size="14" font-weight="600" font-family="sans-serif">C. Frozen geometry matching of |odd a₂| [%]</text>'
    ]
    # Lower-left panel: odd a2.
    l1,r1,t1,b1=92,503,445,714
    l2,r2,t2,b2=607,997,445,714
    result+=axes(l1,r1,t1,b1,.2,.75,-1.35,0,[.2,.3,.4,.5,.6,.75],[-1.2,-.9,-.6,-.3,0],"Relative directional z")
    xcoord=lambda x:l1+(x-.2)/(.75-.2)*(r1-l1)
    ycoord=lambda y:b1-(y+1.35)/1.35*(b1-t1)
    for q,key,color in ((.005,"005","#286c95"),(.01,"010","#b35238")):
        vals=[float(x["odd_tau_a2_q"+key])*1e5 for x in full]
        pts=" ".join(f"{xcoord(z):.2f},{ycoord(v):.2f}" for z,v in zip(rels,vals))
        result.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.1" points="{pts}"/>')
        preds=[float(pred[str(z)]["signed"][str(q)]["odd_tau_a2_predicted_linear"])*1e5 for z in rels]
        for z,val in zip(rels,preds):
            result.append(f'<circle cx="{xcoord(z):.2f}" cy="{ycoord(val):.2f}" r="3.5" fill="white" stroke="{color}" stroke-width="1.7"/>')
    result.append('<text x="101" y="742" font-size="10.5" fill="#555">Solid: full numerical odd a₂; circles: independent linear prediction</text>')
    # Lower-right: relative frozen-zero-gas geometry agreement
    result+=axes(l2,r2,t2,b2,.2,.75,99.98,100.005,[.2,.3,.4,.5,.6,.75],[99.98,99.985,99.99,99.995,100.0],"Relative directional z")
    def yy(v):return b2-(v-99.98)/.025*(b2-t2)
    def xx(v):return l2+(v-.2)/.55*(r2-l2)
    for q,key,color in ((.005,"005","#286c95"),(.01,"010","#b35238")):
        vals=[]
        for f,r in zip(frozen_z,full):
            fullq=float(r["odd_tau_a2_q"+key])
            frozenq=float(next(x for x in f["geometry_only"] if x["q"]==q)["geometry_only_odd_tau_a2"])
            vals.append(100*(1-abs(fullq-frozenq)/abs(fullq)))
        pts=" ".join(f"{xx(z):.2f},{yy(v):.2f}" for z,v in zip(rels,vals))
        result.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.1" points="{pts}"/>')
        for z,val in zip(rels,vals):
            result.append(f'<circle cx="{xx(z):.2f}" cy="{yy(val):.2f}" r="3" fill="{color}"/>')
    result.append('<text x="611" y="742" font-size="10.5" fill="#555">ZERO gas/clock fixed; only signed b(a) substituted</text>')
    result.append('<text x="53" y="787" font-size="11" fill="#595959" font-family="sans-serif">Original five signed prefixes; source-scoped numerical reconstruction, NOT independently ODE-certified or CMB polarization.</text>')
    result.append('</svg>')
    svg=output_dir/"DIRECTIONAL_TAU_RESULTS.svg"
    svg.write_text("\n".join(result)+"\n")
    ElementTree.parse(svg)
    return svg


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base-cache",type=Path,required=True)
    p.add_argument("--geometry-cache",type=Path,required=True)
    p.add_argument("--full",type=Path,required=True)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--analytic",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    print(plot(args.base_cache,args.geometry_cache,
               json.loads(args.full.read_text()),
               json.loads(args.frozen.read_text()),
               json.loads(args.analytic.read_text()),args.output_dir))
